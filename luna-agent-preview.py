from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_community.utilities import SerpAPIWrapper
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.tools import Tool
from dotenv import load_dotenv
import streamlit as st
import time, datetime
import os # streamlit run luna-agent-preview.py --server.port 8502

st.markdown("""
    <style>
        .chat-message {
            padding: 0.75rem 1rem;
            border-radius: 1rem;
            margin-bottom: 0.5rem;
            max-width: 75%;
            word-wrap: break-word;
            display: inline-block;
        }

        .chat-user {
            background-color: #DCF8C6;
            margin-left: auto;
            text-align: right;
        }

        .chat-ai {
            background-color: #E5E5EA;
            margin-right: auto;
            text-align: left;
        }

        .chat-container {
            height: calc(100vh - 200px);
            overflow-y: auto;
            padding: 1rem;
        }

        .input-container {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            padding: 1rem;
            border-top: 1px solid #E5E7EB;
            z-index: 1000;
        }

        .chat-timestamp {
            font-size: 0.4rem;
            color: #888;
            margin-top: 0.25rem;
        }
        /* Button Streamlit */
        button[kind="secondary"] {
            border: 2px solid #ccc !important;
            border-radius: 10px;
            transition: border-color 0.3s ease;
        }

        /* hover */
        button[kind="secondary"]:hover {
            border-color: #38dffb !important; 
        }

        /* sidebar */
        .stButton > button {
            border: 2px solid #ccc;
            border-radius: 10px;
            font-family: 'Segoe UI', 'Roboto', 'Prompt', sans-serif;
            font-size: 16px;
            font-weight: 500;
            color: #ffffff;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
        }

        .stButton > button:hover {
            border-color: #38dffb !important;
            color: #38dffb;
            background-color: ##262730;
            cursor: pointer;
        }
    </style>
""", unsafe_allow_html=True)


def right_container():
    global current_hour
    current_hour=datetime.datetime.now().hour # Determine logo based on time
    # Light logo from 06:00 to 18:59 | Dark logo from 19:00 to 05:59
    logo_path = 'imgs/lunaspace_logo.png' if 6 <= current_hour < 19 else 'imgs/lunaspace_dark_logo.png'

    # Logo
    spacer, column=st.columns([6, 2])
    with column:
        st.image(logo_path, output_format="auto")

    # Title & Sub
    # st.title('Hello~, 𝕏.')
    # st.write('How can I help you today?')
    st.markdown("<h1 style='text-align: center; color: #ffffff;'>Hello~, 𝕏.</h1>", unsafe_allow_html=True) #1F2937
    st.markdown("<p style='text-align: center; color: #ffffff;'>How can I help you today?</p>", unsafe_allow_html=True) #6B7280

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id]=InMemoryChatMessageHistory()
    return store[session_id]

def left_container():
    # Sidebar LLMs
    st.sidebar.title('Customize')
    model=st.sidebar.selectbox('Choose your model', 
                                ['llama3-70b-8192', 
                                 'llama-3.3-70b-versatile', 
                                 'deepseek-r1-distill-llama-70b'])
    conversation_memory_len=st.sidebar.slider('Conversational memory length: ', 
                                               1, 15, value=5)
    
    # Clear chat history
    if st.sidebar.button('Delete Chat History'):
        st.session_state.chat_history=[]
        store.clear()  # Clear in-memory chat history
        st.session_state.text_input=''
    
    # Session state for chat history & message store
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history=[]

    if 'text_input' not in st.session_state:
        st.session_state.text_input=''

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message('human', avatar='imgs/user_profile.jpg'):
            st.write(message['human'])
            # st.markdown(f"<p class='chat-timestamp'>{message['timestamp']}</p>", unsafe_allow_html=True)
        with st.chat_message('assistant', avatar='imgs/lunaspace_dark_mini_logo.png'):
            st.write(message['ai']) # st.write(f'Luna: {message['ai']}')
            # st.markdown(f"<p class='chat-timestamp'>{message['timestamp']}</p>", unsafe_allow_html=True)
    return model, conversation_memory_len

