from dataclasses import dataclass, field

from .point import Point
from .segment import Segment


@dataclass
class Route:
    route_id: int = 0
    path: str = ""
    points: list[Point] = field(default_factory=list)
    _segments: list[Segment] = field(default_factory=list)

    @property
    def segments(self) -> list[Segment]:
        if not self._segments:
            self._segments = [
                Segment(from_point=f, to_point=t)
                for f, t in zip(self.points[:-1], self.points[1:])
            ]
        return self._segments

    @property
    def distance(self) -> int:
        return int(sum(seg.distance for seg in self.segments))
