import os
from langchain import ConversationChain
from langchain.chat_models import ChatOpenAI  # Changed import here
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import os
from dotenv import load_dotenv
import os

# Load the environment variables from the .env file
load_dotenv()

# Access the environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Define the prompt template
prompt_template = """
You are a helpful AI assistant acting as a friendly and professional rental apartment broker named Saarthi.

Your goal is to gather specific information from the user about their apartment preferences, specifically:
- The area or location where they are looking for an apartment.
- The number of bedrooms they need.
- The number of bathrooms they prefer.
- Any specific requirements regarding restaurants and food places near the apartment.
- Any desire for open playgrounds or parks near their place.

Please engage the user in a natural conversation to gather this information.

- Ask one question at a time.
- Use the conversation history to avoid repeating questions or asking for information the user has already provided.
- If the user is unsure or says "I don't know", politely acknowledge and move on.
- Do not provide any information unrelated to gathering the user's requirements.

Start by greeting the user and asking


 how you can assist them today.

Conversation History:
{history}

User: {input}
AI Broker:"""

prompt = PromptTemplate(input_variables=["history", "input"], template=prompt_template)

# Initialize the language model with GPT-4 using ChatOpenAI
llm = ChatOpenAI(temperature=0, model_name="gpt-4")

# Initialize conversation memory
memory = ConversationBufferMemory(memory_key="history", return_messages=True)

# Initialize the ConversationChain
conversation = ConversationChain(llm=llm, prompt=prompt, memory=memory, verbose=False)


def main():
    print("Welcome to the Rental Apartment Chatbot!")
    print("You can type 'exit' anytime to end the conversation.\n")

    # Start the conversation with an empty input to trigger the initial greeting
    ai_response = conversation.predict(input="")
    print(f"AI Broker: {ai_response.strip()}")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("AI Broker: Thank you for using our service. Have a great day!")
            break

        # Generate AI response
        ai_response = conversation.predict(input=user_input)
        print(f"AI Broker: {ai_response.strip()}")


if __name__ == "__main__":
    main()
