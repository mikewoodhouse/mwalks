from dateutil import parser
from datetime import date, datetime
from math import hypot
from shapely.geometry import shape
from typing import NamedTuple

from haversine import distance


class Point(NamedTuple):
    point_id: int
    route_id: int
    secs: float
    dtstr: str
    lat: float
    lon: float
    ele: float

    def __repr__(self) -> str:
        return f'({self.lon},{self.lat})|{self.ele}@{self.secs:.2f}'

    @property
    def loc(self):
        return (self.lon, self.lat)

    @property
    def dt(self):
        return parser.parse(self.dtstr)

class Segment:
    def __init__(self, from_pt, to_pt) -> None:
        self.from_point = from_pt
        self.to_point = to_pt
        self.level_distance = distance(self.from_point.loc, self.to_point.loc)
        self.delta_ele = self.to_point.ele - self.from_point.ele
        self.distance = hypot(self.level_distance, self.delta_ele)
        self.secs = self.to_point.secs - self.from_point.secs
        self.mps = self.distance / self.secs


FILTER_SPEED_LIMIT = 0.5


class Route:

    def __init__(self):
        self.points = []
        self.segments = []
        self.prev_pt = None
        self.walk_date = None

    def add_point(self, pt):
        self.points.append(pt)
        if self.prev_pt:
            self.segments.append(Segment(self.prev_pt, pt))
        else:
            self.walk_date = pt.dt.date()
        self.prev_pt = pt

    def level_distance(self):
        return sum(seg.level_distance for seg in self.segments)

    def metres(self):
        return sum(seg.distance for seg in self.segments)

    def miles(self):
        return self.metres() * 0.621371 / 1000.0

    def filtered_time(self):
        return sum(seg.secs for seg in self.segments if seg.mps > FILTER_SPEED_LIMIT)

    def filtered_miles(self):
        return sum(seg.distance for seg in self.segments if seg.mps > FILTER_SPEED_LIMIT) * 0.621371 / 1000.0

    def time(self):
        return sum(seg.secs for seg in self.segments)

    def avg_mph(self):
        hours = self.time() / 3600.0
        return self.miles() / hours

    def point_at(self, target_elapsed):
        start_time = self.points[0].secs
        target_secs = start_time + target_elapsed
        idx = 1
        while self.points[idx].secs < target_secs:
            idx += 1
            if idx >= len(self.points):
                return None
        return self.points[idx]

    @property
    def bounds(self):
        return (
            min(pt.lon for pt in self.points),
            min(pt.lat for pt in self.points),
            max(pt.lon for pt in self.points),
            max(pt.lat for pt in self.points),
        )

    @property
    def shape(self):
        coords = [[(pt.lon, pt.lat) for pt in self.points]]
        return shape({'type': 'MultiLineString', 'coordinates': coords})

    def __repr__(self) -> str:
        filtered_mph = self.filtered_miles() * 3600.0 / self.filtered_time()
        return(f'{self.miles():.2f} miles ({self.filtered_miles():.2f}), {self.time() / 3600.0:.2f} hrs ({self.filtered_time() / 3600.0:.2f}), {self.avg_mph():.2f} mph ({filtered_mph:.2f})')
