from dataclasses import dataclass, field
from datetime import datetime


def decode_datetime_string(s: str) -> datetime:
    dt = datetime.fromisoformat(s)
    print(f"decoded {s} -> {dt}")
    return dt


@dataclass
class Point:
    point_id: int = 0
    route_id: int = 0
    dt: datetime | str = ""
    lat: float = 0
    lon: float = 0
    ele: float = 0

    def __post_init__(self) -> None:
        if isinstance(self.dt, str):
            self.dt = datetime.fromisoformat(self.dt)


@dataclass
class Route:
    route_id: int = 0
    path: str = ""
    points: list[Point] = field(default_factory=list)
