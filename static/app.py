import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from google.cloud import speech, storage
from pydub import AudioSegment

# Configure logging
logging.basicConfig(filename="app.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Flask app setup
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Configuration
UPLOAD_FOLDER = './static'
CONVERTED_FOLDER = './static/converted'
GCS_BUCKET_NAME = "your-gcs-bucket-name"  # Replace with your actual bucket name

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

# Function to convert audio file to proper format
def convert_audio(file_path, output_path):
    try:
        audio = AudioSegment.from_file(file_path)
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        audio.export(output_path, format="wav")
        logging.info(f"Audio converted and saved to: {output_path}")
        return output_path
    except Exception as e:
        logging.error(f"Error converting audio: {e}")
        raise

# Function to upload file to GCS
def upload_to_gcs(file_path, gcs_filename):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(gcs_filename)
        blob.upload_from_filename(file_path)
        logging.info(f"File uploaded to GCS: {gcs_filename}")
        return f"gs://{GCS_BUCKET_NAME}/{gcs_filename}"
    except Exception as e:
        logging.error(f"Error uploading to GCS: {e}")
        raise

# Routes
@app.route('/upload', methods=['POST'])
def upload_audio():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        logging.info(f"File uploaded successfully: {filepath}")
        return jsonify({"message": "File uploaded successfully", "file_path": filepath})
    except Exception as e:
        logging.error(f"Error uploading file: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/get-transcript', methods=['POST'])
def get_transcript():
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        if not file_path or not os.path.exists(file_path):
            return jsonify({"error": "Invalid file path"}), 400

        converted_file_path = os.path.join(CONVERTED_FOLDER, f"converted-{os.path.basename(file_path)}")
        convert_audio(file_path, converted_file_path)

        # Google Cloud Speech-to-Text client
        client = speech.SpeechClient()
        gcs_path = upload_to_gcs(converted_file_path, f"converted/{os.path.basename(converted_file_path)}")
        
        # Long-running transcription for longer audio
        operation = client.long_running_recognize(
            config={
                "encoding": speech.RecognitionConfig.AudioEncoding.LINEAR16,
                "sample_rate_hertz": 16000,
                "language_code": "en-US",
            },
            audio={"uri": gcs_path},
        )
        logging.info("Waiting for transcription operation to complete...")
        response = operation.result(timeout=300)

        # Extract and return transcript
        transcript = " ".join([result.alternatives[0].transcript for result in response.results])
        logging.info(f"Transcript: {transcript}")
        return jsonify({"transcript": transcript})
    except Exception as e:
        logging.error(f"Error during transcription: {e}")
        return jsonify({"error": str(e)}), 500

# Main function
if __name__ == '__main__':
    app.run(debug=True)
