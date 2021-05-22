from collections import defaultdict
from db_routes import load_routes_from_db

routes = load_routes_from_db()

rt = routes[80]

segs = rt.segments

print(len(segs))

d_over_t = [round(seg.distance / seg.secs, 1) for seg in segs]

from collections import Counter

counter = Counter(d_over_t)

# for k in sorted(counter.keys()):
#     print(f'{k}: {counter[k]}')

print(rt.time())
print(rt.filtered_time())


class Count:
    def __init__(self):
        self.walks = 0
        self.miles = 0.0
        self.hrs = 0.0
        self.filtered_hrs = 0.0
        self.filtered_miles = 0.0

    def add(self, rt):
        self.walks += 1
        self.miles += rt.miles()
        self.hrs += rt.time() / 3600
        self.filtered_hrs += rt.filtered_time() / 3600
        self.filtered_miles += rt.filtered_miles()

    def __repr__(self):
        avg_mph = self.miles / self.hrs
        filtered_avg_mph = self.filtered_miles / self.filtered_hrs
        return(f'{self.walks} walks, {self.miles:.2f} miles ({self.filtered_miles:.2f}), {self.hrs:.2f} hrs ({self.filtered_hrs:.2f}), {avg_mph:.2f} mph ({filtered_avg_mph:.2f})')


def summarise():

    tots = defaultdict(Count)

    for k, r in routes.items():
        yy = r.walk_date.year
        mm = r.walk_date.month
        tots[(yy, mm)].add(r)

    for k, t in tots.items():
        print(k, t)


if __name__ == "__main__":
    summarise()