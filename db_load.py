import xml.etree.ElementTree as ET
import dateutil.parser
import sqlite3


class TrackPoint:
    table_name = 'points'
    columns = [
        ('point_id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
        ('route_id', 'INTEGER'),
        ('dt', 'DATE'),
        ('lat', 'REAL'),
        ('lon', 'REAL'),
        ('ele', 'REAL')
    ]

    @classmethod
    @property
    def create_sql(cls):
        col_defs = ', '.join(' '.join(col) for col in cls.columns)
        return f'CREATE TABLE {cls.table_name} ({col_defs})'

    @classmethod
    @property
    def sql_insert_fields(cls):
        return [col[0] for col in cls.columns if 'PRIMARY KEY' not in col[1]]

    @classmethod
    @property
    def insert_sql(cls):
        return f'INSERT INTO points ({",".join(cls.sql_insert_fields)}) VALUES ({", ".join(list("?" * len(cls.sql_insert_fields)))})'

    def __init__(self, pt):
        self.lat = float(pt.attrib['lat'])
        self.lon = float(pt.attrib['lon'])
        self.ele = float(pt.find('{http://www.topografix.com/GPX/1/1}ele').text)
        date_time = pt.find('{http://www.topografix.com/GPX/1/1}time').text
        self.dt = dateutil.parser.parse(date_time)

    @property
    def coord(self):
        return (self.lon, self.lat)

    def sql_values(self, route_id):
        return (route_id, self.dt, self.lat, self.lon, self.ele)

    def __repr__(self):
        return f'{self.date_time}, ({self.lat}, {self.lon}), {self.ele}m'


class Route:
    create_sql = '''
        DROP TABLE IF EXISTS routes;
        CREATE TABLE routes (
            route_id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT
        );'''

    def __init__(self, path):
        self.path = path
        self.route_id = None

    def add_to_db(self, conn):
        sql = 'INSERT INTO routes (path) VALUES (?)'
        csr = conn.cursor()
        csr.execute(sql, (self.path, ))
        self.route_id = csr.lastrowid
        print(f'inserted route for {self.path} as {self.route_id}')
        csr.close()
        conn.commit()

        root = ET.parse(self.path).getroot()
        pts = [TrackPoint(pt) for pt in root.findall('.//{http://www.topografix.com/GPX/1/1}trkpt')]
        insert_values = [pt.sql_values(self.route_id) for pt in pts]

        sql = TrackPoint.insert_sql
        csr = conn.cursor()
        csr.executemany(sql, insert_values)
        csr.close()
        conn.commit()


class TrackPointDbBuilder:
    def __init__(self, db_path='mwalks.sqlite'):
        self.db_path = db_path
        self.conn = None

    def create_db(self):
        self.connect()
        self.conn.executescript(Route.create_sql)
        self.conn.executescript(f'DROP TABLE IF EXISTS {TrackPoint.table_name};{TrackPoint.create_sql}')
        self.disconnect()

    def add_route_file(self, path):
        route = Route(path)
        self.connect()
        route.add_to_db(self.conn)
        self.disconnect()

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)

    def disconnect(self):
        self.conn.close()


def build_db():

    builder = TrackPointDbBuilder()
    builder.create_db()

    from glob import glob

    for path in glob('routes/*.gpx'):
        builder.add_route_file(path)

    conn = sqlite3.connect(builder.db_path)
    print('database now contains:')
    for tname in ['routes', 'points']:
        c = conn.execute(f'SELECT Count(*) FROM {tname}')
        rows = c.fetchone()[0]
        print(f'    {rows} {tname}')
    conn.close()


if __name__ == "__main__":
    build_db()
