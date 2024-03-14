from datetime import datetime
from pathlib import Path

from icecream import ic


def extract_datetime(path: Path) -> datetime:
    s = path.stem[-14:]
    yy=int(s[:4])
    mm=int(s[4:6])
    dd=int(s[6:8])
    hh=int(s[8:10])
    mi=int(s[10:12])
    ss=int(s[12:])
    return datetime(yy,mm,dd,hh,mi,ss)


for dt in sorted(extract_datetime(path) for path in Path("routes").glob("*.gpx")):
    ic(dt)