import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
SCHEMA_DIR = os.path.join(BASE_DIR, "schemas")
PROMPT_DIR = os.path.join(BASE_DIR, "prompts")
FINE_TUNE_DIR = os.path.join(BASE_DIR, "fine_tune_data")

DEFAULT_SCHEMA = os.path.join(SCHEMA_DIR, "schema.json")
DEFAULT_PROMPT = os.path.join(PROMPT_DIR, "prompt.txt")
DEFAULT_FINE_TUNE = os.path.join(FINE_TUNE_DIR, "data.json")
DEFAULT_PROMPT_SUMMARY = os.path.join(PROMPT_DIR, "summary_prompt.txt")

BASE_URL = "https://www.eastwoodhomes.com/"
DATA_URL = f"{BASE_URL}api/search?query="

CITIES = ["Greensboro+Area", "Atlanta", "Charleston", "Columbia", "Greenville", "Richmond", "Charlotte", "Raleigh"]
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