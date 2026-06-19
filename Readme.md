# 🏫 AI Classroom Co-Pilot

A Voice-Enabled Teaching Assistant designed for government schools, featuring a dual-screen architecture that separates student visualizations from teacher controls.

## 🚀 Features
* **Omni-Channel Voice Control:** Teachers can trigger lessons or quizzes completely hands-free.
* **Dual-View Architecture:** * `?view=student`: A clean, high-contrast, distraction-free smart board display.
  * `?view=teacher`: A mobile-friendly remote control with live previews and hidden answer keys.
* **Instant Concept Simplification:** Converts complex queries into bite-sized Hinglish bullet points with relatable analogies.
* **Smart Quizzing:** Generates structured JSON flashcards on the fly.
* **Domain Guardrails:** Strictly enforces educational topics, automatically rejecting inappropriate prompts.

## 🛠 Tech Stack
* **Frontend:** Streamlit (Custom CSS for Premium EdTech UI)
* **Speech-to-Text:** Groq (Whisper-large-v3 for sub-second transcription)
* **LLM Engine:** Google Gemini (gemini-2.5-flash for native Hinglish and JSON enforcement)

## 💻 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone [Your-GitHub-Repo-URL]
   cd cdf-ai-assistant