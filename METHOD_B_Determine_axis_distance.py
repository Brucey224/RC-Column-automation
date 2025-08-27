import bisect
import json
from pandas import json_normalize

def lerp(x0, y0, x1, y1, x):
    """Linear interpolation between (x0, y0) and (x1, y1)."""
    if x1 == x0:
        return y0  # avoid divide by zero
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def piecewise_interp(b0, a0, b1, a1, b_lookup):
    """Piecewise interpolation for axis distance."""
    if b_lookup <= b0:
        return a0
    elif b_lookup >= b1:
        return a1
    else:
        return a0 + (a1 - a0) * (b_lookup - b0) / (b1 - b0)

def get_axis_distance(data, rei, omega, n, b_lookup):
    """
    Query normalized lookup table and return minimum axis distance a
    for given (rei, omega, n, b) using piecewise interpolation.
    """
    # Step 1: Get REI block
    rei_block = data.get(rei, {}).get("omega", {})
    if not rei_block:
        raise ValueError(f"REI {rei} not found")

    # Step 2: Get sorted omega keys
    omega_keys = sorted(float(k) for k in rei_block.keys())
    pos = bisect.bisect_left(omega_keys, omega)
    print(f"pos(omega): {pos}")
    if pos == 0 or pos == len(omega_keys):
        raise ValueError(f"omega={omega} outside table range")
    omega_low, omega_high = omega_keys[pos-1], omega_keys[pos]

    # Step 3: For each omega, get a(n,b)
    def a_at(rei_block, omega_key, n, b_lookup):
        n_block = rei_block[str(omega_key)]["n"]
        n_keys = sorted(float(k) for k in n_block.keys() if n_block[k] != "NULL")
        pos_n = bisect.bisect_left(n_keys, n)
        if pos_n == 0 or pos_n == len(n_keys):
            raise ValueError(f"n={n} outside table range for omega={omega_key}")
        n_low, n_high = n_keys[pos_n-1], n_keys[pos_n]

        # Step 3a: piecewise interpolation in b for n_low and n_high
        def interp_ab(entry, b_lookup):
            b0, a0, b1, a1 = entry["b_0"], entry["a_0"], entry["b_1"], entry["a_1"]
            return piecewise_interp(b0, a0, b1, a1, b_lookup)

        a_low = interp_ab(n_block[str(n_low)][0], b_lookup)
        a_high = interp_ab(n_block[str(n_high)][0], b_lookup)
        print(f"n_low: {n_low}, n_high: {n_high}, a_low: {a_low}, a_high: {a_high}")

        # Step 3b: interpolate in n
        return lerp(n_low, a_low, n_high, a_high, n)

    a_omega_low = a_at(rei_block, omega_low, n, b_lookup)
    a_omega_high = a_at(rei_block, omega_high, n, b_lookup)

    # Step 4: interpolate in omega
    a_final = lerp(omega_low, a_omega_low, omega_high, a_omega_high, omega)

    return a_final


with open("axis_lookup.json") as f:
    data = json.load(f)

a_val = get_axis_distance(data, rei="REI 90", omega=0.105, n=0.16, b_lookup=301)
print("Minimum axis distance a =", a_val)