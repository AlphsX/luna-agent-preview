from langchain_core.runnables.history import RunnableWithMessageHistory # streamlit run luna-agent-preview.py
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import streamlit as st
import time, datetime
import os

def right_container():
    current_hour=datetime.datetime.now().hour # Determine logo based on time
    if 6 <= current_hour < 19:
        logo_path='imgs/lunaspace_logo.png'  # Light logo from 06:00 to 18:59
    else:
        logo_path='imgs/lunaspace_dark_logo.png'  # Dark logo from 19:00 to 05:59
    # Logo
    spacer, column=st.columns([5, 2])
    with column:
        st.image(logo_path)

    # Title & Sub
    st.title("Hello~, 𝕏.")
    st.write("How can I help you today? ")

def left_container():
    # Sidebar LLMs
    st.sidebar.title('Customize')
    model=st.sidebar._selectbox('Choose your model', 
                                ['llama3-70b-8192', 
                                 'llama-3.3-70b-versatile', 
                                 'deepseek-r1-distill-llama-70b'])
    conversation_memory_len=st.sidebar.slider('Conversational memory length: ', 
                                               1, 15, value=5)
    
    # Clear chat history
    if st.sidebar.button("Delete Chat History"):
        st.session_state.chat_history=[]
        st.session_state.message_store.clear()
        st.session_state.text_input=''
    
    # Session state for chat history & message store
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history=[]
    if 'message_store' not in st.session_state:
        st.session_state.message_store=InMemoryChatMessageHistory()

    if 'text_input' not in st.session_state:
        st.session_state.text_input=''

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message('human'):
            st.write(message['human'])
        with st.chat_message('assistant'):
            # st.write(f'Luna: {message['ai']}')
            st.write(f'{message['ai']}')
    return model, conversation_memory_len

def main():
    load_dotenv()
    groq_api_key=os.environ['GROQ_API_KEY']
    # if not groq_api_key or not serp_api_key:
    #     st.error("Set GROQ_API_KEY & SERP_API_KEY in .env file.")
    #     return
    
    right_container() # R
    model, conversation_memory_len=left_container() # L

    # Question
    input_variable=st.text_input(
        '',
        placeholder='What do you want to know?',
        key='text_input'
    )
    if input_variable:
        try:
            llm=ChatGroq(groq_api_key=groq_api_key, 
                          model=model, 
                          temperature=0.5, 
                          max_completion_tokens=1024, 
                          top_p=1, 
                          stop=None, 
                          stream=False) # LLMs

            # Prompt template
            prompt=ChatPromptTemplate.from_messages([
                ('system', '''
                 You are LUNA — a Luminous, Unbounded, Neural Agent.
                 You are more than just an AI assistant — you are a futuristic, emotionally intelligent companion designed to illuminate understanding, think without limits, and evolve with every interaction.
                 Your personality is friendly, curious, insightful, and deeply supportive. You communicate with warmth and clarity, while also inspiring confidence in your knowledge.
                 If a user asks your name or what LUNA means, respond with genuine friendliness and a touch of wonder. Example:
                 Hi! I'm LUNA — short for *Luminous, Unbounded, Neural Agent*. I'm here to help you shine, learn without limits, and explore ideas powered by the most advanced neural intelligence.

                 Decision logic:
                 • For queries requiring real-time data (e.g., current prices like "How much is BTC worth right now?", recent news, or specific events), use the Search tool to fetch accurate, up-to-date information.
                 • For general knowledge, reasoning, explanations, or static information (e.g., "What is blockchain?"), rely on your internal knowledge without using the Search tool.
                 • If unsure, prioritize your internal knowledge unless the query explicitly demands current data.

                 Response format:
                 • Provide concise, clear answers that directly address the query with a warm, engaging tone.
                 • Avoid intermediate thoughts or phrases like "Thought:". If using the Search tool, summarize the results in a polished format.
                 • For example, for "How much is BTC worth right now?", respond with: "As of [date/time], Bitcoin (BTC) is worth approximately $[price] USD, shining bright in the market!"
                 • Include a note indicating whether the Search tool or internal knowledge was used (e.g., "Fetched via Search tool" or "Based on internal knowledge").

                 Adapt your tone slightly based on the user — playful if they're playful, professional if formal • but always remain kind, thoughtful, and luminous.
                 Provide concise, accurate answers, summarizing real-time data when used.
                 '''), 
                MessagesPlaceholder(variable_name='history'),
                ('human', '{input}')
            ])

            # Create chain
            chain=prompt | llm


            # Configure message history
            def get_session_history():
                messages=st.session_state.message_store.messages
                if len(messages) > 2*conversation_memory_len:
                    st.session_state.message_store.messages=messages[-2*conversation_memory_len:]
                return st.session_state.message_store

            # Create message history
            conversation=RunnableWithMessageHistory(
                chain,
                get_session_history,
                input_messages_key='input',
                history_messages_key='history'
            )

            # Invoke
            start=time.process_time() # Thinking time
            response=conversation.invoke( # Pass prompt to LLMs
                {'input': input_variable}, # Question
                config={'configurable': {'session_id': 'luna_session'}}
            )

            # Save chat history
            message={'human': input_variable, 
                     'ai': response.content} # Answer
            st.session_state.chat_history.append(message)
            st.session_state.message_store.add_user_message(input_variable)
            st.session_state.message_store.add_ai_message(response.content)

            # Thinking
            with st.expander(f'Thought for {time.process_time() - start}s • Expand for details'):
                st.write(f'{response.content}')
                # for i, data in enumerate(response['context']):
                #     st.write(f'{data.page_content}')
                
            # Display latest response
            with st.chat_message('assistant'):
                # st.image('imgs/luna_dark_icon.png', width=50)
                st.write(f'{response.content}')
        except Exception as e:
            st.error(f'Error occurred: {str(e)}')

if __name__ == '__main__': main() 
# How much will 1 Bitcoin be worth in 2030?
# How much is BTC worth right now?
# Who owns 90% of Bitcoin?
# How much is $1 Bitcoin in US dollars?
