from config import *
from dotenv import load_dotenv, find_dotenv
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.document_loaders.url import UnstructuredURLLoader
from langchain.vectorstores.faiss import FAISS
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
import os
import json
import requests

load_dotenv(find_dotenv())
from langchain.globals import set_debug


class Researcher:
    def __init__(self) -> None:
        self.serper_api_key = os.getenv('SERPER_KEY')
        self.groq_api_key = os.getenv('GROQ_KEY')
        self.prompt_template = PromptTemplate(
            template=PROMPT_TEMPLATE,
            input_variables=INPUT_VARIABLES,
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            seperators=SEPERATORS
        )
        self.hfembeddings = HuggingFaceBgeEmbeddings(
            model_name = EMBEDDER,
            model_kwargs = {'device': 'cpu'}
            )
        self.llm = ChatGroq(model_name='mixtral-8x7b32768', groq_api_key=self.groq_api_key)

    def search_articles(self, query):
        url = 'https://google.serper.dev/search'
        data = json.dumps({'q': query})
        headers = {'X-API-KEY': self.serper_api_key, 'Content-Type': 'application/json'}
        response = requests.request("POST", url, headers=headers, data=data)

        return response.json()


    def get_urls(self, articles):
        urls = []
        try:
            urls.append(articles['answerBox']['link'])
        except:
            pass
        for i in range(0, min(3, len(len(articles['organic'])))):
            urls.append(articles['organic'][i]['link'])
        return urls

    def get_content_from_url(self, urls: list):
        loader = UnstructuredURLLoader(urls=urls)
        return loader.load()
    
    def create_vector_store(self, research_content):
        self.db = FAISS.from_documents(documents=self.text_splitter.split_documents(research_content))
        embedding=self.hfembeddings
    def research(self, user_query:str):
        search_articles = self.search_articles(user_query)
        urls = self.get_urls(search_articles)
        research_content = self.get_content_from_url(urls)
        self.create_vector_store(research_content)