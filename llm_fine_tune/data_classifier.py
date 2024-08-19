import os
import json
import glob
import requests
from agents.agents import AgentFactory
from constants import SCHEMA_DIR, DATA_DIR, PROMPT_DIR, DEFAULT_SCHEMA, DEFAULT_PROMPT, DEFAULT_FINE_TUNE, FINE_TUNE_DIR

class DataClassifier:
    def __init__(self, agent):
        self.agent=agent
        self.prompt = os.path.join(PROMPT_DIR, "classify_prompt.txt")
        self.input_file = os.path.join(FINE_TUNE_DIR, "data.jsonl")
        self.output_file = os.path.join(FINE_TUNE_DIR, "classified_data.jsonl")

    def classify_questions(self, model="gemma2:9b"):
        with open(self.prompt, mode="r") as f:
            sys_prompt = f.read()

        with open(self.input_file, 'r') as infile, open(self.output_file, 'w') as outfile:
            for line in infile:
                data = json.loads(line)
                question = data['question']
                label = self.classify_question(question, sys_prompt, model)
                classified_data = {
                    "question": question,
                    "label": label
                }
                outfile.write(json.dumps(classified_data) + '\n')

    def classify_question(self, question, prompt, model):
        formatted_prompt = prompt.format(question=question)        
        response = self.agent.generate(prompt=formatted_prompt, model=model)
        print(response)
        return 1
    
if __name__ == "__main__":
    ollama_agent = AgentFactory.get_agent("LLAMA", use_local=True, base_url="http://localhost:11434/v1")

    classifier = DataClassifier(agent=ollama_agent)
    classifier.classify_questions()