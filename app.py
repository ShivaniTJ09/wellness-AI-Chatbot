import os, io, tempfile
import streamlit as st
from openai import OpenAI
from gtts import gTTS

# ---------------------------- PAGE SETTINGS ----------------------------
st.set_page_config(page_title="Wellness.AI 🌿", page_icon="🧘", layout="centered")

# ---------------------------- STYLING ----------------------------
st.markdown("""
    <style>
    body {
        background: linear-gradient(180deg, #f7fff7 0%, #f0fff0 50%, #fffdf7 100%);
        font-family: "Segoe UI", sans-serif;
        color: #222;
    }
    .hero-section {
        background: linear-gradient(90deg, #d0f0c0 0%, #fefae0 100%);
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .hero-title {
        font-size: 34px;
        font-weight: bold;
        color: #005f4b;
        margin-bottom: 8px;
    }
    .hero-subtitle {
        font-size: 17px;
        font-style: italic;
        color: #444;
    }
    .signature {
        font-size: 14px;
        color: #555;
        margin-top: 10px;
    }
    .chat-container {
        background-color: rgba(255,255,255,0.8);
        border-radius: 20px;
        padding: 20px;
        margin-top: 10px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
    }
    .user-bubble {
        background-color: #DCF8C6;
        color: #222;
        padding: 10px 14px;
        border-radius: 15px;
        margin: 5px 0px 5px 40px;
        text-align: right;
        display: inline-block;
        max-width: 80%;
    }
    .bot-bubble {
        background-color: #E9E9EB;
        color: #222;
        padding: 10px 14px;
        border-radius: 15px;
        margin: 5px 40px 5px 0px;
        text-align: left;
        display: inline-block;
        max-width: 80%;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------- TOP BANNER ----------------------------
st.markdown("""
<div class="hero-section">
    <img src="https://cdn-icons-png.flaticon.com/512/706/706164.png" width="80">
    <div class="hero-title">Wellness.AI 🌿</div>
    <div class="hero-subtitle">Guided by Indian mindfulness and modern AI</div>
    <div class="signature">by <b>Shivani Jadhav</b></div>
</div>
""", unsafe_allow_html=True)

# ---------------------------- SYSTEM PROMPT ----------------------------
SYSTEM_PROMPT = (
    "You are a calm, empathetic Indian wellness guide. "
    "Answer in 2–4 short sentences. Draw on meditation, pranayama, yoga, Ayurveda, "
    "and Indian spiritual wisdom in simple, practical language. "
    "Avoid medical claims; suggest consulting professionals for serious issues."
)

# ---------------------------- OPENAI SETUP ----------------------------
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_KEY:
    st.error("OPENAI_API_KEY is missing. Set it in your environment.")
    st.stop()

client = OpenAI(api_key=OPENAI_KEY)

# ---------------------------- FUNCTIONS ----------------------------
def transcribe_with_whisper(path: str) -> str:
    with open(path, "rb") as f:
        tr = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            temperature=0
        )
    return tr.text.strip()

def chat_response(user_text: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        temperature=0.7,
        max_tokens=250,
    )
    return resp.choices[0].message.content.strip()

def synthesize_gtts(text: str, lang_code: str = "en", indian_accent: bool = True) -> io.BytesIO:
    tld = "co.in" if (lang_code == "en" and indian_accent) else "com"
    tts = gTTS(text=text, lang=lang_code, tld=tld, slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf

# ---------------------------- MAIN APP ----------------------------
st.markdown("### ✨ Ask your wellness question below:")
audio_file = st.file_uploader("🎤 Upload voice (WAV/MP3, 5–15s)", type=["wav", "mp3"])
typed = st.text_input("💬 Or type your question here")
lang_choice = st.selectbox("🎙️ Voice language for reply", ["English (India)", "Hindi"])
run = st.button("🌼 Ask Mindfully")

# ---------------------------- CHAT HISTORY ----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if st.button("🧹 Clear Chat"):
    st.session_state.chat_history = []
    st.experimental_rerun()

# ---------------------------- LOGIC ----------------------------
if run:
    if not audio_file and not typed:
        st.warning("Please upload audio or type something.")
        st.stop()

    user_text = typed.strip() if typed else ""
    if audio_file:
        with st.spinner("🎧 Listening to your voice…"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.name)[1]) as tmp:
                tmp.write(audio_file.read())
                tmp_path = tmp.name
            try:
                user_text = transcribe_with_whisper(tmp_path)
            finally:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    with st.spinner("💭 Reflecting mindfully…"):
        bot_text = chat_response(user_text)

    st.session_state.chat_history.append((user_text, bot_text))

# ---------------------------- CHAT DISPLAY ----------------------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for user_msg, bot_msg in st.session_state.chat_history:
    st.markdown(f'<div class="user-bubble">🧍‍♀️ {user_msg}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="bot-bubble">🤖 {bot_msg}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------- VOICE OUTPUT ----------------------------
if st.session_state.chat_history:
    last_bot_text = st.session_state.chat_history[-1][1]
    with st.spinner("🎵 Creating a natural Indian voice…"):
        if lang_choice.startswith("Hindi"):
            audio_fp = synthesize_gtts(last_bot_text, lang_code="hi")
        else:
            audio_fp = synthesize_gtts(last_bot_text, lang_code="en", indian_accent=True)
    st.audio(audio_fp, format="audio/mp3")

st.info("💡 Tip: Keep chatting naturally — your previous messages stay visible for continuity.")



