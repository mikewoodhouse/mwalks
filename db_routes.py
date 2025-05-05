import sqlite3
from collections import defaultdict

from lib.walks import Point, Route


def load_routes_from_db(from_id: int = -1, to_id: int = 9999):
    conn = sqlite3.connect("mwalks.sqlite")

    db_points = conn.execute(
        """
        SELECT
            point_id
        ,   route_id
        ,   Cast(strftime('%H', dt) AS INTEGER) * 3600
        + Cast(strftime('%M', dt) AS INTEGER) * 60
        + Cast(strftime('%f', dt) AS REAL) AS secs
        ,   datetime(dt) AS dt
        ,   lat
        ,   lon
        ,   ele
        FROM points
        WHERE route_id BETWEEN :from_id AND :to_id
        ORDER BY route_id, point_id
    """,
        {"from_id": from_id, "to_id": to_id},
    ).fetchall()

    conn.close()

    routes = defaultdict(Route)
    points = [Point(*p) for p in db_points]
    for pt in points:
        routes[pt.route_id].add_point(pt)

    return routes
