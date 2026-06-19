import streamlit as st
from audio_recorder_streamlit import audio_recorder
from dotenv import load_dotenv
import os
import json

from modules.audio_processor import transcribe_audio
from modules.llm_engine import generate_smartboard_content

# 1. Load Secure Environment Variables
load_dotenv()

# 2. UI Configuration
st.set_page_config(page_title="AI Teaching Assistant", page_icon="🏫", layout="wide")

STATE_FILE = "shared_classroom_state.json"

def load_shared_state():
    default_state = {
        "mode": "explanation", 
        "visual_display": "👋 Welcome! Say 'Assistant' to begin.",
        "quiz_data": [],       
        "quiz_index": 0        
    }
    
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                if "mode" not in data:
                    return default_state
                return data
        except:
            pass
            
    return default_state

def save_shared_state(state_dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state_dict, f)

shared_data = load_shared_state()

# 3. Detect View Mode
query_params = st.query_params
view_mode = query_params.get("view", "teacher")

# 4. Premium UI/UX CSS Injection
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* Cinematic Background */
.stApp {
    background-color: #050505;
    background-image: 
        radial-gradient(at 80% 0%, hsla(228,100%,74%,0.08) 0px, transparent 50%),
        radial-gradient(at 0% 100%, hsla(263,100%,70%,0.08) 0px, transparent 50%);
    background-attachment: fixed;
    color: #e2e8f0;
}

#MainMenu, header, footer { visibility: hidden; }

