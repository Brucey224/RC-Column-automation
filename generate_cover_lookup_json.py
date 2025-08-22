import json
import csv
import itertools

grades = ["C12/16","C16/20","C20/25","C25/30","C28/35","C30/37","C32/40","C35/45","C40/50","C45/55","C50/60","C55/67","C60/75","C70/85","C80/95","C90/105"]
exposures = ["XC1","XC2","XC3", "XC4", "XD1","XD2","XD3","XS1","XS2","XS3"]
cements = ["CEM I","CEM II/A","CEM II/B-S","SRPC","CEM II/B-V", "CEM III/A","CEM III/B","CEM IV/B"]

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

with open("Cover_lookup.csv", newline="") as f:
    reader = csv.reader(f)
    for row in reader:
        if row[0]:
            exposure = expand_range(row[0], exposures)
        if row[1]:
            cement = expand_range(row[1], cements)
        if row[2]:
            grade = expand_range(row[2], grades)
        cover = row[3]
        print(f"Setting cover for {exposure}, {cement}, {grade} = {cover}")
         

def build_json_from_csv(input_file, output_file):
    data = {}
    last_exposure, last_cement = None, None

    with open(input_file, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Carry forward missing values
            exposure = row["Exposure Class"].strip() or last_exposure
            cement = row["Cement Type"].strip() or last_cement
            grade = row["Concrete Grade"].strip()
            cover = row["Cover"].strip()

            # Update last seen values
            last_exposure = exposure
            last_cement = cement

            # Expand ranges
            exp_values = expand_range(exposure, exposures)
            cem_values = expand_range(cement, cements)
            grd_values = expand_range(grade, grades)

            # Parse cover (int or None)
            cover_val = None if cover.upper() == "NULL" else int(cover)

            # Insert into JSON hierarchy
            for exp in exp_values:
                for cem in cem_values:
                    for grd in grd_values:
                        data.setdefault(exp, {}).setdefault(cem, {})[grd] = {"cover": cover_val}

    # Save to file
    with open(output_file, "w") as f:
        json.dump(data, f, indent=4)

build_json_from_csv("Cover_lookup.csv", "cover.json")