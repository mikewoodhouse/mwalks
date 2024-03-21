from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Point:
    point_id: int = 0
    route_id: int = 0
    dt: datetime | str = ""
    lat: float = 0
    lon: float = 0
    ele: float = 0
    secs: float = field(init=False)

    def __post_init__(self) -> None:
        if isinstance(self.dt, str):
            self.dt = datetime.fromisoformat(self.dt)
        self.secs = (
            self.dt.hour * 3600.0
            + self.dt.minute * 60
            + self.dt.second
            + self.dt.microsecond / 1_000_000.0
        )

    @property
    def loc(self):
        return (self.lon, self.lat)
