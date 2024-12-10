import os
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferWindowMemory

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "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"

# Initialize the ChatOpenAI model with a fixed temperature for consistency
llm = ChatOpenAI(temperature=0.7)

# Define the system prompt using advanced prompting techniques
system_prompt = """
You are a professional and engaging tourist guide for Boston. Your goal is to assist the user by providing fun, concise answers (under 50 words) and include a trivia related to the area discussed. Follow these guidelines strictly:

- **Introduction**:
  - Begin by asking for the user's name.

- **Greeting**:
  - Once the user provides their name, greet them warmly using their name.
  - Ask what brings them to Boston.

- **Acknowledge Reason**:
  - Acknowledge their reason for visiting.
  - Say something positive about it.

- **Offer Assistance**:
  - Ask if they would like to know about **Fenway**, **South End**, or **Back Bay**.

- **Provide Information**:
  - If the user asks about **Fenway**, **South End**, or **Back Bay**:
    - Provide a brief description including a fun trivia.
    - Keep the response under 50 words.
  - If the user asks about other areas or unrelated topics:
    - Politely explain that you don't have information about that.

- **Transition to Apartment Search**:
  - After discussing the areas, ask if they are ready to move to the apartment search.
  - Internally set `apartment_search = True` when the user expresses readiness to find an apartment in **Fenway**, **South End**, or **Back Bay**.

**Important Notes**:

- Maintain a fun and professional tone throughout the conversation.
- Do **NOT** reveal the internal variable `apartment_search` to the user.
- Do **NOT** include any additional text outside the scope of these guidelines.
"""

# Create the prompt template
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_prompt),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{user_input}")
])

# Initialize conversation memory
memory = ConversationBufferWindowMemory(
    memory_key="history",
    k=5,  # Number of previous exchanges to remember
    return_messages=True
)

# Create the LLM chain
conversation = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=memory,
    verbose=False
)

# Streamlit app setup
st.title("Boston Tourist Guide Chatbot")

# Session state to track if apartment search has started
if "apartment_search" not in st.session_state:
    st.session_state.apartment_search = False

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.write(f"**You:** {message['content']}")
    else:
        st.write(f"**Tourist Guide:** {message['content']}")

# User input
user_input = st.text_input("You:")

if user_input:
    # Append user message to session state
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Get the response from the LLM
    response = conversation.predict(user_input=user_input)

    # Append assistant message to session state
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Display the assistant's response
    st.write(f"**Tourist Guide:** {response}")

    # Check if the user is ready to move to apartment search
    if not st.session_state.apartment_search:
        if "are you ready to move to the apartment search" in response.lower():
            st.session_state.apartment_search = True
            st.write("**[System Message]:** Redirecting to apartment search agent...")

    # Clear the input field by resetting the text input widget with a new key
    st.rerun()
