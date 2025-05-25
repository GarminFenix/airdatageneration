import json
from datetime import datetime, timedelta
import logging
import numpy
import os

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


class PollutionData:
    """
    Pollution data per second
    """

    def __init__(self) -> None:
        self.data = []
        self.__loaded = False

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

                # Interpolate each pollutant between timestamps, every 10 seconds
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

        self.__loaded = True
        return self.__loaded


    def get_pollution_data(self, current_timestamp: datetime, system_code_number: str ) -> list:
        
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


        



def main():
    data_list = []
    load_json("data/pollution_data.json", data_list )
    pollution_data = PollutionData()
    pollution_data.__interpolate_data__(data_list)
    
    print(pollution_data.get_pollution_data("2025-05-19T00:00:00.000+0000", "SITE001"))
    
          
    
if __name__ == "__main__":
    main() 
