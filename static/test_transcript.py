import os
from pydub import AudioSegment
from google.cloud import speech

# Function to convert audio file to LINEAR16 PCM format
def convert_to_linear16(input_path, output_path):
    try:
        # Load the input file
        audio = AudioSegment.from_file(input_path)
        
        # Ensure the audio is 16-bit, mono, and 16000 Hz
        audio = audio.set_frame_rate(16000).set_sample_width(2).set_channels(1)  # 2 bytes = 16 bits
        audio.export(output_path, format="wav")
        
        print(f"Converted file saved to: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error during conversion: {e}")
        return None

# Function to send the audio file to Google Cloud Speech-to-Text
def transcribe_audio(file_path):
    try:
        # Initialize Google Speech-to-Text client
        client = speech.SpeechClient()

        # Read the converted audio file
        with open(file_path, "rb") as audio_file:
            audio_content = audio_file.read()

        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
        )

        # Call the Google Speech-to-Text API
        response = client.recognize(config=config, audio=audio)

        # Extract and return the transcript
        transcript = " ".join([result.alternatives[0].transcript for result in response.results])
        return transcript
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    # Specify the input file path and output file path
    input_file_path = "/Users/ryadav/MOM-Backend/static/recording-1733609226148.wav"
    output_file_path = "/Users/ryadav/MOM-Backend/static/converted-recording.wav"

    # Step 1: Convert the audio file
    converted_file_path = convert_to_linear16(input_file_path, output_file_path)

    # Step 2: Transcribe the audio file if conversion was successful
    if converted_file_path:
        print("Sending file for transcription...")
        transcript = transcribe_audio(converted_file_path)
        print("Transcript:")
        print(transcript)
    else:
        print("Conversion failed. Cannot proceed with transcription.")
