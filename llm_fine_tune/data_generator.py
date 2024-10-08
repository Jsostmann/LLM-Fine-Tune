import os
import json
import glob
import requests
from agents.agents import AgentFactory
from constants import SCHEMA_DIR, DATA_DIR, PROMPT_DIR, DEFAULT_SCHEMA, DEFAULT_PROMPT, DEFAULT_FINE_TUNE, DEFAULT_PROMPT_SUMMARY

class DataGenerator:
    def __init__(self, agent):
        self.agent = agent
        
        self.schema_files = self.get_files(SCHEMA_DIR, "*.json")
        self.data_files = self.get_files(DATA_DIR, "*.json")
        self.prompt_files = self.get_files(PROMPT_DIR, "*.txt")

    def generate_qa_pairs(self, data_file, schema, system_prompt, model="gemma2:9b"):
        with open(data_file, mode="r") as f:
            data = json.load(f)

        self.get_summary(data)
        exit()
        json_schema_str = json.dumps(schema, indent=4)
        json_data_str = json.dumps(data, indent=4)
        
        formatted_prompt = system_prompt.format(json_schema=json_schema_str, json_data=json_data_str)        
        return self.agent.generate(prompt=formatted_prompt, model=model)

    def generate_qa_pairs_2(self, data_file, system_prompt, model="gemma2:9b"):

        with open(data_file, mode="r") as f:
            data = json.load(f)

        keys = ["homes_rtb", "homes_mir"]

        for key in keys:
            for home_data in data[key]:
                home_details = json.dumps(home_data, indent=4)
                formatted_prompt = system_prompt.format(home_details=home_details)        
                answer = self.agent.generate(prompt=formatted_prompt, model=model)
                qa_list = answer.split("\n")
                self.save_json(qa_list, DEFAULT_FINE_TUNE)


    def generate_data(self, _files=None, out_file=DEFAULT_FINE_TUNE):
        files = _files if _files else self.data_files

        with open(DEFAULT_SCHEMA, mode="r") as f:
            schema = json.load(f)

        with open(DEFAULT_PROMPT, mode="r") as f:
            sys_prompt = f.read()

        for file in files:
            new_data = self.generate_qa_pairs(data_file=file, schema=schema, system_prompt=sys_prompt)
            if not new_data:
                print(file)
                continue
            qa_list = new_data.split("\n")
            self.save_json(qa_list, out_file)

    def generate_data_2(self, _files=None, out_file=DEFAULT_FINE_TUNE):
        files = _files if _files else self.data_files

        with open(DEFAULT_PROMPT_SUMMARY, mode="r") as f:
            sys_prompt = f.read()

        for file in files:
            self.generate_qa_pairs_2(file, sys_prompt)

    def get_files(self, dir, file_pattern, recursive=True):
        files = glob.glob(os.path.join(dir, file_pattern), recursive=recursive)
        return files
    
    def save_json(self, data, file_name):
        try:
            with open(file_name, 'a+') as f:     
                for qa_pair in data:
                    if not qa_pair:
                        continue
                    try:
                        json.dump(json.loads(qa_pair), f)
                        f.write("\n")
                    except Exception as e:
                        print(f"Error saving QA pair: {qa_pair} : {e}")
                print(f"JSON data has been saved to {file_name}")
        
        except requests.exceptions.RequestException as e:
            print(f"Error Saving JSON: {e}")


if __name__ == "__main__":
    ollama_agent = AgentFactory.get_agent("LLAMA", use_local=True, base_url="http://localhost:11434/v1")
    data_generator = DataGenerator(agent=ollama_agent)
    