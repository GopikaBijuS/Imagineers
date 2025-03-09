


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

# ✅ Check if user input exists
if len(sys.argv) > 1:
    user_input = sys.argv[1].strip()  # Remove extra spaces
    if not user_input:
        print("Error: Empty message received")
        sys.exit(1)  # Exit with error

    # 🔹 Get AI response
    chat_session = model.start_chat(history=history)
    response = chat_session.send_message(user_input)
    model_response = response.text.strip()

    # ✅ Ensure response is printed (so Node.js can capture it)
    print(model_response)

    # Store conversation history
    history.append({"role": "user", "parts": [user_input]})
    history.append({"role": "model", "parts": [model_response]})

else:
    print("Error: No input received")
    sys.exit(1)  # Exit with error

