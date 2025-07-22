import pandas as pd
import json
from pyproj import Transformer

# Initialize transformer from EPSG:27700 (OSGB) to WGS84
transformer = Transformer.from_crs("epsg:27700", "epsg:4326", always_xy=True)

# Read CSV
df = pd.read_csv("data/AIRQUALITY_DEFINITION.csv", usecols=[
    "SYSTEMCODENUMBER", "SHORTDESCRIPTION", "LONGDESCRIPTION",
    "NORTHING", "EASTING", "LASTUPDATED"
])

# Drop rows with incomplete coordinates
df = df.dropna(subset=["NORTHING", "EASTING"])

# Sort and re-index system code numbers
df = df.sort_values(by="SYSTEMCODENUMBER").reset_index(drop=True)

# Generate SITE IDs
df["systemCodeNumber"] = ["SITE{:03d}".format(i + 1) for i in range(len(df))]

# Convert northing/easting to lat/lon
def convert_coords(e, n):
    lon, lat = transformer.transform(e, n)
    return lat, lon

fixed_timestamp = "2025-06-26T19:47:00.000+0000"

json_output = []
for _, row in df.iterrows():
    lat, lon = convert_coords(row["EASTING"], row["NORTHING"])
    entry = {
        "systemCodeNumber": row["systemCodeNumber"],
        "definitions": [
            {
                "longDescription": row["LONGDESCRIPTION"],
                "point": {
                    "easting": row["EASTING"],
                    "northing": row["NORTHING"],
                    "latitude": round(lat, 6),
                    "longitude": round(lon, 6)
                },
                "lastUpdated": fixed_timestamp
            }
        ]
    }
    json_output.append(entry)


# Save to JSON file
with open("data/metadata.json", "w") as f:
    json.dump(json_output, f, indent=2)
