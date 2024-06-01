from flask import Flask, request, jsonify, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import google.generativeai as genai
import os

app = Flask(__name__)

# Configure Rate Limiting
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# Configure Google API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')


@app.route('/generate', methods=['POST'])
@limiter.limit("200 per day; 30 per hour; 10 per minute")  # Custom rate limit for this endpoint
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
        return jsonify({"Error": str(e)}), 500


@app.route('/')
def home():
    return "Hello. I am alive!"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
