import speech_recognition as sr
import json
import os
from dotenv import load_dotenv

# Import our existing AI logic!
from modules.audio_processor import transcribe_audio
from modules.llm_engine import generate_smartboard_content

load_dotenv()
STATE_FILE = "shared_classroom_state.json"

def save_shared_state(display_text, answer):
    """Writes the AI output to the file so Streamlit can read it."""
    with open(STATE_FILE, "w") as f:
        json.dump({"visual_display": display_text, "quiz_answer": answer}, f)
    print("✅ Smart Board Updated Successfully!")

def start_lapel_listener():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("\n🎤 Initializing Bluetooth Lapel Mic...")
    with mic as source:
        # Calibrate for classroom background noise for 2 seconds
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print("🎧 Calibration complete. Listening for wake word 'Assistant'...\n")

    # Infinite loop to keep the microphone open
    while True:
        try:
            with mic as source:
                # Listen for speech. Timeout prevents it from hanging forever.
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("⏳ Speech detected! Processing...")
            
            # Save the captured audio to a temporary file
            file_path = "lapel_temp.wav"
            with open(file_path, "wb") as f:
                f.write(audio.get_wav_data())
            
            # Send to Groq Whisper
            transcript = transcribe_audio(file_path)
            
            if "assistant" not in transcript.lower():
                print(f"🚫 Ignored (No wake word): {transcript}")
                continue
                
            print(f"🎯 Command Accepted: {transcript}")
            
            # Send to Groq Llama 3
            ai_output = generate_smartboard_content(transcript)
            
            # Parse the output
            if "Correct Answer:" in ai_output:
                clean_display, answer_part = ai_output.split("Correct Answer:", 1)
                save_shared_state(clean_display.strip(), answer_part.strip())
            else:
                save_shared_state(ai_output, None)

        except sr.WaitTimeoutError:
            # Just loops back and keeps listening if no one speaks
            continue
        except Exception as e:
            print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    start_lapel_listener()