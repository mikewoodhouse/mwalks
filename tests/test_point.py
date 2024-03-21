from datetime import datetime

from lib import Point


# 2024-03-20 08:15:51.659000+00:00
def test_times():
    from_pt = Point(dt="2024-03-20 08:15:48.767000+00:00")
    assert isinstance(from_pt.dt, datetime) and from_pt.dt.hour == 8
    to_pt = Point(dt="2024-03-20 08:15:51.659000+00:00")
    assert to_pt.secs > from_pt.secs
