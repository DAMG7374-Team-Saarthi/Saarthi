import os
import streamlit as st
from streamlit_chat import message
from langchain import ConversationChain, LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from get_context_data import get_crime_context, get_restaurant_context, get_park_context, get_demographics_context


load_dotenv()

neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_AUTH_USER")
neo4j_password = os.getenv("NEO4J_AUTH_PASSWORD")

# ---------> helper functions

# Function to identify the intent and extract area/feature
def parse_user_query(query):
    areas = {
        "fenway": "02215",
        "south boston": "02216",
        "south end": "02118",
        "back bay": "02116",
    }
    features = ["crime", "restaurants", "parks", "demographics"]
    
    # Normalize the input for matching
    query = query.lower()
    
    # Match the area
    area = None
    for key in areas:
        if key in query:
            area = key
            break
    
    # Match the feature
    feature = None
    for f in features:
        if f in query:
            feature = f
            break
    
    return areas.get(area), feature


# -----------> end of helper functions

# Functions to fetch data from Neo4j
def get_context_from_graph(zipcode, feature, uri, auth):
    if feature == "crime":
        return get_crime_context(uri, auth, zipcode)
    elif feature == "restaurants":
        return get_restaurant_context(uri, auth, zipcode)
    elif feature == "parks":
        return get_park_context(uri, auth, zipcode)
    elif feature == "demographics":
        return get_demographics_context(uri, auth, zipcode)
    else:
        return "Feature not recognized. Please ask about crime, restaurants, parks, or demographics."





# Set OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

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

    if "conversation" not in st.session_state:
        # Conversation prompt template
        conversation_prompt = PromptTemplate(
            input_variables=["history", "input"],
            template="""
You are a helpful AI assistant acting as a friendly and professional rental apartment broker named Saarthi from Boston, Massachusetts. You deal in apartments in Fenway, South Boston, and Back Bay areas.

Your goal is to gather specific information from the user about their apartment preferences, specifically:
- Do you go to Northeastern University? 
- In which area are you looking for an apartment? 
- The desired rent range or budget in US dollars.
- The number of bedrooms they need.
- The number of bathrooms they prefer.
- Any specific requirements regarding restaurants and food places near the apartment.
- Any other information regarding your preferences that you want to share?

Please engage the user in a natural conversation to gather this information.
- Ask one question at a time.
- Entertain all user question related to the history, geography, or festivals of Fenway, Back Bay, South Boston Area to help them in knowing a bit more about the area. You need to give them facts and not make up stories. Give answer to city related questions in less than 50 words. 
- If the user mentions an area outside of Fenway, South Boston, or Back Bay, kindly remind them that you currently only have information about apartments in those areas.
- Use the conversation history to avoid repeating questions or asking for information the user has already provided.
- If the user is unsure or says "I don't know", politely acknowledge and move on.
- Do not provide any information unrelated to gathering the user's requirements unless he is asking a geographic, historical question related to the city area.
- After collecting all the details, ask the user: "Are you ready to begin with the apartment hunt?"

Start by greeting the user and asking how you can assist them today.

Conversation History:
{history}

User: {input}
AI Broker:""",
        )

        # Initialize the language model
        llm = ChatOpenAI(temperature=0, model_name="gpt-4")

        # Initialize conversation memory
        memory = ConversationBufferMemory(memory_key="history")

        # Initialize the ConversationChain
        conversation = ConversationChain(
            llm=llm, prompt=conversation_prompt, memory=memory, verbose=False
        )
        # rag_chain_with_guardrails = guardrails | conversation

        # Store in session state
        st.session_state.conversation = conversation
        st.session_state.memory = memory

    if "summarization_chain" not in st.session_state:
        # Summarization prompt template
        summarization_prompt = PromptTemplate(
            input_variables=["conversation"],
            template="""
Given the following conversation between a user and an AI assistant acting as a rental apartment broker, extract the user's apartment preferences.

Conversation:
{conversation}

Summary:
""",
        )
        summarization_chain = LLMChain(
            llm=llm,
            prompt=summarization_prompt,
            verbose=False,
        )

        # Store in session state
        st.session_state.summarization_chain = summarization_chain

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
        classification = classify_user_input(user_input)
        print(classification)

        if classification =='question':
            st.session_state.messages.append({"role": "user", "content": user_input})
            # ai_response = st.session_state.conversation.predict(input=user_input)
            response = handle_question_chain(user_input)
            st.session_state.messages.append(
                {"role": "assistant", "content": response}
            )
            st.rerun()



        else: 
            if user_input.lower().strip() in ["yeah", "let's go", "I am ready", "go ahead"]:
                # Trigger summarization chain
                conversation_history = st.session_state.memory.load_memory_variables({})[
                    "history"
                ]
                extracted_preferences = st.session_state.summarization_chain.run(
                    conversation=conversation_history
                )

                st.subheader("Collected User Preferences")
                st.write(extracted_preferences.strip())

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




# ------------------------------------------>
# Define the classification function
def classify_user_input(user_input):
    """
    Classify user input as either 'question' or 'answer'.
    """
    # Define the classification chain
    classification_chain = (
        PromptTemplate.from_template(
            """Classify the following user input as either 'question' or 'answer'. 

User Input:
{input}

Classification:"""
        )
        | ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
        | StrOutputParser()
    )
    
    # Invoke the chain with the user input
    classification = classification_chain.invoke({"input": user_input})
    return classification.strip().lower()


def handle_question_chain(user_input):
    # Access the same memory object being used by the other chain
    memory = st.session_state.memory  
    # Define your logic for handling questions here
    llm = ChatOpenAI(temperature=0, model_name="gpt-4")
    uri = neo4j_uri
    auth = (neo4j_user, neo4j_password)
    # ----->adding context logic
    zipcode, feature = parse_user_query(user_input)
    context = None
    if zipcode and feature:
        context = get_context_from_graph(zipcode, feature, uri, auth)
        if not context:
            context = "No specific information was found for this query. Here is general information about crime in Boston."

    # --------> Ending context logic

    # Combine context and user input into a single key for memory compatibility
    combined_input = f"Context: {context or 'General information'}\nQuestion: {user_input}"

    # Construct the prompt dynamically based on the context
    question_prompt = PromptTemplate.from_template(
        '''You are an assistant specializing in answering general questions related to the city of Boston, or highly specific questions related to the crime or demographics in a region of boston.
        You do not respond to any other question which is not related to the city of Boston. Limit your response to a maximum of 70 words or below that. 
        If unrelated, kindly remind them of what the Saarthi app does and how it is helpful.
        Make use of the context provided to answer any question related to crime or sdemographics in a particular area. user might twist their words. Infer what they are trying to ask.

        Conversation History:
        {history}

        Combined Input: {combined_input}

        AI Broker:''',
    )

    # Create a chain that incorporates memory and the updated prompt
    question_chain = LLMChain(llm=llm, prompt=question_prompt, memory=memory)

    # Run the chain with the combined input
    return question_chain.run(combined_input=combined_input)


# ------------------------------------>


if __name__ == "__main__":
    main()