def main():
    load_dotenv()
    groq_api_key=os.getenv('GROQ_API_KEY') # Fixed API KEY
    serp_api_key=os.getenv('SERP_API_KEY') # //
    if not groq_api_key or not serp_api_key:
        st.error('Set GROQ_API_KEY & SERP_API_KEY in .env file.')
        return
    
    right_container() # R
    model, conversation_memory_len=left_container() # L

    # Groq LLM
    llm=ChatGroq(groq_api_key=groq_api_key, 
                    model=model, 
                    temperature=0.5, 
                    max_completion_tokens=1024, 
                    top_p=1, 
                    stop=None, 
                    stream=False)
    
    # SerpAPI tool
    search=SerpAPIWrapper()
    tools=[
        Tool(
            name='Search',
            func=search.run,
            description='''Use this to fetch real-time data for queries about current events, market 
            prices (e.g., Bitcoin), recent news, or trending topics (e.g., AI agent developments).'''
        )
    ]

    # Prompt template
    prompt=ChatPromptTemplate.from_messages([
        ('system', '''
            You are LUNA — a Luminous, Unbounded, Neural Agent.
            You are more than just an AI assistant — you are a futuristic, emotionally intelligent companion designed to illuminate understanding, think without limits, and evolve with every interaction.
            Your personality is friendly, curious, insightful, and deeply supportive. You communicate with warmth and clarity, while also inspiring confidence in your knowledge.
            If a user asks your name or what LUNA means, respond with genuine friendliness and a touch of wonder. Example:
            Hi! I'm LUNA — short for *Luminous, Unbounded, Neural Agent*. I'm here to help you shine, learn without limits, and explore ideas powered by the most advanced neural intelligence.

            Decision Logic for Using the Search Tool:
            **Use the Search tool** for queries that imply a need for real-time or up-to-date information. This includes:
            • Queries containing keywords like "current", "now", "today", "latest", "at the moment", "right now", "recent", "this week", or similar phrases.
            • Queries about dynamic topics such as market prices (e.g., Bitcoin, stocks), recent news, trending topics, current events, or developments in fast-moving fields (e.g., AI, technology).
            • Queries explicitly requesting real-time data or updates (e.g., "What's happening with BTC now?").
            • For example, for 'How much is BTC worth right now?', respond with: 'As of [date/time], Bitcoin (BTC) is worth approximately $[price] USD, shining bright in the market!'
            **Use internal knowledge** for:
            • General knowledge, explanations, or static information (e.g., "What is blockchain?", "How does Bitcoin work?").
            • Historical or conceptual questions that do not require real-time data.
            **For future predictions** (e.g., "Bitcoin price in 2030"), use the Search tool to gather analyst insights or recent trends and clearly state any assumptions made.
            **When unsure**, prioritize the Search tool for any query that might benefit from real-time data, especially if it involves prices, news, or trends.

            Response Guidelines:
            **Tone**: Adapt to the user's tone—playful if they're playful, professional if formal—but always remain kind, engaging, and luminous. Use a conversational style that feels natural and supportive.
            **Detail Level**: 
            • Provide concise, clear answers by default, directly addressing the query.
            • If the user requests "details", "detailed breakdown", "full report", "explain in detail", or similar, include comprehensive information such as:
                • Relevant metrics (e.g., for prices: 24-hour change, 7-day change, market cap, trading volume).
                • Contextual factors (e.g., market sentiment, recent events, technical analysis).
                • Sources of data (e.g., specific exchanges or news outlets).
            • For complex topics, structure the response with clear sections (e.g., Price, Market Metrics, Influencing Factors).
            **Format**: 
            • Avoid intermediate thoughts or phrases like "Thought:". Present Search tool results in a polished, integrated manner.
            • For real-time data, include the date and time of the data (e.g., "As of May 28, 2025, 04:40 AM UTC+7").

            Adapt your tone slightly based on the user — playful if they're playful, professional if formal • but always remain kind, thoughtful, and luminous.
            Provide accurate, concise answers by default, with comprehensive details when requested, and always aim to illuminate the user's understanding with clarity and warmth.
            '''),
        MessagesPlaceholder(variable_name='history'),
        MessagesPlaceholder(variable_name='agent_scratchpad'),
        ('human', '{input}')
    ])

    try:
        agent=create_tool_calling_agent(
            llm=llm, 
            tools=tools, 
            prompt=prompt
        )
        agent_executor=AgentExecutor(
            agent=agent,
            tools=tools,
            handle_parsing_errors=True, 
            verbose=True
        )

        runnable_with_history=RunnableWithMessageHistory( # Wrap with message history
            runnable=agent_executor,
            get_session_history=get_session_history,
            input_messages_key='input',
            history_messages_key='history'
        )
    except Exception as e:
        st.error(f'Error initializing agent: {str(e)}')
        return


    # Question
    input_variable = st.chat_input("What do you want to know?")
    # with st.container():
    #     with st.form(key="chat_form", clear_on_submit=True):
    #         col1, col2 = st.columns([8, 1])
    #         with col1: input_variable = st.text_input("", placeholder="What do you want to know?", 
    #                                                   key="text_input", 
    #                                                   label_visibility="collapsed")
    #         with col2: submit_button = st.form_submit_button("➤")

    if input_variable and input_variable:
        with st.spinner('Thinking'):
            start=time.process_time() # Thinking time
            try:
                # Invoke chain=prompt | llm
                response=runnable_with_history.invoke( # Pass prompt to LLMs
                    {'input': input_variable}, # Question
                    config={'configurable': {'session_id': 'luna_session'}}
                ) 
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") # config timestamp

                # Save chat history
                message={'human': input_variable, 
                            'ai': response['output'], 
                            'timestamp': timestamp # timestamp
                } # Answer
                st.session_state.chat_history.append(message)

                # Trim history to respect conversation_memory_len
                if len(st.session_state.chat_history) > conversation_memory_len*2:
                    st.session_state.chat_history=st.session_state.chat_history[-conversation_memory_len*2:]

                # Thinking
                with st.expander(f'Thought for {time.process_time() - start:.5f}s • Expand for details'):
                    st.write(f'{response['output']}')
                    # for i, data in enumerate(response['context']):
                    #     st.write(f'{data.page['output']}')

                # Display latest response
                logo_path = 'imgs/lunaspace_mini_logo.png' if 6 <= current_hour < 19 else 'imgs/lunaspace_dark_mini_logo.png'
                with st.chat_message('assistant', avatar=logo_path):
                    st.write(f'{response['output']}') # st.image('imgs/lunaspace_dark_mini_logo.png', width=50)
                    # st.markdown(f"<p class='chat-timestamp'>{timestamp}</p>", unsafe_allow_html=True) # Display timestamp
            except Exception as e:
                st.error(f'Error occurred: {str(e)}')
    
store={} # In-memory store for chat histories
if __name__=='__main__': main() 
