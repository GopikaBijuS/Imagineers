import sys
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Set up model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="queries related to yoga\n",
)

history = []

# Get user input from Node.js
user_input = sys.argv[1]  # Read message from command-line argument

chat_session = model.start_chat(history=history)
response = chat_session.send_message(user_input)
model_response = response.text

# Print response (Node.js will capture this output)
print(model_response)

# Store conversation history
history.append({"role": "user", "parts": [user_input]})
history.append({"role": "model", "parts": [model_response]})
