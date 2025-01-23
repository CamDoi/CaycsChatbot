from flask import Flask, render_template, request, jsonify
import openai
from dotenv import load_dotenv
import os
import logging
import traceback

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

# Redirect HTTP to HTTPS (for production, this is better handled by a reverse proxy like Nginx)
@app.before_request
def redirect_to_https():
    if not request.is_secure and app.env != "development":
        url = request.url.replace("http://", "https://", 1)
        return jsonify({"error": "Please use HTTPS."}), 403

@app.route("/", methods=["GET", "HEAD"])
def home():
    logging.debug(f"Home route accessed with method: {request.method}")
    logging.debug(f"Template folder: {app.template_folder}")
    if request.method == "HEAD":
        # Respond with only headers for HEAD requests
        return "", 200
    try:
        # Render the template for GET requests
        return render_template("index.html"), 200
    except Exception as e:
        logging.error(f"Error rendering template: {str(e)}")
        logging.error(traceback.format_exc())
        return ("Error loading the homepage. Please contact support.", 500)

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
    # Specify paths to your SSL certificate and private key
    ssl_context = ('path/to/cert.pem', 'path/to/key.pem')  # Replace with actual file paths

    try:
        app.run(debug=True, ssl_context=ssl_context)  # HTTPS enabled
    except Exception as e:
        logging.error("Error starting the application with SSL context.")
        logging.error(traceback.format_exc())
