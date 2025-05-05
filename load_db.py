import sqlite3
import xml.etree.ElementTree as ET
import re
import dateutil.parser
from pathlib import Path
from db_routes import load_routes_from_db
from summarise import summarise
from lib.route_collections import collection_for


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


class RouteFile:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.date_time_str = self.to_date_time_str(
            re.search(r"\d{14}", self.path.name)[0]
        )

    @staticmethod
    def to_date_time_str(s: str) -> str:
        return f"{s[:4]}-{s[4:6]}-{s[6:8]} {s[8:10]}:{s[10:12]}:{s[13:]}"


class RouteLoader:
    create_sql = """
        DROP TABLE IF EXISTS routes;
        CREATE TABLE routes (
            route_id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT,
            date_time TEXT,
            collection TEXT
        );"""

    def __init__(self, route_file: RouteFile):
        self.route_file = route_file
        self.path = route_file.path
        self.route_id = None

    @staticmethod
    def set_collection(conn: sqlite3.Connection, route_id: int) -> None:
        sql = "UPDATE routes SET collection = :collection WHERE route_id = :route_id"
        csr = conn.cursor()
        csr.execute(sql, {"route_id": route_id, "collection": collection_for(route_id)})
        csr.close()
        conn.commit()

    def add_to_db(self, conn: sqlite3.Connection) -> None:
        sql = "INSERT INTO routes (path, date_time) VALUES (?, ?)"
        csr = conn.cursor()
        csr.execute(sql, (self.path.name, self.route_file.date_time_str))
        self.route_id = csr.lastrowid
        csr.close()
        conn.commit()

        self.set_collection(conn, self.route_id)

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

    def add_route_file(self, file: RouteFile):
        route = RouteLoader(file)
        route.add_to_db(self.conn)


def build_db():
    builder = TrackPointDbBuilder()
    builder.create_db()

    files = [RouteFile(path) for path in Path("routes").glob("*.gpx")]
    files.sort(key=lambda f: f.date_time_str)
    for file in files:
        builder.add_route_file(file)

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
    summarise(routes)
