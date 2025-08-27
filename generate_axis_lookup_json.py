import csv
import json
import math
import re
from collections import defaultdict
import bisect
import numpy as np

# -----------------------------
# Parsing helpers
# -----------------------------

PAIR_RE = re.compile(r"\s*(\d+)\s*/\s*(\d+)\s*")
n = [0.15, 0.30, 0.50, 0.70]

omega = [0.1, 0.5, 1.0]

def parse_cell(cell):

    parts = str(cell).split(":")
    pts = []
    for p in parts:
        m = PAIR_RE.fullmatch(p.strip())
        if not m:
            return None
        b = float(m.group(1))
        a = float(m.group(2))
        pts.append((b, a))

    pts.sort(key=lambda t: t[0])
    return pts


# -----------------------------
# Data container
# -----------------------------
# -----------------------------
# Load your CSV
# -----------------------------
#
# Expected columns (case-sensitive here; rename if needed):
# 'Standard fire resistance' (REI category like 'REI 60')
# 'Mechanical reinforcement ratio ω' (float like 0.100, 0.500, 1.000)
# 'n = 0,15', 'n = 0,3', 'n = 0,5', 'n = 0,7'  (cell strings)


def build_json_from_table(csv_path):
    data = defaultdict(lambda: {"omega": {}})
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        REI = None
        for row in reader:
            if row["Standard fire resistance"]:
                REI = row["Standard fire resistance"].strip()
            if not REI:
                continue

            if row["Mechanical reinforcement ratio"]:
                omega_val = (row.get("Mechanical reinforcement ratio")).strip()
            else:
                print("error: missing omega")
                continue
            try:
                omega_val = str(float(omega_val))  # Use string keys for JSON compatibility
            except ValueError:
                print("error: invalid data for omega:")
                continue

            omega_dict = data[REI]["omega"]
            if omega_val not in omega_dict:
                omega_dict[omega_val] = {"n": {}}

            for n in ["0.15", "0.3", "0.5", "0.7"]:
                cell = row.get(n)
                print(f"Processing REI={REI}, omega={omega_val}, n={n}, cell={cell}")
                pts = parse_cell(cell)
                if pts:
                    dict_pts = [
                        {f"b_{i}": b, f"a_{i}": a} for i, (b, a) in enumerate(pts)
                    ]
                else:
                    dict_pts = "NULL"
                omega_dict[omega_val]["n"][n] = dict_pts
    return data

# Example usage:
csv_path = "axis_distance_lookup.csv"
result = build_json_from_table(csv_path)
with open("axis_lookup.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)
    






