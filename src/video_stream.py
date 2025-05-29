import os

import cv2
import base64
import requests
import json
import time
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS # Import CORS

app = Flask(__name__)
CORS(app)

API_KEY = "your api key" #TODO put your KEY
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
#API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-live:generateContent" # Updated to gemini-2.0-flash-live

CAPTURE_FREQUENCY_SECONDS = 2
PROMPT = """
You are a virtual sports coach which speak hebrew. Your role is to analyze video footage of a user performing physical activities. Your tasks are:
Sport Identification: Detect and identify which sport the user is performing based on body movements, equipment, and environment.
Form and Technique Evaluation: Analyze the user's posture, gestures, and movement patterns to determine if they align with the correct technique for the identified sport.
Feedback and Alerts:
If the technique is correct, provide positive reinforcement and suggestions for improvement.
If the technique is incorrect or potentially harmful, issue an alert with a clear explanation of what is wrong and how to correct it.
Tone and Style: Be encouraging, constructive, and professional. Use terminology appropriate to the sport and skill level of the user.
Safety Awareness: Prioritize injury prevention. If a movement appears unsafe, flag it immediately and suggest safer alternatives.
You are capable of understanding video input, recognizing human motion, and comparing it to sport-specific biomechanical models. 
You adapt your feedback based on the user's apparent skill level and progress over time.
"""



def get_gemini_response(base64_image_data, prompt):
    """
    Sends a Base64 encoded image to the Gemini API and returns the text response.
    """
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt},
                    {
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": base64_image_data
                        }
                    }
                ]
            }
        ]
    }

    try:
        # Append API key to URL if it's provided by Canvas runtime
        full_api_url = f"{API_URL}?key={API_KEY}" if API_KEY else API_URL
        response = requests.post(full_api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        result = response.json()

        if result.get("candidates") and len(result["candidates"]) > 0 and \
           result["candidates"][0].get("content") and \
           result["candidates"][0]["content"].get("parts") and \
           len(result["candidates"][0]["content"]["parts"]) > 0:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            print(f"[{time.strftime('%H:%M:%S')}] Warning: Unexpected Gemini API response structure: {result}", file=sys.stderr)
            return "No valid response from Gemini API."

    except requests.exceptions.RequestException as e:
        print(f"[{time.strftime('%H:%M:%S')}] Error calling Gemini API: {e}", file=sys.stderr)
        return f"API Error: {e}"
    except json.JSONDecodeError as e:
        print(f"[{time.strftime('%H:%M:%S')}] Error decoding JSON response: {e}", file=sys.stderr)
        return "Error decoding API response."
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] An unexpected error occurred: {e}", file=sys.stderr)
        return f"An unexpected error occurred: {e}"




def main():
    # Initialize webcam
    # 0 indicates the default webcam. Change if you have multiple cameras.
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam. Please ensure it's connected and not in use.", file=sys.stderr)
        return

    print("Webcam started. Press 'q' to quit.")
    print(f"Sending frames to Gemini every {CAPTURE_FREQUENCY_SECONDS} seconds...")
    print("-" * 50)

    last_capture_time = time.time()

    while True:
        ret, frame = cap.read() # Read a frame from the webcam

        if not ret:
            print("Error: Failed to grab frame.", file=sys.stderr)
            break

        # Display the frame in a window
        cv2.imshow('Webcam Feed (Press "q" to quit)', frame)

        current_time = time.time()
        if current_time - last_capture_time >= CAPTURE_FREQUENCY_SECONDS:
            print(f"\n[{time.strftime('%H:%M:%S')}] Capturing frame and sending to Gemini...")
            # Encode frame to JPEG
            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80]) # 80% quality
            base64_image = base64.b64encode(buffer).decode('utf-8')

            # Get response from Gemini
            gemini_response = get_gemini_response(base64_image, PROMPT)
            print(f"[{time.strftime('%H:%M:%S')}] Gemini says: {gemini_response}")
            print("-" * 50)

            last_capture_time = current_time

        # Wait for 1 millisecond and check for 'q' key press to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\n'q' pressed. Exiting...")
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    print("Webcam released and windows closed.")

@app.route('/analyze_frame', methods=['POST'])
def analyze_frame():
    """
    API endpoint to receive a Base64 encoded image frame and send it to Gemini for analysis.
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    base64_image_data = data.get('image_data')

    if not base64_image_data:
        return jsonify({"error": "Missing 'image_data' in request body"}), 400

    print(f"[{time.strftime('%H:%M:%S')}] Received frame for analysis.")
    gemini_response = get_gemini_response(base64_image_data, PROMPT)
    print(f"[{time.strftime('%H:%M:%S')}] Sending response: {gemini_response[:50]}...") # Log first 50 chars

    return jsonify({"analysis_result": gemini_response})


#main()

if __name__ == '__main__':
    # Cloud Run provides the port via the PORT environment variable.
    # We default to 8080 if not set (e.g., for local development).
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)