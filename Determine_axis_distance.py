import json
from pandas import json_normalize

with open("axis_lookup.json") as f:
    data = json.load(f)

df = json_normalize(data)
print(df)