from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import openai
import os
from typing import Any, Union, Dict, List, Optional
from openai import OpenAIError, RateLimitError
from openai.types.chat.chat_completion import ChatCompletion

app = Flask(__name__)
CORS(app)  # Initialize CORS

# Set up OpenAI API key
openai.api_key = 'sk-proj-xm1tU9Jczi6U7zYW9chXT3BlbkFJeiZbOueEs2A5ZkLSyRDJ'

# Explicitly setting debug and environment
app.config['ENV'] = 'development'
app.config['DEBUG'] = True

# Define characters and state (for simplicity, we use a dictionary)
campaign_state = {
    "characters": [],
    "sessions": []
}

def generate_response(input_text: str) -> str:
    prompt: str = f"OSRIC campaign response: {input_text}"
    try:
        response: ChatCompletion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        # Ensure you handle the response correctly
        choices = response.choices
        if not choices or not choices[0].message.content:
            raise ValueError("No content in message")
        message_content = choices[0].message.content.strip()
        return message_content
    except RateLimitError:
        return "Rate limit error: You have exceeded your quota. Please check your plan and billing details."
    except OpenAIError as e:
        app.logger.error(f"OpenAI API error: {e}")
        return f"OpenAI API error: {e}"
    except Exception as e:
        app.logger.error(f"Error generating response: {e}")
        return f"An error occurred while generating the response: {e}"

@app.route('/chat', methods=['POST'])
def chat() -> Union[Response, tuple[Response, int]]:
    if request.json is None:
        app.logger.error("Invalid input: request.json is None")
        return jsonify({"error": "Invalid input"}), 400

    user_input: str = request.json.get('input')
    if not user_input or not isinstance(user_input, str):
        app.logger.error(f"Invalid input: {user_input}")
        return jsonify({"error": "Invalid input"}), 400

    try:
        response_text: str = generate_response(input_text=user_input)
        return jsonify({"response": response_text})
    except Exception as e:
        app.logger.error(f"Error processing request: {e}")
        return jsonify({"error": "An error occurred while processing the request"}), 500

@app.route('/add_character', methods=['POST'])
def add_character() -> Union[Response, tuple[Response, int]]:
    if request.json is None:
        return jsonify({"error": "Invalid character data"}), 400

    character: Any = request.json.get('character')
    if not character:
        return jsonify({"error": "Invalid character data"}), 400

    campaign_state["characters"].append(character)
    return jsonify({"message": "Character added", "character": character})

@app.route('/get_characters', methods=['GET'])
def get_characters() -> Response:
    return jsonify({"characters": campaign_state["characters"]})

@app.route('/')
def serve_index() -> Response:
    return send_from_directory(directory='.', path='index.html')

@app.route('/favicon.ico')
def favicon() -> Response:
    return send_from_directory(directory=os.path.join(app.root_path, 'static'), path='favicon.ico')

if __name__ == '__main__':
    app.run(debug=True)







































