/* =========================================
   STUDENT SMARTBOARD (PHYSICAL BOARD LOOK)
========================================= */
.smartboard-frame {
    background: #0f172a;
    border: 12px solid #1e293b; /* Top/Sides of the frame */
    border-bottom: 24px solid #1e293b; /* Thicker bottom tray */
    border-radius: 16px;
    width: 100%;
    aspect-ratio: 16 / 9; /* Forces horizontal landscape mode */
    max-height: 80vh;
    padding: 3rem 4rem;
    box-shadow: 0 30px 60px rgba(0,0,0,0.6), inset 0 0 30px rgba(0,0,0,0.5);
    overflow-y: auto; /* Scrolls neatly inside the board if text is long */
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.smartboard-content {
    color: #f8fafc;
    font-size: 2.2rem; /* Scaled down for paragraphs */
    line-height: 1.6;
    text-align: left; /* Much better for reading lists */
}

/* =========================================
   AUDIO RECORDER IFRAME FIX
========================================= */
iframe[title="audio_recorder_streamlit.audio_recorder"] {
    border-radius: 50% !important;
    width: 60px !important;
    height: 60px !important;
    display: block;
    margin: 0 auto;
    box-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
}

/* Streamlit Native Button Overrides */
.stButton>button {
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    background: rgba(255, 255, 255, 0.05) !important;
    color: white !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
.stButton>button:hover {
    background: rgba(255, 255, 255, 0.1) !important;
    border-color: rgba(255,255,255,0.2) !important;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 📺 STUDENT / SMART BOARD VIEW
# ==========================================
if view_mode == "student":
    @st.fragment(run_every=2)
    def student_board_updater():
        data = load_shared_state()
        
        if data["mode"] == "explanation":
            # Format line breaks for HTML
            formatted_display = data["visual_display"].replace('\n', '<br>')
            st.markdown(
                f'<div class="smartboard-frame"><div class="smartboard-content">{formatted_display}</div></div>', 
                unsafe_allow_html=True
            )
            
        elif data["mode"] == "quiz" and len(data["quiz_data"]) > 0:
            idx = data["quiz_index"]
            current_q = data["quiz_data"][idx]
            options_html = "<br><br>".join([f"• {opt}" for opt in current_q["options"]])
            st.markdown(
                f"""
                <div class="smartboard-frame">
                    <div class="smartboard-content">
                        <span style="color: #94a3b8; font-size: 0.7em;">Question {idx + 1}</span><br>
                        <b style="font-size: 1.2em;">{current_q['question']}</b><br><br>
                        <div style="color: #cbd5e1;">{options_html}</div>
                    </div>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
    student_board_updater()

# ==========================================
# 📱 TEACHER REMOTE CONTROL VIEW
# ==========================================
else:
    st.title("Teacher Control Panel")
    st.caption("AI-Powered Classroom Remote • Live Smartboard Mirror • Voice Control")
    
    @st.fragment(run_every=2)
    def live_preview_section():
        data = load_shared_state()
        
        if data["mode"] == "explanation":
            # SINGLE HTML STRING to prevent Streamlit from breaking the div
            formatted_text = data["visual_display"].replace('\n', '<br>')
            html_card = f"""
            <div style="background: rgba(30,41,59,0.4); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 2rem; margin-top: 1rem; margin-bottom: 2rem;">
                <h4 style="color: #94a3b8; text-transform: uppercase; letter-spacing: 2px; font-size: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.8rem; margin-bottom: 1.5rem; margin-top:0;">
                    📡 Live Smartboard Mirror
                </h4>
                <div style="color: #f8fafc; font-size: 1.15rem; line-height: 1.8;">
                    {formatted_text}
                </div>
            </div>
            """
            st.markdown(html_card, unsafe_allow_html=True)
            
        elif data["mode"] == "quiz" and len(data["quiz_data"]) > 0:
            idx = data["quiz_index"]
            current_q = data["quiz_data"][idx]
            options_list = "".join([f"<li style='margin-bottom: 8px;'>{opt}</li>" for opt in current_q["options"]])
            
            html_card = f"""
            <div style="background: rgba(30,41,59,0.4); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 2rem; margin-top: 1rem; margin-bottom: 1rem;">
                <h4 style="color: #94a3b8; text-transform: uppercase; letter-spacing: 2px; font-size: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.8rem; margin-bottom: 1.5rem; margin-top:0;">
                    📡 Live Smartboard Mirror (Quiz Mode)
                </h4>
                <p style="color: #60a5fa; font-weight: bold; margin-bottom: 0.5rem; font-size: 0.9rem;">QUESTION {idx + 1} OF {len(data["quiz_data"])}</p>
                <p style="color: #f8fafc; font-size: 1.2rem; margin-bottom: 1.5rem;"><b>{current_q["question"]}</b></p>
                <ul style="color: #cbd5e1; font-size: 1.1rem; list-style-type: disc; margin-left: 20px;">
                    {options_list}
                </ul>
                <div style="background: rgba(16,185,129,0.15); color: #34d399; padding: 10px 20px; border-radius: 50px; display: inline-block; font-weight: 600; margin-top: 1rem; border: 1px solid rgba(16,185,129,0.3);">
                    🔑 Answer Key: Option {current_q["answer"]}
                </div>
            </div>
            """
            st.markdown(html_card, unsafe_allow_html=True)
            
            # Interactive Buttons handled natively by Streamlit BELOW the HTML card
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Previous Question", disabled=(idx == 0), use_container_width=True):
                    data["quiz_index"] -= 1
                    save_shared_state(data)
                    st.rerun()
            with col2:
                if st.button("Next Question →", disabled=(idx == len(data["quiz_data"]) - 1), use_container_width=True):
                    data["quiz_index"] += 1
                    save_shared_state(data)
                    st.rerun()
                    
    live_preview_section()
    
    # --- SECURE NATIVE MIC LAYOUT ---
    st.markdown("<br><hr style='border-color: rgba(255,255,255,0.1);'><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; font-weight: 600; font-size: 0.8rem; letter-spacing: 2px;'>HOLD TO SPEAK</p>", unsafe_allow_html=True)
    
    # Uses native columns to center the mic so Streamlit doesn't break the layout
    c1, c2, c3 = st.columns([1, 0.2, 1])
    with c2:
        audio_bytes = st.session_state.get("last_audio", None)
        new_audio_bytes = audio_recorder(text="", recording_color="#ef4444", neutral_color="#ffffff", icon_size="2x")
    
    status_container = st.empty()
    
    if new_audio_bytes and new_audio_bytes != audio_bytes:
        st.session_state["last_audio"] = new_audio_bytes
        
        with status_container.container():
            file_path = "temp_audio.wav"
            with open(file_path, "wb") as f:
                f.write(new_audio_bytes)
                
            with st.spinner("Processing voice command..."):
                transcript = transcribe_audio(file_path)
                
                if "assistant" not in transcript.lower():
                    st.warning("Wake word 'Assistant' was not detected in this command.")
                else:
                    st.success(f"Command acknowledged: '{transcript}'")
                    
                    with st.spinner("Updating classroom display..."):
                        ai_output = generate_smartboard_content(transcript)
                        clean_output = ai_output.replace("```json", "").replace("```", "").strip()
                        
                        try:
                            quiz_json = json.loads(clean_output)
                            if isinstance(quiz_json, list):
                                new_state = {
                                    "mode": "quiz",
                                    "visual_display": "",
                                    "quiz_data": quiz_json,
                                    "quiz_index": 0
                                }
                                save_shared_state(new_state)
                        except json.JSONDecodeError:
                            new_state = {
                                "mode": "explanation",
                                "visual_display": ai_output,
                                "quiz_data": [],
                                "quiz_index": 0
                            }
                            save_shared_state(new_state)