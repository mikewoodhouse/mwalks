from math import hypot
from typing import NamedTuple

from dateutil import parser
from shapely.geometry import MultiLineString, shape

from lib.haversine import distance


def to_miles(metres):
    return metres * 0.621371 / 1000.0


class Point(NamedTuple):
    point_id: int
    route_id: int
    secs: float
    dtstr: str
    lat: float
    lon: float
    ele: float

    def __repr__(self) -> str:
        return f"({self.lon},{self.lat})|{self.ele}@{self.secs:.2f}"

    @property
    def loc(self):
        return (self.lon, self.lat)

    @property
    def dt(self):
        return parser.parse(self.dtstr)

    def __copy__(self):
        return type(self)(
            self.point_id,
            self.route_id,
            self.secs,
            self.dtstr,
            self.lat,
            self.lon,
            self.ele,
        )


class Segment:
    def __init__(self, from_pt, to_pt) -> None:
        self.from_point = from_pt
        self.to_point = to_pt
        self.level_distance = distance(self.from_point.loc, self.to_point.loc)
        self.delta_ele = self.to_point.ele - self.from_point.ele
        self.distance = hypot(self.level_distance, self.delta_ele)
        self.secs = self.to_point.secs - self.from_point.secs
        self.mps = 0 if self.secs == 0 else self.distance / self.secs

    def __repr__(self):
        return f"{self.from_point}->{self.to_point}"


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

    @property
    def level_distance(self):
        return sum(seg.level_distance for seg in self.segments)

    @property
    def metres(self):
        return sum(seg.distance for seg in self.segments)

    @property
    def miles(self):
        return to_miles(self.metres)

    @property
    def time(self):
        return sum(seg.secs for seg in self.segments)

    @property
    def mph(self):
        hours = self.time / 3600.0
        return self.miles / hours

    @property
    def rise(self):
        return sum(seg.delta_ele for seg in self.segments if seg.delta_ele > 0.0)

    @property
    def fall(self):
        return sum(seg.delta_ele for seg in self.segments if seg.delta_ele < 0.0)

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
    def shape(self) -> MultiLineString:
        coords = [[(pt.lon, pt.lat) for pt in self.points]]
        return shape({"type": "MultiLineString", "coordinates": coords})

    def moving_segments(self):
        def faster_than(seg):
            return seg.mps > FILTER_SPEED_LIMIT

        yield from filter(faster_than, self.segments)

    @property
    def filtered(self):
        rt = Route()
        for s in self.moving_segments():
            rt.segments.append(s)
        return rt

    def __repr__(self) -> str:
        return ", ".join(
            [
                f"{self.miles:.2f} miles ({self.filtered.miles:.2f})",
                f"{self.time / 3600.0:.2f} hrs ({self.filtered.time / 3600.0:.2f})",
                f"{self.mph:.2f} mph ({self.filtered.mph:.2f}) rise/fall {self.rise:.1f}/{self.fall:.1f}m",
            ]
        )
