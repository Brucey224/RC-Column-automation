import csv
import math
import re
from collections import defaultdict
import bisect
import numpy as np

# -----------------------------
# Parsing helpers
# -----------------------------

PAIR_RE = re.compile(r"\s*(\d+)\s*/\s*(\d+)\s*")

def parse_cell(cell):
    """
    Parse a cell string like '150/30:200/25' into a sorted list of (b_min, a).
    Returns [] if the cell is NULL/empty.
    """
    if not cell or str(cell).strip().upper() == "NULL":
        return []

    parts = str(cell).split(":")
    pts = []
    for p in parts:
        m = PAIR_RE.fullmatch(p.strip())
        if not m:
            # If you want to be strict, raise here. We'll be permissive and skip.
            continue
        b = float(m.group(1))
        a = float(m.group(2))
        pts.append((b, a))

    pts.sort(key=lambda t: t[0])
    return pts


def piecewise_a_from_b(b, points):
    """
    Given a list of sorted (b_min, a) breakpoints, return a(b) by piecewise linear interpolation.
    If list is empty -> return None.
    If list has 1 point -> treat as constant a (flat segment).
    """
    if not points:
        return None
    if len(points) == 1:
        return points[0][1]

    bs = [p[0] for p in points]
    as_ = [p[1] for p in points]

    # If b is below the first breakpoint or above the last, extrapolate linearly
    # (change to clamp if you prefer)
    idx = bisect.bisect_left(bs, b)

    if idx == 0:
        b0, a0 = bs[0], as_[0]
        b1, a1 = bs[1], as_[1]
    elif idx >= len(bs):
        b0, a0 = bs[-2], as_[-2]
        b1, a1 = bs[-1], as_[-1]
    else:
        b0, a0 = bs[idx-1], as_[idx-1]
        b1, a1 = bs[idx], as_[idx]

    if b1 == b0:
        return a0  # avoid div by zero

    t = (b - b0) / (b1 - b0)
    return a0 + t * (a1 - a0)


# -----------------------------
# Data container
# -----------------------------

def nested_dict():
    return defaultdict(nested_dict)

# data[rei][omega][n] = list of (b, a)
data = nested_dict()

# -----------------------------
# Load your CSV
# -----------------------------
#
# Expected columns (case-sensitive here; rename if needed):
# 'Standard fire resistance' (REI category like 'REI 60')
# 'Mechanical reinforcement ratio ω' (float like 0.100, 0.500, 1.000)
# 'n = 0,15', 'n = 0,3', 'n = 0,5', 'n = 0,7'  (cell strings)
#
# If your headers differ, adapt the names below.

def load_table(csv_path):
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row[0]:
                REI = row[0]
            rei_raw = (row.get("Standard fire resistance") or "").strip()
            if rei_raw:
                last_rei = rei_raw
            rei = last_rei  # carry-down merged cells

            # omega
            omega_str = (row.get("Mechanical reinforcement ratio ω") or "").strip()
            if not omega_str:
                continue
            try:
                omega = float(omega_str)
            except ValueError:
                continue

            # n-columns (adjust names if required)
            n_cols = [
                ("n = 0,15", 0.15),
                ("n = 0,3",  0.30),
                ("n = 0,5",  0.50),
                ("n = 0,7",  0.70),
            ]

            for col_name, n_val in n_cols:
                cell = row.get(col_name)
                pts = parse_cell(cell)
                if pts:
                    data[rei][omega][n_val] = pts

# Example:
# load_table("your_table.csv")


# -----------------------------
# Bilinear interpolation across (omega, n)
# -----------------------------

def bilinear_a(rei, omega, n, b):
    """
    Return interpolated a for given (rei, omega, n, b).
    Steps:
      - Find the lattice rectangle around (omega, n): (w0<=omega<=w1, n0<=n<=n1)
      - For each corner, compute a_corner(b) via piecewise interpolation on the corner's breakpoints
      - Bilinearly interpolate those four corner values in (omega, n)
    If data is missing so bilinear is impossible, falls back to nearest 1D/point if available.
    Returns None if no usable data.
    """
    rei_map = data.get(rei, {})
    if not rei_map:
        return None

    omegas = sorted(rei_map.keys())
    # find neighbors in omega
    i = bisect.bisect_left(omegas, omega)
    if i == 0:
        w0 = w1 = omegas[0]
    elif i == len(omegas):
        w0 = w1 = omegas[-1]
    else:
        w0, w1 = omegas[i-1], omegas[i]

    def n_neighbors(w):
        ns = sorted(rei_map[w].keys())
        j = bisect.bisect_left(ns, n)
        if j == 0:
            return ns[0], ns[0]
        elif j == len(ns):
            return ns[-1], ns[-1]
        else:
            return ns[j-1], ns[j]

    n0_w0, n1_w0 = n_neighbors(w0)
    n0_w1, n1_w1 = n_neighbors(w1)

    # collect corner values
    corners = []
    for (w, nn) in [(w0, n0_w0), (w0, n1_w0), (w1, n0_w1), (w1, n1_w1)]:
        pts = rei_map.get(w, {}).get(nn, [])
        a_val = piecewise_a_from_b(b, pts)
        corners.append(((w, nn), a_val))

    # If all corners None → no data
    if all(v is None for (_, v) in corners):
        return None

    # If we can't form a full rectangle, progressively fall back
    # Build unique sorted axes present in corners with data
    present = [c for c in corners if c[1] is not None]
    if len({c[0][0] for c in present}) == 1 and len({c[0][1] for c in present}) == 1:
        # single point
        return present[0][1]

    # If we have two points on same omega (interpolate in n)
    def interp1d(x0, y0, x1, y1, x):
        if x1 == x0:
            return y0
        t = (x - x0) / (x1 - x0)
        return y0 + t * (y1 - y0)

    # Try to get two along n at w0
    a_w0 = None
    if corners[0][1] is not None and corners[1][1] is not None:
        a_w0 = interp1d(corners[0][0][1], corners[0][1], corners[1][0][1], corners[1][1], n)
    elif corners[0][1] is not None:
        a_w0 = corners[0][1]
    elif corners[1][1] is not None:
        a_w0 = corners[1][1]

    # Try to get two along n at w1
    a_w1 = None
    if corners[2][1] is not None and corners[3][1] is not None:
        a_w1 = interp1d(corners[2][0][1], corners[2][1], corners[3][0][1], corners[3][1], n)
    elif corners[2][1] is not None:
        a_w1 = corners[2][1]
    elif corners[3][1] is not None:
        a_w1 = corners[3][1]

    # If we have both a_w0 and a_w1, interpolate across omega
    if (a_w0 is not None) and (a_w1 is not None):
        return interp1d(w0, a_w0, w1, a_w1, omega)
    # Otherwise return whichever side we have
    return a_w0 if a_w0 is not None else a_w1


# -----------------------------
# Public API
# -----------------------------

def get_axis_distance(rei, omega, n, b_min):
    """
    High-level query: given (rei category, omega, n, b_min), return axis distance 'a'
    using piecewise + bilinear interpolation. Returns None if not computable.
    """
    return bilinear_a(rei, omega, n, b_min)


# Example usage (after load_table("your_table.csv")):
load_table("axis_distance_lookup.csv")
a = get_axis_distance("REI 120", 0.5, 0.5, 260)
# print(a)

