import os
import streamlit as st
from dotenv import load_dotenv, find_dotenv
from langchain_groq import ChatGroq
from langchain import hub
from langchain.agents import load_tools, AgentExecutor, create_react_agent
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
import asyncio
from GroqSearch.researcher import Researcher


load_dotenv(find_dotenv())
groq_api_key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(temperature=0.5, model_name="mixtral-8x7b-32768", groq_api_key=groq_api_key)
tools = load_tools(["ddg-search"])
prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm,  tools,  prompt)
agent_executor = AgentExecutor(agent= agent, tools= tools, verbose=True, handle_parsing_errors=True)
st_callback = StreamlitCallbackHandler(st.container())

@st.cache_resource(show_spinner=True)
def create_researcher():
    researcher = Researcher()
    return researcher
research_apprentice = create_researcher()

question = 'What is a recipe for baked salmon?'

research_apprentice.search_articles(question)