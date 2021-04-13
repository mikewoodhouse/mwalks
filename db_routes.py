from collections import defaultdict
import sqlite3

from walks import Route, Point


def load_routes_from_db():
    conn = sqlite3.connect('mwalks.sqlite')

    db_points = conn.execute("""
        SELECT
            point_id
        ,   route_id
        ,   Cast(strftime('%H', dt) AS INTEGER) * 3600
        + Cast(strftime('%M', dt) AS INTEGER) * 60
        + Cast(strftime('%f', dt) AS REAL) AS secs
        ,   lat
        ,   lon
        ,   ele
        FROM points ORDER BY route_id, point_id
    """).fetchall()
    print(len(db_points))

    route_bounds = conn.execute('SELECT Min(lon), Min(lat), Max(lon), Max(lat) FROM points').fetchone()
    print(route_bounds)

    conn.close()

    routes = defaultdict(Route)
    points = [Point(*p) for p in db_points]
    for pt in points:
        routes[pt.route_id].add_point(pt)

    return routes
