from openai import OpenAI
import csv
import os
import json
from dotenv import load_dotenv

class DataGenerator:
    def __init__(self, use_local, api_key="OPENAI_API_KEY", server_url="http://localhost:11434/v1/"):
        self.server_url = server_url
        self.use_local = use_local
        self.client = None
        self.api_key = None

        if use_local:
            self.client = OpenAI(base_url=server_url, api_key='ollama')
        else:
            load_dotenv()
            self.api_key = os.environ.get(api_key)
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            self.client = OpenAI(api_key=self.api_key)


    def generate_qa_pair(self, system_prompt, user_prompt, model="llama3:8b"):

        messages=[{"role": "user", "content": user_prompt},
                  {"role": "system", "content": system_prompt}]
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

if __name__ == "__main__":
    data = []
    sys_prompt = None
    data = None
    schema = None

    with open("system_messages/basic_division_message.txt", mode="r", encoding="utf-8") as f:
        sys_prompt = f.read()
        
    with open("schemas/division_schema.json", mode="r", encoding="utf-8") as f:
        schema = f.read()

    with open("eastwood_data/Atlanta.json", mode="r", encoding="utf-8") as f:
        data = json.load(f)
        data = data['division']

    user_prompt = "Schema:\n{}\nData:\n{}".format(schema, data)
    data_generator = DataGenerator(use_local=True)
    for i in range(10):
        res = data_generator.generate_qa_pair(user_prompt=user_prompt, system_prompt=sys_prompt)
        print(res)