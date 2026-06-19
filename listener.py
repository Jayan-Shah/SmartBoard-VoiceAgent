import os
import json
import speech_recognition as sr
from modules.audio_processor import transcribe_audio
from modules.llm_engine import generate_smartboard_content

# --- ABSOLUTE PATH SETUP ---
# Guarantees it writes to the exact same file app.py is reading
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "shared_classroom_state.json")
TEMP_AUDIO_FILE = os.path.join(BASE_DIR, "lapel_temp.wav")

def start_listening():
    recognizer = sr.Recognizer()
    
    # Optional: Tweaking these helps with background classroom noise
    recognizer.energy_threshold = 300 
    recognizer.dynamic_energy_threshold = True

    with sr.Microphone() as source:
        print("Initializing Bluetooth Lapel Mic...")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Calibration complete. Listening for wake word 'Assistant'...\n")

        while True:
            try:
                # Listen for audio (phrase_time_limit prevents it from recording forever if it gets stuck)
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=15)
                print("🎤 Speech detected! Processing...")

                # Save the audio bytes to our temporary file for Groq to read
                with open(TEMP_AUDIO_FILE, "wb") as f:
                    f.write(audio.get_wav_data())

                # Send to Groq for ultra-fast transcription
                transcript = transcribe_audio(TEMP_AUDIO_FILE)

                # Check for the Wake Word
                if transcript and "assistant" in transcript.lower():
                    print(f"✅ Command Accepted: {transcript.strip()}")
                    
                    # Pass the command to Gemini
                    ai_output = generate_smartboard_content(transcript)

                    # Clean out any accidental markdown from the LLM
                    clean_output = ai_output.replace("```json", "").replace("```", "").strip()

                    # --- SMART ROUTER ---
                    try:
                        # Try to parse it as a Quiz
                        quiz_json = json.loads(clean_output)
                        if isinstance(quiz_json, list):
                            new_state = {
                                "mode": "quiz",
                                "visual_display": "",
                                "quiz_data": quiz_json,
                                "quiz_index": 0
                            }
                    except json.JSONDecodeError:
                        # If JSON parsing fails, treat it as a standard text explanation
                        new_state = {
                            "mode": "explanation",
                            "visual_display": ai_output,
                            "quiz_data": [],
                            "quiz_index": 0
                        }

                    # Safely write the new state to the shared file
                    with open(STATE_FILE, "w") as f:
                        json.dump(new_state, f)
                        
                    print("✅ Smart Board Updated Successfully!\n")
                    print("Listening for wake word 'Assistant'...")

            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                print(f"⚠️ Error processing audio: {e}")

if __name__ == "__main__":
    start_listening()