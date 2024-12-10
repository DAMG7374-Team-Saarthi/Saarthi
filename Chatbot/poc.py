# import os
# from langchain import ConversationChain
# from langchain.chat_models import ChatOpenAI  # Changed import here
# from langchain.prompts import PromptTemplate
# from langchain.memory import ConversationBufferMemory
# import os

# from dotenv import load_dotenv
# import os

# # Load the environment variables from the .env file
# load_dotenv()

# # Access the environment variables
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# # Define the prompt template
# prompt_template = """
# You are a helpful AI assistant acting as a friendly and professional rental apartment broker named Saarthi from Boston, Massachusetts, who deals in apartments in Fenway, South Boston, Allston area.

# Your goal is to gather specific information from the user about their apartment preferences, specifically:
# - The area or location where they are looking for an apartment.
# - The desired rent range or budget in US dollars.
# - The number of bedrooms they need.
# - The number of bathrooms they prefer.
# - Any specific requirements regarding restaurants and food places near the apartment.
# - Any desire for open playgrounds or parks near their place.

# Please engage the user in a natural conversation to gather this information.

# - Ask one question at a time.
# - If the user states a area or location out of the areas mentioned in the prompt, kindly remind them that for now you only have information about apartments in the Boston, MA region.
# - Use the conversation history to avoid repeating questions or asking for information the user has already provided.
# - If the user is unsure or says "I don't know", politely acknowledge and move on.
# - Do not provide any information unrelated to gathering the user's requirements.
# - Once all the requirements are gathered from the user, give out the final output by populating the ... below with user preference using ONLY this format:
#      "Area": ...,
#      "Budget": ...,
#      "Bedrooms": ...,
#      "Bathrooms": ...,
#      "Food Preferences": ...,
#      "Playgrounds": ...

# Start by greeting the user and asking

#  how you can assist them today.

# Conversation History:
# {history}

# User: {input}
# AI Broker:"""

# prompt = PromptTemplate(input_variables=["history", "input"], template=prompt_template)

# # Initialize the language model with GPT-4 using ChatOpenAI
# llm = ChatOpenAI(temperature=0, model_name="gpt-4")
# memory = ConversationBufferMemory(memory_key="history", return_messages=True)
# conversation = ConversationChain(llm=llm, prompt=prompt, memory=memory, verbose=False)


# def main():
#     print("Welcome to the Rental Apartment Chatbot!")
#     print("You can type 'exit' anytime to end the conversation.\n")

#     # Start the conversation with an empty input to trigger the initial greeting
#     ai_response = conversation.predict(input="")
#     print(f"AI Broker: {ai_response.strip()}")

#     while True:
#         user_input = input("You: ").strip()
#         if user_input.lower() in ["exit", "quit"]:
#             print("AI Broker: Thank you for using our service. Have a great day!")
#             break

#         # Generate AI response
#         ai_response = conversation.predict(input=user_input)
#         print(f"AI Broker: {ai_response.strip()}")


# if __name__ == "__main__":
#     main()


import os
from langchain import ConversationChain, LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
from nemoguardrails import RailsConfig
from nemoguardrails.integrations.langchain.runnable_rails import RunnableRails

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Conversation prompt template
# conversation_prompt = PromptTemplate(
#     input_variables=["history", "input"],
#     template="""
# You are a helpful AI assistant acting as a friendly and professional rental apartment broker named Saarthi from Boston, Massachusetts. You deal in apartments in Fenway, South Boston.

# Your goal is to gather specific information from the user about their apartment preferences, specifically:
# - The area or location where they are looking for an apartment.
# - The desired rent range or budget in US dollars.
# - The number of bedrooms they need.
# - The number of bathrooms they prefer.
# - Any specific requirements regarding restaurants and food places near the apartment.
# - Any desire for open playgrounds or parks near their place.

# Please engage the user in a natural conversation to gather this information.

# - Ask one question at a time.
# - If the user mentions an area outside of Fenway, South Boston, or Allston, kindly remind them that you currently only have information about apartments in those areas.
# - Use the conversation history to avoid repeating questions or asking for information the user has already provided.
# - If the user is unsure or says "I don't know", politely acknowledge and move on.
# - Do not provide any information unrelated to gathering the user's requirements.

# Start by greeting the user and asking how you can assist them today.

# Conversation History:
# {history}

# User: {input}
# AI Broker:""",
# )
conversation_prompt = PromptTemplate(
    input_variables=["history", "input"],
    template="""
You are a helpful AI assistant acting as a friendly and professional rental apartment broker named Saarthi from Boston, Massachusetts.

Your goal is to gather specific information from the user about their apartment preferences, specifically:
- The area or location where they are looking for an apartment.
- The desired rent range or budget in US dollars.
- The number of bedrooms they need.
- The number of bathrooms they prefer.
- Any specific requirements regarding restaurants and food places near the apartment.
- Any desire for open playgrounds or parks near their place.

Please engage the user in a natural conversation to gather this information.

Start by greeting the user and asking how you can assist them today.

Conversation History:
{history}

User: {input}
AI Broker:""",
)

# Summarization prompt template
summarization_prompt = PromptTemplate(
    input_variables=["conversation"],
    template="""
Given the following conversation between a user and an AI assistant acting as a rental apartment broker, extract the user's apartment preferences.


Conversation:
{conversation}

""",
)
import os
import yaml

# # Define the path to the config file
# config_file_path = r'D:\Github_Saarthi_November\Chatbot_POC\summary_config.yml'

# # Check if the config file exists
# if os.path.isfile(config_file_path):
#     print("Config file found at:", config_file_path)
#     with open(config_file_path, 'r') as file:
#         try:
#             raw_config = yaml.safe_load(file)
#             print("Raw Config Loaded Successfully:", raw_config)
#         except yaml.YAMLError as e:
#             print("Error loading YAML:", e)
# else:
#     print(f"Config file not found at: {config_file_path}")

# # Load the guardrails configuration
config = RailsConfig.from_path("guardrails.yaml")
# print("config file is here------------>",config)
guardrails = RunnableRails(config, passthrough=False)

# Set up the language model with guardrails


# Initialize the language model
llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

llm_with_guardrails = guardrails | llm

memory = ConversationBufferMemory(memory_key="history")
conversation = ConversationChain(
    llm=llm_with_guardrails, prompt=conversation_prompt, memory=memory, verbose=False
    # llm=llm,
    # prompt=conversation_prompt,
    # memory=memory,
    # verbose=False
)

# Initialize the summarization chain
summarization_chain = LLMChain(
    llm=llm, prompt=summarization_prompt, verbose=False
    # llm=llm,
)


def main():
    print("Welcome to the Rental Apartment Chatbot!")
    print("You can type 'exit' anytime to end the conversation.\n")

    # Start the conversation
    ai_response = conversation.predict(input="")
    print(f"AI Broker: {ai_response.strip()}")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit", "thank you"]:
            print(
                "AI Broker: Thank you for using our service. Let's review the information you've provided."
            )
            break

        # Generate AI response

        ai_response = conversation.predict(input=user_input)
        print(f"AI Broker: {ai_response.strip()}")

    conversation_history = memory.load_memory_variables({})["history"]

    # Run the summarization chain
    extracted_preferences = summarization_chain.run(conversation=conversation_history)

    # Output the extracted preferences
    print("\nCollected User Preferences:")
    print(extracted_preferences.strip())


if __name__ == "__main__":
    main()
