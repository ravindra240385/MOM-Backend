import pyaudio
import wave

def record_audio(file_name="test_audio.wav", duration=5, sample_rate=44100, channels=1, chunk=1024):
    """
    Records audio from the microphone and saves it as a .wav file.

    Args:
        file_name (str): The name of the output .wav file.
        duration (int): Duration of the recording in seconds.
        sample_rate (int): Sample rate of the recording (in Hz).
        channels (int): Number of audio channels (1 for mono, 2 for stereo).
        chunk (int): Number of frames per buffer.
    """
    audio = pyaudio.PyAudio()

    # Open a stream for recording
    stream = audio.open(format=pyaudio.paInt16,
                        channels=channels,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=chunk)

    print("Recording... Speak into the microphone.")
    frames = []

    # Record for the specified duration
    for _ in range(0, int(sample_rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    print("Recording finished.")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recording to a WAV file
    with wave.open(file_name, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))

    print(f"Audio saved as {file_name}")

if __name__ == "__main__":
    # Record audio and save it as "test_audio.wav" in the current directory
    record_audio() 
