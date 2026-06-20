"""Logic-smell fixtures — WAYPOINT-PLANT should fire, WAYPOINT-OK must not."""


def selfcmp(a, b):
    # WAYPOINT-PLANT: waypoint-py-logic-self-comparison
    if a == a:
        return 1
    # WAYPOINT-OK: distinct operands
    if a == b:
        return 2
    return 0


def identity(x):
    # WAYPOINT-PLANT: waypoint-py-logic-is-literal
    if x is 5:
        return 1
    # WAYPOINT-OK: identity against None is the correct idiom
    if x is None:
        return 2
    return 0


def fin():
    try:
        return risky()
    finally:
        # WAYPOINT-PLANT: waypoint-py-logic-return-in-finally
        return 0


def fin_ok():
    try:
        return risky()
    finally:
        # WAYPOINT-OK: finally does cleanup, no control flow
        cleanup()


def constant(x):
    # WAYPOINT-PLANT: waypoint-py-logic-constant-condition
    if True:
        return 1
    # WAYPOINT-OK: a real, variable condition
    if x:
        return 2
    return 0


def nonecmp(x):
    # WAYPOINT-PLANT: waypoint-py-logic-eq-none
    if x == None:
        return 1
    # WAYPOINT-OK: proper identity check
    if x is not None:
        return 2
    return 0


def risky():
    return 1


def cleanup():
    pass
