import os
from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.agents import load_tools

load_dotenv()

llm = OpenAI(temperature=0.5, streaming=True, openai_api_key=os.getenv('API_KEY'))



