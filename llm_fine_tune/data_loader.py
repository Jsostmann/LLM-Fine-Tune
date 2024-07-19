import json
import requests
import os
import re
from bs4 import BeautifulSoup

FIELDS = [
    r"^communities\.\d+\.name$",
    r"^communities\.\d+\.from_the$",
    r"^communities\.\d+\.hoa_name$",
    r"^communities\.\d+\.hoa_yearly_fee$",
    r"^communities\.\d+\.city$",
    r"^communities\.\d+\.state\.state$",
    r"^communities\.\d+\.zip$",
    r"^communities\.\d+\.county$",
    r"^communities\.\d+\.headline$",
    r"^communities\.\d+\.description$",
    r"^communities\.\d+\.amenities_photos\.\d+\.caption$",
    r"^communities\.\d+\.model_home_phone$",

    r"^division\.name$",
    r"^division\.subheadline$",
    r"^division\.intro$",
    r"^division\.description$",
    r"^division\.highlights\.\d+\.name$",
    r"^division\.highlights\.\d+\.description$",

    r"^(homes_mir|homes_rtb)\.\d+\.floor_plan\.extension\.name$",
    r"^(homes_mir|homes_rtb)\.\d+\.price$",
    r"^(homes_mir|homes_rtb)\.\d+\.address$",
    r"^(homes_mir|homes_rtb)\.\d+\.city$",
    r"^(homes_mir|homes_rtb)\.\d+\.zip$",
    r"^(homes_mir|homes_rtb)\.\d+\.square_feet$",
    r"^(homes_mir|homes_rtb)\.\d+\.bedrooms$",
    r"^(homes_mir|homes_rtb)\.\d+\.bathrooms$",
    r"^(homes_mir|homes_rtb)\.\d+\.half_baths$",
    r"^(homes_mir|homes_rtb)\.\d+\.garage$",
    r"^(homes_mir|homes_rtb)\.\d+\.stories$",
    r"^(homes_mir|homes_rtb)\.\d+\.basement$",
    r"^(homes_mir|homes_rtb)\.\d+\.description$",
    r"^(homes_mir|homes_rtb)\.\d+\.unique_features$",
    r"^(homes_mir|homes_rtb)\.\d+\.sold$",
    r"^(homes_mir|homes_rtb)\.\d+\.community\.name$",
    r"^(homes_mir|homes_rtb)\.\d+\.floorplan_type\.name$",
    r"^(homes_mir|homes_rtb)\.\d+\.special\d+\.summary$"
]

BASE_URL = "https://www.eastwoodhomes.com/api/search?query="
CITIES = ["Greensboro+Area", "Atlanta", "Charleston", "Columbia", "Greenville", "Richmond", "Charlotte", "Raleigh"]
DATA_DIR = "eastwood_data"


def contains_html(text):
    if isinstance(text, str):
        html_pattern = re.compile(r'<[^>]+>')
        return bool(html_pattern.search(text))
    return False


def extract_text_from_html(text):
    if contains_html(text):
        soup = BeautifulSoup(text, "html.parser")
        text = soup.get_text().replace("\n","")

    return text


def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def download_json(url, output_file):
    try:
        response = requests.get(url)
        response.raise_for_status()

        with open(output_file, 'w') as f:
            
            data = response.json()
            json.dump(data, f, indent=4)
        
        print(f"Downloaded JSON data has been written to {output_file}")

        return data
    
    except requests.exceptions.RequestException as e:
        print(f"Error downloading JSON: {e}")


def load_json(file_name):
    try:
        with open(file_name, 'r') as f:
            data = json.load(f)
        
        print(f"JSON data has been loaded to {file_name}")

        return data
    
    except requests.exceptions.RequestException as e:
        print(f"Error Loading JSON: {e}")


def save_json(data, file_name):
    try:
        with open(file_name, 'w') as f:        
    
            json.dump(data, f, indent=4)
        
            print(f"JSON data has been saved to {file_name}")
    
    except requests.exceptions.RequestException as e:
        print(f"Error Saving JSON: {e}")


