"""
This file generates simulated pollution data over a 24 hour period.
Output saved as a JSON file, structured to mimic the UTMC Open Data Service
and to be consumed by PANT Spring API
Author: Ross Cochrane
"""

import random
import json
from datetime import datetime, timedelta
import os



# Settings for the simulation:
num_sites = 130
start_time = datetime(2025, 5, 19, 0, 0, 0)
interval_minutes = 10
num_points = (24 * 60) // interval_minutes  # 144 points for 24 hours


def is_busy_period(ts):
    """
    A function to determine if the timestamp is during a busy period 
    ie 8:00-9:00 or 16:00-19:00.
    """
    hour = ts.hour
    return (8 <= hour < 9) or (16 <= hour < 19)



# A program to generate the dataset.
sites = []
for site_num in range(1, num_sites + 1):
    system_code = f"SITE{site_num:03d}"
    dynamics = []

    for i in range(num_points):
        current_time = start_time + timedelta(minutes=i * interval_minutes)
        busy = is_busy_period(current_time)

        
        # Simulate pollutant and noise values based on busy or quiet period.
        # Data points taken from: no and no2: Sunderland Wessington Way. co: Newcastle 
        # centre historic (2012) monitoring sites
        # Noise: www.extrium.co.uk/noiseviewer.html
        
        co = round(random.uniform(0.5, 5.0) if busy else random.uniform(0.1, 0.17), 2)
        no = round(random.uniform(20, 150) if busy else random.uniform(1, 10), 2)
        no2 = round(random.uniform(40, 300) if busy else random.uniform(5, 30), 2)
        noise = round(random.uniform(70, 100) if busy else random.uniform(30, 60), 2)
        rh = round(random.uniform(70, 85) if busy else random.uniform(55, 59.9))
        
        # Set the temperature according to the time of day
        # TO DO: Change this to follow a day pattern
        if 10 <= current_time.hour < 18:
            temperature = round(random.uniform(18, 24), 1)
        elif 22 <= current_time.hour or current_time.hour < 6:
            temperature = round(random.uniform(5, 10), 1)
        else:
            temperature = round(random.uniform(7, 17), 1)

        battery = round(random.uniform(3.5, 4.2), 1)

        dynamics.append({
            "co": co,
            "no": no,
            "no2": no2,
            "rh": rh,
            "temperature": temperature,
            "noise": noise,
            "battery": battery,
            "lastUpdated": current_time.strftime("%Y-%m-%dT%H:%M:%S.000+0000")
        })

    sites.append({
        "systemCodeNumber": system_code,
        "dynamics": dynamics
    })


# Save JSON to data folder

os.makedirs("data", exist_ok=True)

file_path = os.path.join("data", "pollution_data.json")
with open(file_path, "w") as json_file:
    json.dump(sites, json_file, indent=4)

print(f"JSON data successfully saved to {file_path}")
