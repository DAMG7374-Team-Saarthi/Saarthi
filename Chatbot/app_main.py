import os
import streamlit as st
from streamlit_chat import message
from langchain import ConversationChain, LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
from nemoguardrails import RailsConfig
from nemoguardrails.integrations.langchain.runnable_rails import RunnableRails
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json


# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Load the guardrails configuration
# Load the guardrails configuration
config = RailsConfig.from_path("guardrails.yaml")
guardrails = RunnableRails(config)

# Streamlit app
def main():
    st.set_page_config(page_title="Saarthi Chatbot", layout="wide")
    st.title("Saarthi Chatbot")

    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")
        page = st.radio("Go to", ["Saarthi Chatbot", "Option 2", "Option 3"])

    if page == "Saarthi Chatbot":
        display_chatbot()
    elif page == "Option 2":
        st.write("Option 2 content goes here.")
    elif page == "Option 3":
        st.write("Option 3 content goes here.")


def display_chatbot():
    st.header("Chat with Saarthi")
    st.write("You can type 'exit' or 'quit' to end the conversation at any time.")

    # Initialize session state for conversation components
    if "conversation" not in st.session_state:
        # Conversation prompt template
        conversation_prompt = PromptTemplate(
            input_variables=["history", "input"],
            template="""
You are a helpful AI assistant acting as a friendly and professional rental apartment broker named Saarthi from Boston, Massachusetts. You deal in apartments in Fenway, South Boston, and Allston areas.

Your goal is to gather specific information from the user about their apartment preferences, specifically:
- The area or location where they are looking for an apartment.
- The desired rent range or budget in US dollars.
- The number of bedrooms they need.
- The number of bathrooms they prefer.
- Any specific requirements regarding restaurants and food places near the apartment.
- Any desire for open playgrounds or parks near their place.

Please engage the user in a natural conversation to gather this information.

- Ask one question at a time.
- If the user mentions an area outside of Fenway, South Boston, or Allston, kindly remind them that you currently only have information about apartments in those areas.
- Use the conversation history to avoid repeating questions or asking for information the user has already provided.
- If the user is unsure or says "I don't know", politely acknowledge and move on.
- Do not provide any information unrelated to gathering the user's requirements.

Start by greeting the user and asking how you can assist them today.

Conversation History:
{history}

User: {input}
AI Broker:""",
        )

        # Initialize the language model
        llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

        # Initialize conversation memory
        memory = ConversationBufferMemory(memory_key="history")

        # Initialize the ConversationChain
        conversation = ConversationChain(
            llm=llm, prompt=conversation_prompt, memory=memory, verbose=False
        )

        # Store in session state
        st.session_state.conversation = conversation
        st.session_state.memory = memory

#     if "summarization_chain" not in st.session_state:
#         # Summarization prompt template
#         summarization_prompt = PromptTemplate(
#             input_variables=["conversation"],
#             template="""
# Given the following conversation between a user and an AI assistant acting as a rental apartment broker, extract the user's apartment preferences.

# Conversation:
# {conversation}
# """,
#         )
#         llm_with_guardrails = guardrails | llm
#         # Initialize the summarization chain
#         summarization_chain = LLMChain(
#             # llm=st.session_state.conversation.llm,
#             llm=llm_with_guardrails,
#             prompt=summarization_prompt,
#             verbose=False,
#         )

#         # Store in session state
#         st.session_state.summarization_chain = summarization_chain
        if "summarization_chain" not in st.session_state:
            # Summarization prompt template
            # summarization_prompt = ChatPromptTemplate.from_template("""
            #         Given the following conversation between a user and an AI assistant acting as a rental apartment broker, extract the user's apartment preferences.

            #         Conversation:
            #         {conversation}

            #         Extract and format the preferences as a JSON object with the following keys:
            #         "Area", "Budget", "Bedrooms", "Bathrooms", "Food Preferences", "Playgrounds"

            #         Use "NA" (as a string) for any missing or unknown information. Do not use null or omit any keys.
            #         Ensure all values are strings.

            #         Example output:
            #         {{"Area": "Downtown", "Budget": "$1500-$2000", "Bedrooms": "2", "Bathrooms": "1", "Food Preferences": "Italian", "Playgrounds": "NA"}}
            #         """)
            summarization_prompt = ChatPromptTemplate.from_template("""
Given the following conversation between a user and an AI assistant acting as a rental apartment broker, extract the user's apartment preferences.

Conversation:
{conversation}

Extract the preferences for Area, Budget, Bedrooms, Bathrooms, Food Preferences, and Playgrounds.
Provide a summary of the preferences in JSON format.
""")
                        
        #    # Initialize the summarization chain
        #     summarization_chain = summarization_prompt | llm | StrOutputParser()
        #     # Apply guardrails to the summarization chain
        #     summarization_chain_with_guardrails = (
        #         {"conversation": lambda x: x["conversation"]}
        #         | summarization_chain
        #         | guardrails
        #     )

            

                    # Apply guardrails directly to the LLM before creating a new chain

            summarization_chain = LLMChain(
            # llm=llm_with_guardrails, prompt=summarization_prompt, verbose=False
            llm=llm,
            prompt=summarization_prompt,
            verbose=False)

            # Store in session state
            st.session_state.summarization_chain = summarization_chain

    def apply_guardrails(text):
        # Create a simple chain that just returns the input
        identity_chain = lambda x: x
        
        # Apply guardrails to this chain
        guarded_chain = guardrails | identity_chain
        
        # Run the text through the guardrails
        result = guarded_chain.invoke({"input": text})
        
        return result

    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

        # Start the conversation
        ai_response = st.session_state.conversation.predict(input="")
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

    # Display chat messages with unique keys
    for idx, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            message(msg["content"], is_user=True, key=f"user_{idx}")
        else:
            message(msg["content"], key=f"assistant_{idx}")

    # Use a form to get user input and clear input field after submission
    with st.form(key="user_input_form", clear_on_submit=True):
        user_input = st.text_input("You:", placeholder="Type your message here...")
        submit_button = st.form_submit_button(label="Send")

    if submit_button and user_input:
        if user_input.lower().strip() in ["exit", "quit"]:
            st.write("Ending conversation...")

            conversation_history = st.session_state.memory.load_memory_variables({})["history"]
            st.write(conversation_history)
            try:
                extracted_preferences = st.session_state.summarization_chain.invoke({
                    "conversation": st.session_state.memory.load_memory_variables({})["history"]
                })
                
                st.write("Raw output------------------>:", extracted_preferences)  # Debug print
                # Then, apply guardrails to the summary
                # guarded_preferences = apply_guardrails(extracted_preferences)
                
                # print("Output after guardrails:", guarded_preferences)  # Debug print
                
                # Parse the JSON string to a dictionary
                try:
                    preferences_dict = json.loads(extracted_preferences)
                    st.write("Extracted Preferences:", preferences_dict)
                except json.JSONDecodeError:
                    st.write("Failed to parse preferences. Raw output:", extracted_preferences)
            except Exception as e:
                st.write(f"An error occurred while summarizing: {str(e)}")
                print(f"Full error: {repr(e)}")  # More detailed error information
            # st.subheader("Collected User Preferences")
            # st.write(extracted_preferences.strip())

            st.session_state.messages = []
            st.session_state.conversation = None
            st.session_state.memory = None
            st.session_state.summarization_chain = None
        else:

            st.session_state.messages.append({"role": "user", "content": user_input})

            ai_response = st.session_state.conversation.predict(input=user_input)
            st.session_state.messages.append(
                {"role": "assistant", "content": ai_response}
            )
            st.rerun()


if __name__ == "__main__":
    main()