def filter_data(data, fields):
    compiled_patterns = [re.compile(pattern) for pattern in fields]
    filtered_data = {key: value for key, value in data.items() if any(pattern.match(key) for pattern in compiled_patterns)}

    return filtered_data


def flatten_data(data):
    def flatten_data_recursive(data, parent_key):
        current_data = {}

        if isinstance(data, dict):
            for k, v in data.items():

                new_key = f"{parent_key}.{k}" if parent_key else k
                new_data = flatten_data_recursive(v, new_key)

                new_data = {k: v for k ,v in new_data.items() if v}
                current_data.update(new_data)

        elif isinstance(data, list):
            for i, item in enumerate(data):
                
                new_key = f"{parent_key}.{i}" if parent_key else str(i)
                new_data = flatten_data_recursive(item, new_key)

                new_data = {k: v for k ,v in new_data.items() if v}
                current_data.update(new_data)
        else:
            current_data[parent_key] = data  

        return current_data

    return flatten_data_recursive(data, "")


def transform_city_data(data):

    mir_homes_offset = None
    rtb_homes_offset = None
    
    transformed_data = {
        "communities": [],
        "homes_mir": [],
        "homes_rtb": [],
        "division": {}
    }

    for key, value in data.items():
        value = extract_text_from_html(value)
        if key.startswith("communities"):
            parts = key.split('.')
            n = int(parts[1])
            prop = parts[2]
            if len(transformed_data["communities"]) < n + 1:
                transformed_data["communities"].append({})
            if prop == "amenities_photos":
                if "amenities_photos" not in transformed_data["communities"][n]:
                    transformed_data["communities"][n]["amenities_photos"] = []
                if value not in transformed_data["communities"][n]["amenities_photos"]:
                    transformed_data["communities"][n]["amenities_photos"].append(value)
            else:
                transformed_data["communities"][n][prop] = value
                
        elif key.startswith("homes_mir"):
            parts = key.split('.')
            n = int(parts[1])

            if not mir_homes_offset:
                mir_homes_offset = n
            if n - mir_homes_offset == 1:
                mir_homes_offset = n
            prop = parts[2]
            if len(transformed_data["homes_mir"]) < (mir_homes_offset) + 1:
                transformed_data["homes_mir"].append({})
            else:
                transformed_data["homes_mir"][mir_homes_offset][prop] = value

        elif key.startswith("homes_rtb"):
            parts = key.split('.')
            n = int(parts[1])

            if not rtb_homes_offset:
                rtb_homes_offset = n
            if n - rtb_homes_offset == 1:
                rtb_homes_offset = n
            prop = parts[2]
            if len(transformed_data["homes_rtb"]) < (rtb_homes_offset) + 1:
                transformed_data["homes_rtb"].append({})
            else:
                transformed_data["homes_rtb"][rtb_homes_offset][prop] = value

        elif key.startswith("division"):
            parts = key.split('.')
            prop = parts[1]
            if prop.startswith("highlights"):
                n = int(key.split('.')[2])
                if "highlights" not in transformed_data["division"]:
                    transformed_data["division"]["highlights"] = []
                if len(transformed_data["division"]["highlights"]) < n + 1:
                    transformed_data["division"]["highlights"].append({})
                transformed_data["division"]["highlights"][n][parts[3]] = value
            else:
                transformed_data["division"][prop] = value 

    return transformed_data


def load_city_data():
    
    create_directory(DATA_DIR)

    for city in CITIES:
        city_url = f"{BASE_URL}{city}"
        city_file = f"{city}.json"
        city_path =  os.path.join(DATA_DIR, city_file)

        city_data = None

        if not os.path.exists(city_path):
            city_data = download_json(city_url, city_path)
        else:
            city_data = load_json(city_path)


        flattened_data = flatten_data(city_data)
        filtered_data = filter_data(flattened_data, FIELDS)
        transformed_data = transform_city_data(filtered_data)

if __name__ == "__main__":
    load_city_data()