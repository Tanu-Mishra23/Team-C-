import streamlit as st
from PIL import Image
import pytesseract
import ollama

# Set your Tesseract executable path (your path)
# NOTE: This path is specific to your local machine and might need adjustment.
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Dell\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

def ocr_and_query(img: Image.Image, question: str) -> str:
    """Extract text via OCR and query the text-only model."""
    try:
        extracted = pytesseract.image_to_string(img)
    except Exception:
        # Fallback in case of a Tesseract error
        extracted = "OCR extraction failed."

    prompt = (
        "Below is the text extracted from an image (OCR). "
        "Then there is the user question. "
        "Answer the user question using the extracted text and reasoning.\n\n"
        f"Extracted text:\n{extracted}\n\n"
        f"User question: {question}"
    )
    # Use the appropriate model for text-only processing
    resp = ollama.chat(
        model="llama3.2:1b",
        messages=[{"role": "user", "content": prompt}]
    )
    return resp["message"]["content"]

def general_chat(user_input: str) -> str:
    """Query the text-only model for general conversation."""
    try:
        resp = ollama.chat(
            model="llama3.2:1b",
            messages=[{"role": "user", "content": user_input}],
        )
        return resp["message"]["content"]
    except Exception as e:
        st.error("Error with LLM: " + str(e))
        return "An error occurred while connecting to the LLM."


def main():
    st.set_page_config(page_title="Unified Chat & OCR Assistant", layout="wide")

    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "history_text" not in st.session_state:
        st.session_state.history_text = []
    if "history_ocr" not in st.session_state:
        st.session_state.history_ocr = []

    # Login screen
    if not st.session_state.logged_in:
        st.title("Login to Chatbot & OCR")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == "admin" and password == "1234":
                st.session_state.logged_in = True
                st.success("Login successful!")
                st.rerun() # Rerun to switch to the main app view
            else:
                st.error("Invalid username / password")
        st.stop()

    st.title(" Chatbot + OCR Assistant 💬")

    # Sidebar: history toggle and clear
    with st.sidebar:
        st.subheader("Assistant History")
        show_history = st.checkbox("🕘 Show History", value=False, key="show_history")
        
        if show_history:
            # Display history, combining both types for simplicity
            st.markdown("---")
            st.markdown("**Text Chat History**")
            for q, a in reversed(st.session_state.history_text):
                st.markdown(f"**You:** {q}\n\n**Bot:** {a}\n---")
            
            st.markdown("**OCR / Image History**")
            for q, a in reversed(st.session_state.history_ocr):
                st.markdown(f"**You:** {q}\n\n**Bot:** {a}\n---")
        
        if st.button("Clear All History", key="clear_history"):
            st.session_state.history_text = []
            st.session_state.history_ocr = []
            st.rerun()
            
    # --- Main Interaction Area ---

    # 1. Image Upload
    uploaded_file = st.file_uploader(
        "Upload an image (PNG, JPG, JPEG) for OCR or leave blank for general chat:", 
        type=["png", "jpg", "jpeg"], 
        key="main_file_uploader"
    )

    is_ocr_mode = uploaded_file is not None

    if is_ocr_mode:
        # OCR Mode
        st.header("Image Question & Answering (OCR Mode)")
        
        try:
            img = Image.open(uploaded_file).convert("RGB")
            st.image(img, caption="Uploaded Image", use_column_width=True)
        except Exception as e:
            st.error("Cannot open image: " + str(e))
            return # Stop processing if image can't be opened

        # 2. Text Input for Question (OCR Mode)
        ocr_question = st.text_input("Ask a question about the content of this image:", key="unified_input_ocr")
        
        if st.button("Get Answer (OCR)", key="unified_send_ocr"):
            if not ocr_question.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner("Generating answer using OCR and LLM..."):
                    answer = ocr_and_query(img, ocr_question)
                
                st.subheader("AI Answer (Based on Image)")
                st.markdown(answer)
                st.session_state.history_ocr.append((ocr_question, answer))
                
                # Optional: Show extracted text below the answer for debugging/clarity
                # with st.expander("Show Extracted Text"):
                #     extracted = pytesseract.image_to_string(img)
                #     st.text_area("Extracted Text", value=extracted, height=150)

    else:
        # General Chat Mode
        st.header("General Chat ")
        
        # 2. Text Input for Question (Chat Mode)
        user_input = st.text_input("Ask something (general question):", key="unified_input_chat")
        
        if st.button("Send ", key="unified_send_chat"):
            if user_input.strip():
                with st.spinner("Thinking..."):
                    answer = general_chat(user_input)
                
                st.subheader("AI Answer")
                st.markdown(answer)
                st.session_state.history_text.append((user_input, answer))
            else:
                st.warning("Please enter a question.")


if __name__ == "__main__":
    main()