"""
A module that simulates air quality data by loading pre-generated readings and 
interpolating values. Pushes updates every 60 seconds.
Author: Ross Cochrane
"""


import json
from datetime import datetime, timedelta, timezone
import logging
import numpy
import os
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from subscriptions_utils import notify_subscribers



def load_json(file_name: str, json_data: list) -> bool:
    """
    A function to load a json file into a list of dictionaries
    """
    json_data.clear()
    with open(file_name, "r") as file:
        input_file = json.load(file)
    success = True
    

    # Looping over each site
    for site in input_file:
        site_data = {}
        site_data["systemCodeNumber"] = site["systemCodeNumber"]
        site_data["dynamics"] = []

        # Iterating through sets of recorded measurements for the site
        for dynamic in site["dynamics"]:
            measurement_dict = {}
            local_success = True
            
            # Iterating through each measurement and its value
            for measurement, value in dynamic.items(): 
                try:
                    if measurement == "rh":
                        value = int(value)
                    elif measurement == "lastUpdated":
                        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f%z')
                    elif measurement in ["co", "no", "no2", "temperature", "noise", "battery"]:
                        value = float(value)
                except ValueError:
                        logging.error(f"Failed to convert {measurement} at site {site['systemCodeNumber']}.")
                        local_success = False
                        success = False
                
                if local_success:
                    measurement_dict[measurement] = value
            
            if measurement_dict:
                site_data["dynamics"].append(measurement_dict)
               
        json_data.append(site_data)
    
    return success


def simulate_live_data():
    """
    A method to simulate live data by pushing the latest pollution data to subscribers.
    """

    current_sim_time = simulate_live_data.timestamp
    data_to_push = []

    for site in pollution_data.data:
        dynamics = site.get("dynamics", [])
        # Select the closest dynamics entry to the current simulated time
        # and ensure it is within 10 seconds of the current time
        if dynamics:
            closest = min(
                dynamics,
                key=lambda d: abs((d["lastUpdated"] - current_sim_time).total_seconds())
            )
            if abs((closest["lastUpdated"] - current_sim_time).total_seconds()) <= 10:
                data_to_push.append({
                "systemCodeNumber": site["systemCodeNumber"],
                **{k: v for k, v in closest.items() if k != "lastUpdated"},
                "lastUpdated": closest["lastUpdated"].isoformat()
                })


    logging.info(f"Pushing data at {current_sim_time.isoformat()} with {len(data_to_push)} records.")

    if data_to_push:
        notify_subscribers("AIR QUALITY DYNAMIC", data_to_push)

    # Advance simulated time by 60 seconds as per UTMC specs
    simulate_live_data.timestamp += timedelta(seconds=60)
    

