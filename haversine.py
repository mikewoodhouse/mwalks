import math


def distance(p1, p2):
    lat1, lon1 = p1
    lat2, lon2 = p2
    R = 6_371_000  # metres
    φ1 = lat1 * math.pi / 180  # φ, λ in radians
    φ2 = lat2 * math.pi / 180
    Δφ = (lat2 - lat1) * math.pi / 180
    Δλ = (lon2 - lon1) * math.pi / 180

    a = math.sin(Δφ / 2) * math.sin(Δφ / 2) + math.cos(φ1) * math.cos(φ2) * math.sin(Δλ / 2) * math.sin(Δλ / 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    d = R * c  # in metres
    return round(d, 3)
