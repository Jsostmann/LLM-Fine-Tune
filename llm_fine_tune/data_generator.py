from openai import OpenAI
from groq import Groq
import os
import json
import glob
from dotenv import load_dotenv

from constants import SCHEMA_DIR, DATA_DIR, PROMPT_DIR, DEFAULT_SCHEMA, DEFAULT_PROMPT

AGENT_MAP = {"GROG": Groq, "LLAMA": OpenAI}

class DataGenerator:
    def __init__(self, use_local, api_key="OPENAI_API_KEY", server_url="http://localhost:11434/v1/", agent="LLAMA"):
        self.server_url = server_url
        self.use_local = use_local
        self.client = None
        self.api_key = None
        
        self.schema_files = self.get_files(SCHEMA_DIR, "*.json")
        self.data_files = self.get_files(DATA_DIR, "*.json")
        self.prompt_files = self.get_files(PROMPT_DIR, "*.txt")

        agent_class = AGENT_MAP.get(agent)

        if not agent_class:
            raise ValueError(f"Invalid agent type: {agent}")
        
        if use_local:
            self.client = agent_class(base_url=server_url, api_key='ollama')

        else:
            load_dotenv()
            self.api_key = os.environ.get(api_key)

            if not self.api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            
            self.client = agent_class(api_key=self.api_key)

    def generate_qa_pairs(self, data_file, schema, system_prompt, model="llama-3.1-70b-versatile"):
    
        with open(data_file, mode="r") as f:
            data = json.load(f)

        json_schema_str = json.dumps(schema, indent=4)
        json_data_str = json.dumps(data, indent=4)
        
        formatted_prompt = system_prompt.format(json_schema=json_schema_str, json_data=json_data_str)

        return self.generate_prompt(user_prompt=formatted_prompt, model=model)
    
    def generate_prompt(self, system_prompt=None, user_prompt=None, model="llama3:8b", temperature=0.7):
        messages=[]

        if user_prompt:
            messages.append({"role": "user", "content": user_prompt})
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        response = self.client.chat.completions.create(model=model, messages=messages, temperature=temperature)
        return response.choices[0].message.content.strip()

    def generate_data(self):
        data = []

        with open(DEFAULT_SCHEMA, mode="r") as f:
            schema = json.load(f)

        with open(DEFAULT_PROMPT, mode="r") as f:
            sys_prompt = f.read()

        for file in self.data_files:
            new_data = self.generate_qa_pairs(data_file=file, schema=schema, system_prompt=sys_prompt)
            print(new_data)
            exit(1)

    def get_files(self, dir, file_pattern, recursive=True):
        files = glob.glob(os.path.join(dir, file_pattern), recursive=recursive)
        return files
    
if __name__ == "__main__":

    
    data_generator = DataGenerator(use_local=False, api_key="GROG_API_KEY", agent="GROG")
    data_generator.generate_data()