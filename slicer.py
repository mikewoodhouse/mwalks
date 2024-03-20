from copy import copy

from lib.walks import Point, Route


def split_point(seg, split_secs):
    split_pct = split_secs / seg.secs
    lat = seg.from_point.lat + (seg.to_point.lat - seg.from_point.lat) * split_pct
    lon = seg.from_point.lon + (seg.to_point.lon - seg.from_point.lon) * split_pct
    ele = seg.from_point.ele + (seg.to_point.ele - seg.from_point.ele) * split_pct
    p2 = Point(
        None,
        None,
        seg.from_point.secs + split_secs,
        seg.from_point.dtstr,
        lat,
        lon,
        ele,
    )

    return p2


class Slicer:

    def __init__(self, route, num_slices=10) -> None:
        self.route = route
        self.num_slices = num_slices
        self.slices = self.slice()

    def slice(self):
        secs = self.route.filtered_time()
        split_secs = secs / self.num_slices
        s = 0
        splits = []
        split_rt = Route()
        for seg in self.route.moving_segments():
            split_rt.add_point(seg.from_point)
            s += seg.secs
            if s >= split_secs:
                mid_pt = split_point(seg, s - split_secs)
                split_rt.add_point(mid_pt)
                splits.append(split_rt)
                split_rt = Route()
                split_rt.add_point(mid_pt)
                s -= split_secs
        if len(split_rt.segments) > 0:
            splits.append(split_rt)
        return splits
