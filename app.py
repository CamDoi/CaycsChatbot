from flask import Flask, render_template, request, jsonify
import openai
from dotenv import load_dotenv
import os
import logging

# Load environment variables from the .env file
load_dotenv()

# Get the API key from environment variables
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

openai.api_key = api_key

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

@app.route("/", methods=["GET", "HEAD"])
def home():
    logging.debug("Home route accessed")
    return render_template("index.html"), 200

@app.route("/api/chat", methods=["POST"])
def chat():
    # Get user input from the POST request
    user_input = request.json.get("user_input")

    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    try:
        # Call OpenAI's API
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Specify the model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        # Extract the assistant's response
        assistant_response = response['choices'][0]['message']['content']

        # Return the response as JSON
        return jsonify({"response": assistant_response})
    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Ensure the app runs securely if hosted locally
    app.run(debug=True)
