from pydub import AudioSegment
import os

def convert_audio(input_path, output_path):
    try:
        # Load the audio file
        audio = AudioSegment.from_file(input_path)

        # Convert to 16kHz sample rate and mono channel
        audio = audio.set_frame_rate(16000).set_channels(1)

        # Export the converted audio
        audio.export(output_path, format="wav")
        print(f"Converted file saved to: {output_path}")
    except Exception as e:
        print(f"Error converting file: {e}")

# Input and output file paths
input_path = "/Users/ryadav/MOM-Backend/static/recording-1733609226148.wav"
output_path = "/Users/ryadav/MOM-Backend/static/recording-1733609226148_converted.wav"

convert_audio(input_path, output_path)
