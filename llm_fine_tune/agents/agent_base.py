import os
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()

class Agent(ABC):
    def __init__(self, api_key_env_var=None, api_key=None):
        self.api_key = api_key or os.getenv(api_key_env_var)

        if not self.api_key:
            raise ValueError(f"API key not provided and {api_key_env_var} environment variable not set.")
        
    @abstractmethod
    def generate(self, *args, **kwargs):
        pass