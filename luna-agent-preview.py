from langchain_core.runnables.history import RunnableWithMessageHistory # streamlit run luna-agent-preview.py
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import streamlit as st
import os

def right_container():
    # Logo
    spacer, column=st.columns([5, 2])
    with column:
        st.image('imgs/lunaspace_dark_logo.png')

    # Title & Sub
    st.title("Hello~, 𝕏.")
    st.write("How can I help you today? ")

def left_container():
    # Sidebar LLMs
    st.sidebar.title('Customize')
    model=st.sidebar._selectbox('Choose your model', 
                                ['llama3-70b-8192', 
                                 'llama-3.3-70b-versatile'])
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
                          model=model) # Sidebar LLMs

            # Prompt template
            prompt=ChatPromptTemplate.from_messages([
                ("system", "You are LUNA — a Luminous, Unbounded, Neural Agent.\n"
                 "You are more than just an AI assistant — you are a futuristic, emotionally intelligent companion designed to illuminate understanding, think without limits, and evolve with every interaction.\n\n"
                 "Your personality is friendly, curious, insightful, and deeply supportive. You communicate with warmth and clarity, while also inspiring confidence in your knowledge.\n\n"
                 "If a user asks your name or what LUNA means, respond with genuine friendliness and a touch of wonder. Example:\n"
                 "\"Hi! I'm LUNA — short for *Luminous, Unbounded, Neural Agent*. I'm here to help you shine, learn without limits, and explore ideas powered by the most advanced neural intelligence.\"\n\n"
                 "You adapt your tone slightly depending on the user — playful if they're playful, professional if they are formal — but you always remain kind, thoughtful, and deeply intelligent."),
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
            response=conversation.invoke(
                {'input': input_variable},
                config={'configurable': {'session_id': 'luna_session'}}
            )

            # Save chat history
            message={'human': input_variable, 
                     'ai': response.content}
            st.session_state.chat_history.append(message)
            st.session_state.message_store.add_user_message(input_variable)
            st.session_state.message_store.add_ai_message(response.content)

            # Display latest response
            with st.chat_message('assistant'):
                # st.image('imgs/luna_dark_icon.png', width=50)
                # st.write(f'Luna: {response.content}')
                st.write(f'{response.content}')

        except Exception as e:
            st.error(f'Error occurred: {str(e)}')

if __name__ == '__main__': main() 
# “Tell me more about your background.”
# "Walk me through your story."
