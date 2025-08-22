import csv
import math
import re
from collections import defaultdict
import bisect
import numpy as np

Fire_period = ["REI30", "REI60", "REI90", "RE120", "REI180", "REI240"]
mechanical_reinforcement_ratio = [0.1, 0.5, 1.0]
load_level = [0.15, 0.3, 0.5, 0.7]

nested_lookup = {}

def expand_range(item, order_list):
    """Expand 'X:Y' into all values between them (inclusive)."""
    if not item or item.strip().upper() == "NULL":
        return []
    if ":" not in item:
        return [item.strip()]
    start, end = [x.strip() for x in item.split(":")]
    s, e = order_list.index(start), order_list.index(end)
    return order_list[s:e+1]

with open("axis_distance_lookup.csv", newline="") as f:
    reader = csv.reader(f)
    for row in reader:
