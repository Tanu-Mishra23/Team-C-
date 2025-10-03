import streamlit as st
import ollama
from openai import OpenAI
import os
from easyocr_helper import extract_text_from_image   # OCR helper

# --------------------------
# Configure Streamlit page
# --------------------------
st.set_page_config(
    page_title="Ollama + DeepSeek Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------
# Upload directory
# --------------------------
UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Initialize session state
# --------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "saved_chats" not in st.session_state:
    st.session_state.saved_chats = []
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "llama3.2:1b"  # default model

# --------------------------
# DeepSeek API setup
# --------------------------
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
deepseek_client = None
if DEEPSEEK_API_KEY:
    deepseek_client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com"
    )

def chat_with_deepseek(messages):
    response = deepseek_client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )
    return response.choices[0].message.content

# --------------------------
# Main layout
# --------------------------
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    if not st.session_state.messages:
        st.markdown("\n\n\n")
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            st.subheader("🤖 Ollama + DeepSeek Chatbot")
            st.write("How can I help you today?")

# --------------------------
# Model options
# --------------------------
model_options = {
    "Llama 3.2 1B (Fast)": "llama3.2:1b",
    "Llama 3.1 8B (Better)": "llama3.1:8b",
    "DeepSeek Coder 1.3B (Lightweight)": "deepseek-coder:1.3b",
    "DeepSeek Coder 6.7B (Powerful)": "deepseek-coder:6.7b",
    "DeepSeek API (Cloud)": "deepseek-api",
}

# --------------------------
# Show old chat history
# --------------------------
with col2:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --------------------------
# Input row (text + file uploader)
# --------------------------
with col2:
    col_in1, col_in2 = st.columns([4, 1])

    with col_in1:
        user_input = st.text_input("Type your message...", key="chat_text")

    with col_in2:
        uploaded_file = st.file_uploader(
            "📤",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed"
        )

# --------------------------
# Handle uploaded image
# --------------------------
if uploaded_file is not None:
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)

    # Save uploaded file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    with st.spinner("🔎 Extracting text from image..."):
        try:
            ocr_text = extract_text_from_image(file_path)
        except Exception as e:
            st.error(f"OCR error: {e}")
            ocr_text = ""

    st.image(file_path, caption="Uploaded Image", use_column_width=True)
    st.success(f"📜 OCR Text: {ocr_text}")

    # Use OCR text as input
    user_input = ocr_text
# Process text or OCR input
# --------------------------
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with col2:
        with st.chat_message("user"):
            st.markdown(user_input)

    if len(st.session_state.messages) == 1:
        chat_title = user_input[:50] + "..." if len(user_input) > 50 else user_input
        st.session_state.current_chat_id = len(st.session_state.saved_chats)

    with col2:
        with st.chat_message("assistant"):
            with st.spinner("Just a moment..."):
                try:
                    if st.session_state.selected_model == "deepseek-api":
                        if deepseek_client is None:
                            assistant_response = "⚠️ DeepSeek API key not found. Please set DEEPSEEK_API_KEY."
                        else:
                            assistant_response = chat_with_deepseek([
                                {"role": msg["role"], "content": msg["content"]}
                                for msg in st.session_state.messages
                            ])
                    else:
                        response = ollama.chat(
                            model=st.session_state.selected_model,
                            messages=[
                                {"role": msg["role"], "content": msg["content"]}
                                for msg in st.session_state.messages
                            ]
                        )
                        assistant_response = response.get("message", {}).get("content", "")

                    st.markdown(assistant_response)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_response
                    })

                    if st.session_state.current_chat_id is not None:
                        if st.session_state.current_chat_id < len(st.session_state.saved_chats):
                            st.session_state.saved_chats[st.session_state.current_chat_id]["messages"] = st.session_state.messages.copy()
                        else:
                            chat_title = st.session_state.messages[0]["content"][:50] + "..." if len(st.session_state.messages[0]["content"]) > 50 else st.session_state.messages[0]["content"]
                            st.session_state.saved_chats.append({
                                "title": chat_title,
                                "messages": st.session_state.messages.copy()
                            })

                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
# --------------------------
# Sidebar
# --------------------------
with st.sidebar:
    st.markdown("### 🤖 Model")

    names = list(model_options.keys())
    values = list(model_options.values())
    try:
        default_index = values.index(st.session_state.selected_model)
    except ValueError:
        default_index = 0

    selected_model_name = st.selectbox(
        "Select Model:",
        options=names,
        index=default_index,
        label_visibility="collapsed"
    )
    st.session_state.selected_model = model_options[selected_model_name]

    st.caption("Backend: Ollama + DeepSeek")
    st.divider()

    if st.button("➕ New Chat", use_container_width=True):
        if st.session_state.messages:
            if st.session_state.current_chat_id is not None:
                if st.session_state.current_chat_id < len(st.session_state.saved_chats):
                    st.session_state.saved_chats[st.session_state.current_chat_id]["messages"] = st.session_state.messages.copy()
                else:
                    chat_title = st.session_state.messages[0]["content"][:50] + "..." if len(st.session_state.messages[0]["content"]) > 50 else st.session_state.messages[0]["content"]
                    st.session_state.saved_chats.append({
                        "title": chat_title,
                        "messages": st.session_state.messages.copy()
                    })
        st.session_state.messages = []
        st.session_state.current_chat_id = None
        st.rerun()

    st.markdown("### 🔍 Search")
    search_query = st.text_input(
        "Search in conversation:",
        placeholder="Search in Chats...",
        label_visibility="collapsed"
    )

    if search_query and st.session_state.saved_chats:
        matching_chats = []
        for chat_idx, chat in enumerate(st.session_state.saved_chats):
            if search_query.lower() in chat["title"].lower():
                matching_chats.append((chat_idx, chat))

        if matching_chats:
            st.caption(f"Found {len(matching_chats)} chats:")
            for chat_idx, chat in matching_chats[:3]:
                if st.button(f"🔍 {chat['title']}", key=f"search_{chat_idx}", use_container_width=True):
                    st.session_state.messages = chat["messages"].copy()
                    st.session_state.current_chat_id = chat_idx
                    st.rerun()
        else:
            st.caption("No chats found")

    st.divider()
    st.markdown("### 💬 Recent Chats")

    if st.session_state.saved_chats:
        st.caption(f"Saved chats: {len(st.session_state.saved_chats)}")
        recent_chats = st.session_state.saved_chats[-5:]
        for i, chat in enumerate(reversed(recent_chats)):
            chat_index = len(st.session_state.saved_chats) - 1 - i
            if st.button(f"{chat['title']}", key=f"chat_{chat_index}", use_container_width=True):
                st.session_state.messages = chat["messages"].copy()
                st.session_state.current_chat_id = chat_index
                st.rerun()
    else:
        st.caption("No saved chats yet")

    if st.session_state.messages:
        st.caption(f"Current: {len(st.session_state.messages)} messages")
