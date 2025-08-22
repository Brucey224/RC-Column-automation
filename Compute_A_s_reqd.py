# Purpose of code 
# The purpose of this code is to compute the required area of reinforcement within a given RC column

# Inputs required by user
# Column geometry
# series of [N,M] internal forces

import numpy as np
import json

bar_sizes = [8, 10, 12, 16, 20, 25, 32, 40] #mm

def compute_c_min(exposure_class, cement_type, grade, bar_diameter, cover_deviation = 10):
    with open("cover_lookup.json") as f:
        cover_data = json.load(f)
        if cover_data[exposure_class][cement_type][grade]['cover']:
            durability_cover = float(cover_data[exposure_class][cement_type][grade]['cover']) + cover_deviation
        else:
            print("invalid concrete grade - exposure class - cement type combination")
        cover = max(10, durability_cover, bar_diameter)
    return cover

def compute_A_s_reqd(N, M, column):
    b = column.section.b
    h = column.section.h
    A_smin = determine_min_rebar(b,h)
    possible_arrangements = []
    for bar_size in bar_sizes:
        min_spacing = max(bar_size, 20)
        num_rows = 2
        num_cols = 2
        while code_compliance == True:
            horizontal_bar_spacing = (column.section.b - 2*cover - 2*link)
            if horizontal_bar_spacing > min_spacing:
                possible_arrangements.append(bar_size, num_rows, num_cols)
            else:
                code_compliance = False
            while code_compliance == True:
                vertical_bar_spacing = (column.section.h - 2*cover - 2*link)
                if vertical_bar_spacing > min_spacing:
                    possible_arrangements.append(bar_size, num_rows, num_cols) 
                else:
                    code_compliance = False
                num_rows+=1
            num_cols+=1

def determine_min_rebar(b, h):
    
    A_smin = 0.0015* b * h

def determine_max_rebar(b,h):
    A_s_max = 0.04 * b * h

cover = compute_c_min("XC1", "CEM I", "C30/37",16)
print(cover)