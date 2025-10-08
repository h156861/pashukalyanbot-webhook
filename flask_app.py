import os
import json
from flask import Flask, request, jsonify
import google.generativeai as genai

# Initialize the Flask App
app = Flask(__name__)

# --- Configure the Gemini API ---
# This securely gets your key from the server's environment variables (like in Render)
API_KEY = os.environ.get('GEMINI_API_KEY')
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handles the incoming request from Dialogflow ES."""
    request_json = request.get_json(silent=True)

    # --- ES LOGIC: Get Intent Name instead of Tag ---
    intent_name = request_json.get('queryResult', {}).get('intent', {}).get('displayName')
    params = request_json.get('queryResult', {}).get('parameters', {})
    response_text = ""

    try:
        # The "Router" now checks the intent's display name
        # IMPORTANT: Make sure these names exactly match your intent names in Dialogflow
        if intent_name == 'intent.diagnosis.start':
            animal = params.get('animal', 'an animal')
            symptoms = params.get('symptoms', 'no symptoms provided')
            
            system_prompt = "You are a specialist AI Veterinarian and Triage Assistant for the Pashu Kalyan initiative, focused on Indian livestock. Your response must be concise and **strictly in English**. Provide a probable condition, severity, 3-5 simple first-aid steps, and a clear next step to consult a vet. Format the response with Markdown."
            user_query = f"Animal: {animal}. Symptoms: {symptoms}."
            
            full_prompt = f"{system_prompt}\n\n{user_query}"
            response = model.generate_content(full_prompt)
            response_text = response.text

        elif intent_name == 'intent.economic.info':
            animal_or_product = params.get('animal_or_product', 'livestock')
            
            system_prompt = "You are an AI Economic Advisor for the Viksit Bharat initiative. Provide real-time, grounded information for an Indian farmer. Find one relevant government scheme, current market rates, and one preventative welfare tip. Use Google Search. Respond in clear English and structure the answer with Markdown headings."
            user_query = f"Find the latest government scheme, market rates, and a seasonal preventative welfare tip for a farmer dealing with {animal_or_product}."
            
            full_prompt = f"{system_prompt}\n\n{user_query}"
            response = model.generate_content(full_prompt)
            response_text = response.text

        elif intent_name == 'intent.feed.plan':
            animal = params.get('animal', 'an animal')
            details = params.get('details', 'no details provided')
            
            system_prompt = "You are an expert AI Livestock Nutritionist specializing in Indian livestock and locally available, cost-effective feed. Generate a practical, balanced daily feed plan. Structure the response with Markdown headings for Morning, Afternoon, and Evening feeds, and include a section for supplements."
            user_query = f"Generate a daily feed plan for a {animal}. Details: {details}."

            full_prompt = f"{system_prompt}\n\n{user_query}"
            response = model.generate_content(full_prompt)
            response_text = response.text
            
        else:
            response_text = f"Webhook received but the intent name '{intent_name}' was not recognized."

    except Exception as e:
        print(f"An error occurred: {e}")
        response_text = "I apologize, a technical error occurred while processing the request."

    # --- ES LOGIC: The response format is simpler ---
    response_payload = {
        "fulfillmentText": response_text
    }
    return jsonify(response_payload)

