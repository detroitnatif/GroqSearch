import os
import streamlit as st
from dotenv import load_dotenv, find_dotenv
from langchain_groq import ChatGroq
from langchain import hub
from langchain.agents import load_tools, AgentExecutor, create_react_agent
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
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

    def invoke_agent(self, prompt):
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []
        
        # Building the context from the conversation history
        context = [entry['user'] for entry in st.session_state.conversation_history if 'user' in entry]
        context += [entry['agent'] for entry in st.session_state.conversation_history if 'agent' in entry]
        
        # Concatenating the user's current question with the context
        context_str = " ".join(context + [prompt])  # Add the current prompt to the context
        
        # Invoke the agent with the concatenated context
        response = self.agent_executor.invoke({"input": prompt, "context": context_str}, {"callbacks": [self.st_callback]})
        
        # Update the conversation history
        st.session_state.conversation_history.append({'user': prompt})
        
        if response and "output" in response:
            st.session_state.conversation_history.append({'agent': response["output"]})
            return response["output"]
        else:
            return "An error occurred, or the response was not in the expected format."

    def run(self):
        if 'conversation_history' in st.session_state:
            for interaction in st.session_state.conversation_history:
                if 'user' in interaction:
                    st.text_area("User", value=interaction['user'], disabled=True, height=100)
                if 'agent' in interaction:
                    st.text_area("Assistant", value=interaction['agent'], disabled=True, height=100)

        user_input = st.text_input("Ask me anything:", key="new_prompt")

        submit_button = st.button("Submit")

        if submit_button:
            response_output = self.invoke_agent(user_input)
            # Trigger a rerun of the app to refresh and display the latest conversation
            st.rerun()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = LangchainSearchApp()
    app.run()
