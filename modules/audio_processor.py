import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def transcribe_audio(file_path):
    try:
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-large-v3", # Groq's fast Whisper model
                file=audio_file,
                prompt="Hinglish language teaching, basic science, math, Haryana school context. Baccho, aaj hum gravity padhenge."
            )
        return transcript.text
    except Exception as e:
        return f"Error transcribing audio: {str(e)}"