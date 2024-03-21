import sqlite3
import xml.etree.ElementTree as ET

import dateutil.parser

from db_routes import load_routes_from_db
from summarise import summarise


class TrackPoint:
    table_name = "points"
    columns = [
        ("point_id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
        ("route_id", "INTEGER"),
        ("dt", "DATE"),
        ("lat", "REAL"),
        ("lon", "REAL"),
        ("ele", "REAL"),
    ]

    @classmethod
    def create_sql(cls):
        col_defs = ", ".join(" ".join(col) for col in cls.columns)
        return f"""
        DROP TABLE IF EXISTS {cls.table_name};
        CREATE TABLE {cls.table_name} ({col_defs});"""

    @classmethod
    def sql_insert_fields(cls):
        return [col[0] for col in cls.columns if "PRIMARY KEY" not in col[1]]

    @classmethod
    def insert_sql(cls) -> str:
        return f"""
        INSERT INTO points ({",".join(cls.sql_insert_fields())})
        VALUES ({", ".join(list("?" * len(cls.sql_insert_fields())))})
        """

    def __init__(self, pt):
        self.lat = float(pt.attrib["lat"])
        self.lon = float(pt.attrib["lon"])
        self.ele = float(pt.find("{http://www.topografix.com/GPX/1/1}ele").text)
        date_time = pt.find("{http://www.topografix.com/GPX/1/1}time").text
        self.dt = dateutil.parser.parse(date_time)

    @property
    def coord(self):
        return (self.lon, self.lat)

    def sql_values(self, route_id):
        return (route_id, self.dt, self.lat, self.lon, self.ele)

    def __repr__(self):
        return f"{self.dt}, ({self.lat}, {self.lon}), {self.ele}m"


class RouteLoader:
    create_sql = """
        DROP TABLE IF EXISTS routes;
        CREATE TABLE routes (
            route_id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT
        );"""

    def __init__(self, path):
        self.path = path
        self.route_id = None

    def add_to_db(self, conn: sqlite3.Connection) -> None:
        sql = "INSERT INTO routes (path) VALUES (?)"
        csr = conn.cursor()
        csr.execute(sql, (self.path,))
        self.route_id = csr.lastrowid
        csr.close()
        conn.commit()

        root = ET.parse(self.path).getroot()
        pts = [
            TrackPoint(pt)
            for pt in root.findall(".//{http://www.topografix.com/GPX/1/1}trkpt")
        ]
        insert_values = [pt.sql_values(self.route_id) for pt in pts]

        sql = TrackPoint.insert_sql()
        csr = conn.cursor()
        csr.executemany(sql, insert_values)
        csr.close()
        conn.commit()
        print(f"added route for {self.path} as {self.route_id}")


class TrackPointDbBuilder:
    def __init__(self, db_path="mwalks.sqlite"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)

    def create_db(self):
        self.conn.executescript(RouteLoader.create_sql)
        self.conn.executescript(TrackPoint.create_sql())

    def add_route_file(self, path):
        route = RouteLoader(path)
        route.add_to_db(self.conn)


def build_db():

    builder = TrackPointDbBuilder()
    builder.create_db()

    from glob import glob

    for path in glob("routes/*.gpx"):
        builder.add_route_file(path)

    conn = sqlite3.connect(builder.db_path)
    print("database now contains:")
    for tname in ["routes", "points"]:
        c = conn.execute(f"SELECT Count(*) FROM {tname}")
        rows = c.fetchone()[0]
        print(f"    {rows} {tname}")
    conn.close()


if __name__ == "__main__":
    build_db()
    routes = load_routes_from_db()
    for route in routes.items():
        print(route)
    summarise(routes)
