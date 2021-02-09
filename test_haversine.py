from haversine import distance


def dms_to_decimal(d, m, s):
    return d + m / 60.0 + s / 3600.0


def test_dms_to_decimal():
    assert 51.47778 == round(dms_to_decimal(51, 28, 40), 5)


def test_haversine():
    assert distance((0.113592, 51.415508), (0.113483, 51.415523)) == 7.741