class PollutionData:
    """
    Pollution data per second
    """

    def __init__(self) -> None:
        self.data = []
        self.site_metadata_cache = {}
        self.__loaded = False
        self.load_site_metadata()


    def __interpolate_data__(self, input_data) -> list:
        """
        A method to generate interpolated pollution values
        """

        for site in input_data:
            new_dynamics = []

            # Sort dynamics by timestamp
            dynamics_sorted = sorted(site["dynamics"], key=lambda timestamp: timestamp["lastUpdated"])

            for i in range(len(dynamics_sorted) - 1):
                current = dynamics_sorted[i]
                next_entry = dynamics_sorted[i + 1]

                start_time = current["lastUpdated"]
                end_time = next_entry["lastUpdated"]
                elapsed_seconds = int((end_time - start_time).total_seconds())

                # Interpolate each pollutant between timestamps, every 10 
                step = 10
                for j in range(0, elapsed_seconds, step):
                    interpolated_time = start_time + timedelta(seconds=j)
                    interpolated_entry = {
                        "co" : numpy.interp(j, [0, elapsed_seconds], [current["co"], next_entry["co"]]),
                        "no" : numpy.interp(j, [0, elapsed_seconds], [current["no"], next_entry["no"]]),
                        "no2" : numpy.interp(j, [0, elapsed_seconds], [current["no2"], next_entry["no2"]]),
                        "rh" : numpy.interp(j, [0, elapsed_seconds], [current["rh"], next_entry["rh"]]),
                        "temperature" : numpy.interp(j, [0, elapsed_seconds], [current["temperature"], next_entry["temperature"]]),
                        "noise" : numpy.interp(j, [0, elapsed_seconds], [current["noise"], next_entry["noise"]]),
                        "battery" : numpy.interp(j, [0, elapsed_seconds], [current["battery"], next_entry["battery"]]),
                        "lastUpdated" : interpolated_time
                    }
                    new_dynamics.append(interpolated_entry)

                # Append the final reading
                new_dynamics.append(dynamics_sorted[-1])

            site["dynamics"] = new_dynamics

        return input_data
      

    def load(self) -> bool:
        """
        A method to load pollution data from a json file.
        """

        success = True

        input_data = []
        self.data.clear()

        # Load the json data files
        # Go one level up from the src directory to the project root
        parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        data_dir = os.path.join(parent_dir, "data")
        file_path = os.path.join(data_dir, "pollution_data.json")
        success = load_json(file_path, input_data)

        if not success:
            logging.error("Failed to load json data.")
            return success
        
        # Interpolate missing values and store data within the class
        self.__interpolate_data__(input_data)

        # Store processed data in the instantiation
        self.data = input_data
        
        if success:
            print("Data loaded and processed successfully.")
        self.__loaded = True
        return self.__loaded
    

    def load_site_metadata(self, file_name=None, json_data=None) -> None:
        """
        A method to  method preload the metadata from a json file and store it in a cache
        for quick access.
        """
        
        if file_name is None:
            # Go one level up from the src directory to the project root
            parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            data_dir = os.path.join(parent_dir, "data")
            file_name = os.path.join(data_dir, "metadata.json")
        if json_data is None:
            json_data = []


        json_data.clear()
        with open(file_name, "r") as file:
            all_sites = json.load(file)
    
        
        for site in all_sites:
            system_code = site.get("systemCodeNumber")
            point = site.get("definitions", [{}])[0].get("point", {})
            coordinates = {
                "lat": point.get("latitude"),
                "lon": point.get("longitude"),
            }
            self.site_metadata_cache[system_code] = coordinates
        print("Site metadata preloaded successfully.")
                   
                


    def get_pollution_data(self, current_timestamp: datetime, system_code_number: str ) -> list:
        """
        A method to return pollution data for a given time and site.
        """
        if isinstance(current_timestamp, str):
            try:
                current_timestamp = datetime.strptime(current_timestamp, '%Y-%m-%dT%H:%M:%S.%f%z')
            except ValueError:
                print("Error: incorrect timestamp format")
                return None


        pollution_data_list = []

        if not self.__loaded:
            self.load()
        if not self.__loaded:
            print("Error: failed to load pollution data")
            return None

        # Find speficied site and closest pollution readings based on given time  
        for site in self.data:
            if system_code_number == site["systemCodeNumber"]:
                
                closest_dynamic = min(
                    site["dynamics"], 
                    key=lambda dynamic: abs((dynamic['lastUpdated'] - current_timestamp).total_seconds())
                )
                pollution_data_list.append(closest_dynamic)
                
        return pollution_data_list


    def get_site_coordinates(self, system_code_number: str) -> dict:
        """
        A method to get the coordinates of a site based on its system code number.
        """
        if not self.site_metadata_cache:
            self.load_site_metadata()
        
        return self.site_metadata_cache.get(system_code_number, None)
    
    
    def get_all_sites_coordinates(self) -> list:
        """
        A method to get the coordinates of all sites.
        """
        if not self.site_metadata_cache:
            self.load_site_metadata()
        
        return [
            {"systemCodeNumber": key, **value}
            for key, value in self.site_metadata_cache.items()
        ]




       
# Create a global instance
pollution_data = PollutionData()
pollution_data.load()                   


# Initial timestamp to simulate from
simulate_live_data.timestamp = datetime(2025, 5, 19, 0, 0, 0, tzinfo=timezone.utc)

scheduler = BackgroundScheduler()
scheduler.add_job(simulate_live_data, 'interval', seconds=60)
scheduler.start()

