"""Loop fixtures — WAYPOINT-PLANT should fire, WAYPOINT-OK must not."""
import time


def server():
    # WAYPOINT-PLANT: waypoint-py-infinite-loop
    while True:
        time.sleep(1)


def poll():
    # WAYPOINT-PLANT: waypoint-py-infinite-loop
    while 1:
        pass


def bounded(items):
    # WAYPOINT-OK: bounded iteration over a finite collection
    for it in items:
        print(it)


def countdown(n):
    # WAYPOINT-OK: loop bounded by a real condition
    while n > 0:
        n -= 1
