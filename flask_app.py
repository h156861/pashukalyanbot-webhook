from flask import Flask, request, jsonify
import os
import google.generativeai as genai

# -----------------------------
# Initialization & Configuration
# -----------------------------

def create_app():
    """Initialize and configure the Flask app."""
    app = Flask(__name__)
    configure_gemini()
    register_routes(app)
    return app


def configure_gemini():
    """Configure the Gemini API."""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY not set in environment variables.")
    genai.configure(api_key=api_key)


def get_model():
    """Return a configured Gemini model."""
    return genai.GenerativeModel('gemini-2.5-flash-preview-05-20')


# -----------------------------
# Business Logic
# -----------------------------

def get_intent_and_params(request_json):
    """Extract intent name and parameters from the Dialogflow request."""
    intent_name = request_json.get('queryResult', {}).get('intent', {}).get('displayName')
    params = request_json.get('queryResult', {}).get('parameters', {})
    return intent_name, params


def handle_intent(intent_name, params):
    """Process the intent logic and return response text."""
    if intent_name == 'intent.diagnosis.start':
        animal = params.get('animal', 'an animal')
        symptoms = params.get('symptoms', 'no symptoms provided')
        return f"Okay, let's start diagnosis for {animal}. What symptoms are you noticing?"
    else:
        return "I didn’t understand that intent. Can you repeat?"


def build_response(response_text):
    """Build the Dialogflow response payload."""
    return {"fulfillmentText": response_text}


# -----------------------------
# Routes
# -----------------------------

def register_routes(app):
    """Register Flask routes."""

    @app.route('/webhook', methods=['POST'])
    def webhook():
        """Handle incoming requests from Dialogflow ES."""
        try:
            request_json = request.get_json(silent=True)
            intent_name, params = get_intent_and_params(request_json)
            print("DEBUG:", intent_name, params)
            response_text = handle_intent(intent_name, params)
        except Exception as e:
            print(f"An error occurred: {e}")
            response_text = "I apologize, a technical error occurred while processing the request."

        return jsonify(build_response(response_text))


# -----------------------------
# App Entry Point
# -----------------------------

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)




