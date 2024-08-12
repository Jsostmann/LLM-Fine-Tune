from .agent_base import Agent
from openai import OpenAI
from groq import Groq
import google.generativeai as genai

class GroqAgent(Agent):
    def __init__(self, api_key=None):
        super().__init__(api_key_env_var="GROG_API_KEY", api_key=api_key)
        self.client = Groq(api_key=self.api_key)

    def generate(self, *args, **kwargs):
        # OpenAI-specific data generation logic
        messages = []
        user_prompt = kwargs.get('prompt')
        model = kwargs.get('model')

        if user_prompt:
            messages.append({"role": "user", "content": user_prompt})
        try:
            response = self.client.chat.completions.create(messages=messages, model=model, max_tokens=1024)
        except Exception as e:
            print(f"Error generating response: {e}")
            return None
        return response.choices[0].message.content.strip()

class OpenAIAgent(Agent):
    def __init__(self, api_key=None, use_local=False, base_url=None):
        super().__init__(api_key_env_var="OPENAI_API_KEY", api_key=api_key)
        self.use_local = use_local
        self.base_url = base_url

        if use_local:
            if not base_url:
                raise ValueError("Base URL must be provided for local use.")
            # Instantiate the local version of OpenAI
            self.client = OpenAI(base_url=base_url, api_key=self.api_key)
        else:
            self.client = OpenAI(api_key=self.api_key)


    def generate(self, *args, **kwargs):
        # OpenAI-specific data generation logic
        messages = []
        system_prompt = kwargs.get('system_prompt')
        user_prompt = kwargs.get('user_prompt')
        model = kwargs.get('model')

        if user_prompt:
            messages.append({"role": "user", "content": user_prompt})
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        kwargs['messages'] = messages
        response = self.client.chat.completions.create(messages=messages, model=model)
        return response.choices[0].message.content.strip()

class GeminiAgent(Agent):
    def __init__(self, api_key=None):
        super().__init__(api_key_env_var="GEMMINI_KEY", api_key=api_key)
        genai.configure(api_key=self.api_key)

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json"
        }

        self.client = genai.GenerativeModel(model_name="models/gemini-1.5-flash", generation_config=generation_config)

    
    def generate(self, *args, **kwargs):
        # Gemini-specific data generation logic
        user_prompt = kwargs.get('prompt')
        chat_session = self.client.generate_content(user_prompt)
        return chat_session.text



class AgentFactory:
    @staticmethod
    def get_agent(agent_name, **kwargs):
        agents = {
            "GROG": GroqAgent,
            "LLAMA": OpenAIAgent,
            "GEMINI": GeminiAgent
        }
        
        agent_class = agents.get(agent_name)
        
        if not agent_class:
            raise ValueError(f"Agent {agent_name} is not supported.")
        
        return agent_class(**kwargs)