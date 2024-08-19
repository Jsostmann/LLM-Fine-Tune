import json
import requests
import os
import re
from bs4 import BeautifulSoup
from multiprocessing import Pool

from constants import BASE_URL, DATA_URL, FIELDS, DATA_DIR

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

def get_citiy_names(url):
    cities = []
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        city_elements = soup.find_all('h3', class_='c-card-location__name')
        for div_element in city_elements:
            city = div_element.text
            city = city.replace(" ", "+")
            if city:
                cities.append(city)
    
        return cities
    
    except requests.exceptions.RequestException as e:
        print(f"Error getting city names: {e}")

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def download_json(url, output_file):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        print(f"JSON data has been downloaded to: {output_file}")

        return data
    
    except requests.exceptions.RequestException as e:
        print(f"Error downloading JSON: {e}")


def load_json(file_name):
    try:
        with open(file_name, 'r') as f:
            data = json.load(f)
        
        print(f"JSON data has been loaded from {file_name}")

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
            while len(transformed_data["communities"]) <= n:
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

            if mir_homes_offset is None:
                mir_homes_offset = n
            prop = parts[2]

             #TODO: possible bug. keys of homes are sometimes not contiguous. Ex: 0, 1, 3, 4 or 3, 4, 8, 9
            while len(transformed_data["homes_mir"]) <= (n - mir_homes_offset):
                transformed_data["homes_mir"].append({})
            transformed_data["homes_mir"][n - mir_homes_offset][prop] = value

        elif key.startswith("homes_rtb"):
            parts = key.split('.')
            n = int(parts[1])

            if rtb_homes_offset is None:
                rtb_homes_offset = n
            prop = parts[2]

            #TODO: possible bug. keys of homes are sometimes not contiguous. Ex: 0, 1, 3, 4 or 3, 4, 8, 9
            while len(transformed_data["homes_rtb"]) <= (n - rtb_homes_offset):
                transformed_data["homes_rtb"].append({})
            transformed_data["homes_rtb"][n - rtb_homes_offset][prop] = value

        elif key.startswith("division"):
            parts = key.split('.')
            prop = parts[1]
            if prop.startswith("highlights"):
                n = int(key.split('.')[2])
                if "highlights" not in transformed_data["division"]:
                    transformed_data["division"]["highlights"] = []
                while len(transformed_data["division"]["highlights"]) <= n:
                    transformed_data["division"]["highlights"].append({})
                transformed_data["division"]["highlights"][n][parts[3]] = value
            else:
                transformed_data["division"][prop] = value
                
    transformed_data["homes_mir"] = [house for house in transformed_data["homes_mir"] if house]
    transformed_data["homes_rtb"] = [house for house in transformed_data["homes_rtb"] if house]

    return transformed_data

def load_city_data_async():

    create_directory(DATA_DIR)
    cities = get_citiy_names(BASE_URL)

    with Pool(len(cities)) as pool:
        data = pool.map(get_city_data, cities)

    return data

def get_city_data(city):

    print(f"Getting data for city: {city}")
    city_url = f"{DATA_URL}{city}"
    city_file = f"{city}.json"
    city_path =  os.path.join(DATA_DIR, city_file)

    city_data = None

    if not os.path.exists(city_path):
        city_data = download_json(city_url, city_path)
        flattened_data = flatten_data(city_data)
        filtered_data = filter_data(flattened_data, FIELDS)
        transformed_data = transform_city_data(filtered_data)
        save_json(transformed_data, city_path)
    else:
        city_data = load_json(city_path)

    return city_data

def load_city_data_sync():

    create_directory(DATA_DIR)
    cities = get_citiy_names(BASE_URL)
    
    for city in cities:
        city_url = f"{DATA_URL}{city}"
        city_file = f"{city}.json"
        city_path =  os.path.join(DATA_DIR, city_file)

        city_data = None

        if not os.path.exists(city_path):
            city_data = download_json(city_url, city_path)
            flattened_data = flatten_data(city_data)
            filtered_data = filter_data(flattened_data, FIELDS)
            transformed_data = transform_city_data(filtered_data)
            save_json(transformed_data, city_path)
            
        else:
            city_data = load_json(city_path)

if __name__ == "__main__":
    load_city_data_async()