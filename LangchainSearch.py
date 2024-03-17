# import os
# from dotenv import load_dotenv, find_dotenv
# from langchain.llms import OpenAI
# from langchain import hub
# from langchain.agents import load_tools, initialize_agent, AgentType, AgentExecutor, create_react_agent
# import streamlit as st
# from langchain_groq import ChatGroq
# from langchain_community.callbacks.streamlit import (
#     StreamlitCallbackHandler,
# )

# load_dotenv(find_dotenv())

# groq_api_key = os.getenv("GROQ_API_KEY")

# # llm = OpenAI(temperature=0.5, streaming=True, openai_api_key=os.getenv('OPENAI_API_KEY'))
# llm = ChatGroq(temperature=0.5, model_name="mixtral-8x7b-32768", groq_api_key=groq_api_key)

# tools = load_tools(["ddg-search"])
# prompt = hub.pull("hwchase17/react")
# agent = create_react_agent(llm, tools, prompt)
# agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
# st_callback = StreamlitCallbackHandler(st.container())


# # if prompt := st.chat_input():
# #     st.chat_message('user').write(prompt)
# #     with st.chat_message("assisstant"):
# #         st.write('thinking')
# #         st_callback = StreamlitCallbackHandler(st.container())
# #         response = agent.run(prompt, callbacks=[st_callback])
# #         st.write(response)

# if prompt := st.chat_input():
#     st.chat_message("user").write(prompt)
#     with st.chat_message("assistant"):
#         st_callback = StreamlitCallbackHandler(st.container())
#         response = agent_executor.invoke(
#             {"input": prompt}, {"callbacks": [st_callback]}
#         )
#         st.write(response["output"])

import os
import streamlit as st
from dotenv import load_dotenv, find_dotenv
from langchain.llms import OpenAI
from langchain_groq import ChatGroq
from langchain import hub
from langchain.agents import load_tools, AgentExecutor, create_react_agent
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
import threading
import asyncio

class LangchainSearchApp:
    def __init__(self):
        load_dotenv(find_dotenv())
        groq_api_key = os.getenv("GROQ_API_KEY")
        self.llm = ChatGroq(temperature=0.5, model_name="mixtral-8x7b-32768", groq_api_key=groq_api_key)
        self.tools = load_tools(["ddg-search"])
        self.prompt = hub.pull("hwchase17/react")
        self.agent = create_react_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
        self.st_callback = StreamlitCallbackHandler(st.container())

    def run_async_code(self, async_func, *args):
        """
        Run an asynchronous function async_func, passing it *args, in a separate thread
        and return the result.
        """
        def thread_func(async_func, args, loop, results):
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.collect_result(async_func, args, results))
        
        loop = asyncio.new_event_loop()
        results = []
        thread = threading.Thread(target=thread_func, args=(async_func, args, loop, results))
        thread.start()
        thread.join()
        return results[0] if results else None

    async def collect_result(self, async_func, args, results):
        result = await async_func(*args)
        results.append(result)

    async def invoke_agent_async(self, prompt):
    # Directly await and return the response for debugging
        response = await self.agent_executor.invoke({"input": prompt}, {"callbacks": [self.st_callback]})
        print("Response received:", response)  # Temporary logging
        return response


    def invoke_agent(self, prompt):
    # Synchronously invoke the agent_executor without awaiting.
        response = self.agent_executor.invoke({"input": prompt}, {"callbacks": [self.st_callback]})
        return response


    def run(self):
        if prompt := st.chat_input():
            st.chat_message("user").write(prompt)
            with st.chat_message("assistant"):
                response = self.invoke_agent(prompt)
                if response and "output" in response:
                    st.write(response["output"])
                else:
                # This condition handles cases where the response does not contain the expected output
                    st.write("An error occurred, or the response was not in the expected format.")


if __name__ == "__main__":

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    app = LangchainSearchApp()
    app.run()

