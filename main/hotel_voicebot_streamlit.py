import streamlit as st
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
import time
import google.api_core.exceptions

# -----------------------------
# CONFIG
# -----------------------------
genai.configure(api_key="API_KEY")  
model = genai.GenerativeModel("models/gemini-2.5-flash")

# -----------------------------
# Text-to-Speech
# -----------------------------
def speak(text):
    """Speaks a given text using pyttsx3 safely."""
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except RuntimeError:
        time.sleep(1)
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

# -----------------------------
# Voice Input
# -----------------------------
def listen():
    """Listen from mic and return recognized speech."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎤 Listening...")
        audio = r.listen(source, phrase_time_limit=8)
    try:
        text = r.recognize_google(audio)
        st.write(f"🗣️ You said: {text}")
        return text
    except sr.UnknownValueError:
        st.warning("Sorry, I couldn't understand that.")
        return ""
    except sr.RequestError:
        st.error("Speech service unavailable.")
        return ""

# -----------------------------
# Safe Gemini Message Send
# -----------------------------
def safe_send_message(text):
    """Send message with retry on 429 error."""
    retries = 3
    for i in range(retries):
        try:
            return st.session_state.chat.send_message(text).text
        except google.api_core.exceptions.ResourceExhausted:
            if i < retries - 1:
                st.warning("⚠️ Gemini is busy — retrying in 5 seconds...")
                time.sleep(5)
            else:
                st.error("Gemini API quota exceeded. Please try again later.")
                return "Sorry, the system is busy right now. Please try again in a minute."

# -----------------------------
# Initialize Session
# -----------------------------
if "conversation" not in st.session_state:
    st.session_state.conversation = []
    st.session_state.started = False
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.auto_listen = False

st.set_page_config(page_title="Hotel Voice Bot", page_icon="🏨")
st.title("🏨 Hotel Voice Bot")

# -----------------------------
# Chat Display
# -----------------------------
for message in st.session_state.conversation:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------
# Greet User Initially
# -----------------------------
if not st.session_state.started:
    greeting = "Hello! Welcome to Hotel Assistant. How can I help you today? You can speak or type your message below."
    st.session_state.conversation.append({"role": "assistant", "content": greeting})
    with st.chat_message("assistant"):
        st.markdown(greeting)
    speak(greeting)
    st.session_state.started = True

# -----------------------------
# Handle Auto-Listen Response
# -----------------------------
if st.session_state.auto_listen:
    st.write("🎤 Auto listening for your reply...")
    auto_text = listen()
    if auto_text:
        st.session_state.conversation.append({"role": "user", "content": auto_text})
        st.chat_message("user").markdown(auto_text)
        reply = safe_send_message(auto_text)
        st.session_state.conversation.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""
            for chunk in reply.split():
                full_response += chunk + " "
                placeholder.markdown(full_response + "▌")
                time.sleep(0.04)
            placeholder.markdown(full_response)
        
        speak(reply)
        st.session_state.auto_listen = True
        st.rerun()
    else:
        st.session_state.auto_listen = False

# -----------------------------
# Text Input Box
# -----------------------------
user_input = st.text_input("💬 Type your message and press Enter:")

# -----------------------------
# Voice and Restart Buttons
# -----------------------------
col1, col2 = st.columns(2)
with col1:
    if st.button("🎤 Speak"):
        spoken_text = listen()
        if spoken_text:
            user_input = spoken_text

with col2:
    if st.button("🔄 Restart Chat"):
        st.session_state.conversation = []
        st.session_state.started = False
        st.session_state.chat = model.start_chat(history=[])
        st.session_state.auto_listen = False
        st.rerun()

# -----------------------------
# Process User Input (Manual or Voice)
# -----------------------------
if user_input and not st.session_state.auto_listen:
    st.session_state.conversation.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)
    reply = safe_send_message(user_input)
    st.session_state.conversation.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        for chunk in reply.split():
            full_response += chunk + " "
            placeholder.markdown(full_response + "▌")
            time.sleep(0.04)
        placeholder.markdown(full_response)

    speak(reply)
    st.session_state.auto_listen = True
    st.rerun()