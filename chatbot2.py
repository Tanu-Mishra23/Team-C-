import streamlit as st
import requests
import pyttsx3
import json

# ---------- API Call ----------
def get_model_response(user_input, model_name):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model_name,
        "prompt": user_input
    }
    response = requests.post(url, json=payload, stream=True)
    output = ""
    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            if "response" in data:
                output += data["response"]
    return output.strip()

# ---------- Voice ----------
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# ---------- UI ----------
st.set_page_config(page_title="Chatbot", layout="wide")

# Sidebar: history + model select
st.sidebar.title("💬 Chat History")
if "history" not in st.session_state:
    st.session_state.history = []

# Model selection (default = Ollama)
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Choose Model")
model_choice = st.sidebar.radio(
    "Select model:",
    ("llama3.1:8b", "deepseek-r1:7b"),
    index=0
)

# Show history in sidebar
for chat in st.session_state.history:
    st.sidebar.markdown(f"**You:** {chat['user']}")
    st.sidebar.markdown(
        f"🤖 **{chat['model']}**:\n\n{chat['bot']}"
    )
    st.sidebar.divider()

st.title("🤖 Chatbot")

# Chat input
message = st.chat_input("Enter your message")
if message:
    st.session_state.user_input = message

# Process input
if st.session_state.get("user_input"):
    user_msg = st.session_state.user_input
    bot_response = get_model_response(user_msg, model_choice)

    # Save history
    st.session_state.history.append({
        "user": user_msg,
        "bot": bot_response,
        "model": model_choice
    })

    st.session_state.user_input = None

# Display main chat
for i, chat in enumerate(st.session_state.history):
    with st.chat_message("user"):
        st.write(chat["user"])
    with st.chat_message("assistant"):
        # 👇 remove model name, show only bot reply
        st.markdown(chat["bot"])  
        if st.checkbox(f"🔊 Read response", key=f"voice_{i}"):
            speak(chat["bot"])
