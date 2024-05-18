# This code is part of the server application, that is used to connect to Google's AI.
# Not to be used in main application

import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configure Google API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')


@app.route('/generate', methods=['POST'])
def generate():
    """
    This function generates content using the provided prompt.

    Returns:
    - A JSON response containing the generated content.

    Raises:
    - A 400 Bad Request error if the prompt text is not provided.
    - A 500 Internal Server Error if an exception occurs during the generation process.

    Usage:
    - Send a POST request to the '/generate' endpoint with a JSON payload containing a 'prompt' field.
    """
    data = request.json
    prompt = data.get("prompt", "")

    if not prompt:
        return jsonify({"error": "Prompt text is required"}), 400

    try:
        response = model.generate_content(prompt)
        return jsonify({"response": response.text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/')
def home():
    return "Hello. I am alive!"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
