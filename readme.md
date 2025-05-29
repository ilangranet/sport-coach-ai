I'll create a comprehensive README.md file for this Sports Coach AI project:

# Sports Coach AI

This project is an AI-powered sports coach that uses computer vision and the Google Gemini AI model to analyze video streams of physical activities in real-time. The system can identify sports, evaluate form and technique, and provide feedback in Hebrew.

## Features

- Real-time video analysis through webcam
- Sport identification based on body movements
- Form and technique evaluation
- Constructive feedback in Hebrew
- Alerts for improper or unsafe technique
- REST API endpoint for frame analysis
- CORS support for web integration

## Prerequisites

- Python 3.8+
- Webcam (for local video stream)
- Google Gemini API key

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ilangranet/sport-coach-ai.git
   cd sport-coach-ai
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## Usage

### Running the Flask API Server

To start the Flask server that provides the API endpoint for video analysis:

```bash
python src/video_stream.py
```

This will start the server on `http://localhost:5001`.

### API Endpoint

The system exposes a single API endpoint:

- **POST /analyze_frame**
  - Accepts a JSON payload with a base64-encoded image
  - Returns AI analysis of the sports activity

Example request:
```bash
curl -X POST \
  http://localhost:5001/analyze_frame \
  -H 'Content-Type: application/json' \
  -d '{
    "image_data": "base64_encoded_image_data_here"
  }'
```

### Running the Webcam Demo

To run the webcam-based demo directly:

1. Ensure your webcam is connected
2. Edit the `src/video_stream.py` file and uncomment the `main()` line
3. Run:
   ```bash
   python src/video_stream.py
   ```
4. Press 'q' to exit the webcam feed

## Configuration

You can adjust the following parameters in the `src/video_stream.py` file:

- `CAPTURE_FREQUENCY_SECONDS`: Time between frame captures (default: 2 seconds)
- `PROMPT`: The instructions given to the Gemini model
- API model: Choose between `gemini-2.0-flash` or `gemini-2.0-flash-live`

## How It Works

1. The system captures video frames from your webcam or receives them via API
2. Frames are encoded to base64 and sent to Google's Gemini AI model
3. The AI analyzes the sports activity in the frame
4. The system returns feedback about the detected sport, technique, and suggestions for improvement
5. All communication with the user is provided in Hebrew

## Security Note

Be sure to protect your API key and not commit it to public repositories. The repository includes a `.env` file in `.gitignore` to help prevent accidental exposure.

## License

Sport Coach AI is licensed under the MIT License.