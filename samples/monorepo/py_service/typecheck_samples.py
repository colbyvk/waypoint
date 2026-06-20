"""Type-checker correctness fixtures. mypy --warn-unreachable / --strict-equality
/ --warn-no-return should flag the PLANT lines; the OK function stays clean.
These are bugs a type-checker can PROVE and a pattern matcher cannot."""


def unreachable_demo(x: int) -> int:
    return x
    # WAYPOINT-PLANT: [unreachable] — dead code after an unconditional return
    print("never runs")


def overlap_demo(s: str) -> bool:
    # WAYPOINT-PLANT: [comparison-overlap] — str == int is always False
    return s == 5


def no_return_demo(x: int) -> int:
    if x > 0:
        return 1
    # WAYPOINT-PLANT: [return] — this path falls through and returns None


def ok_demo(x: int) -> int:
    # WAYPOINT-OK: total function, no dead code, overlapping comparison
    if x > 0:
        return 1
    return 0
