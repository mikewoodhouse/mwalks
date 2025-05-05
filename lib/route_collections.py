ID_COLLECTION_MAP = {
    "sidcup": "0-35, 48, 51, 56, 114, 149-150, 155",
    "costa": "36-47, 49-50, 52-55, 57-89, 91, 94-99, 139-148, 151-154, 156",
    "green_chain": "90, 92-93",
    "the_city": "100-113, 115-125, 127, 129, 131, 136-138",
    "regents_canal": "126, 128, 130, 132-135",
    "capital_ring": "157-163",
}


def is_in_list(n: int, ids: str) -> bool:
    inc = [s.strip() for s in ids.split(",")]
    for chunk in inc:
        if "-" in chunk:
            lo, hi = chunk.split("-")
        else:
            lo = hi = chunk
        if int(lo) <= n <= int(hi):
            return True
    return False


def collection_for(route_id: int) -> str:
    return next(k for k, v in ID_COLLECTION_MAP.items() if is_in_list(route_id, v))
