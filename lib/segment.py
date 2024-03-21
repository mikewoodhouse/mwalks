from dataclasses import dataclass, field
from math import hypot

from lib.calcs import haversine_distance

from .point import Point


@dataclass
class Segment:
    from_point: Point
    to_point: Point
    level_distance: float = field(init=False)
    delta_ele: float = field(init=False)
    distance: float = field(init=False)
    secs: float = field(init=False)
    mps: float = field(init=False)

    def __post_init__(self) -> None:
        self.level_distance = haversine_distance(self.from_point.loc, self.to_point.loc)
        self.delta_ele = self.to_point.ele - self.from_point.ele
        self.distance = hypot(self.level_distance, self.delta_ele)
        self.secs = self.to_point.secs - self.from_point.secs
        self.mps = 0 if self.secs == 0 else self.distance / self.secs

    def __repr__(self):
        return (
            f"{self.from_point.point_id}->{self.to_point.point_id}: "
            f"{self.distance}m in {self.secs}s ({self.mps} m/s)"
        )
