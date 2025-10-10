import os
from datetime import datetime
import streamlit as st
import easyocr

# -------------------------------
# APP CONFIGURATION
# -------------------------------
st.set_page_config(
    page_title="Smart OCR & Chatbot Assistant",
    page_icon="🧠",
    layout="wide",
)

# -------------------------------
# SIDEBAR - ABOUT & THEME
# -------------------------------
with st.sidebar:
    st.title("📘 About the Project")
    st.markdown("""
    **Smart OCR Chatbot**  
    This intelligent Streamlit app can:
    - Extract text from images using OCR  
    - Interact using a rule-based chatbot  
    - Work fast even without GPU  

    Developed for **Infosys Springboard Final Milestone**.
    """)
    st.markdown("---")
    st.markdown("**Developed by:** Santhiya & Team 🧩")  
    st.markdown("**Year:** 2025")  
    st.markdown("**License:** MIT License 🪪")
    st.markdown("---")
    st.info("💡 Tip: Upload a clear image (English text preferred) for best OCR accuracy!")

# -------------------------------
# LOAD OCR MODEL (CACHED)
# -------------------------------
@st.cache_resource
def load_ocr():
    # English only, CPU mode
    return easyocr.Reader(['en'], gpu=False)

reader = load_ocr()

# -------------------------------
# TITLE & HEADER
# -------------------------------
st.title("🧠 Smart OCR & Chatbot Assistant")
st.markdown("### Extract, Understand, and Interact with Your Images Effortlessly")

st.markdown("---")

# -------------------------------
# IMAGE UPLOAD SECTION
# -------------------------------
st.subheader("📤 Step 1: Upload an Image")

col1, col2 = st.columns([1, 1.2])
extracted_text = ""

with col1:
    uploaded_file = st.file_uploader(
        "Choose an image file (JPG, PNG, JPEG)",
        type=["png", "jpg", "jpeg"]
    )
    if uploaded_file:
        st.image(uploaded_file, caption="📸 Uploaded Image", use_container_width=True)

with col2:
    if uploaded_file:
        with st.spinner("🔍 Extracting text... Please wait"):
            try:
                # Perform OCR
                file_bytes = uploaded_file.read()
                result = reader.readtext(file_bytes, detail=0)

                if result:
                    extracted_text = "\n".join(result)
                    st.success("✅ Text successfully extracted!")
                    st.text_area("📝 Extracted Text", extracted_text, height=250)

                    # Save extracted text file
                    os.makedirs("outputs", exist_ok=True)
                    filename = f"outputs/ocr_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(extracted_text)

                    st.download_button(
                        "💾 Download Extracted Text",
                        data=extracted_text,
                        file_name="ocr_text.txt",
                        mime="text/plain"
                    )
                else:
                    st.warning("⚠️ No readable text detected in the image.")
            except Exception as e:
                st.error(f"❌ OCR failed: {e}")
    else:
        st.info("📂 Please upload an image to begin text extraction.")

st.markdown("---")

# -------------------------------
# CHATBOT SECTION
# -------------------------------
st.subheader("💬 Step 2: Chatbot Assistant")

user_query = st.text_input("💭 Ask something about the extracted text:")
ask_button = st.button("🚀 Ask the Chatbot")

if ask_button:
    if not uploaded_file:
        st.warning("⚠️ Please upload an image and extract text first!")
    elif not user_query.strip():
        st.info("💡 Type a question to get started.")
    else:
        lower_q = user_query.lower()
        response = ""

        # Rule-based chatbot responses
        if "what" in lower_q:
            response = f"The text mainly says:\n\n{extracted_text[:250]}..."
        elif "who" in lower_q:
            response = "👤 I cannot detect persons, only textual data from the image."
        elif "hello" in lower_q or "hi" in lower_q:
            response = "👋 Hello there! Upload an image and I’ll extract the text for you."
        elif "how" in lower_q:
            response = "⚙️ I use EasyOCR to detect and extract readable text from your image efficiently."
        elif "why" in lower_q:
            response = "🤔 Because automating text extraction saves time and prevents manual errors!"
        elif "where" in lower_q:
            response = "📍 I work locally on your system without requiring cloud or GPU!"
        else:
            response = f"Here’s a part of your extracted text:\n\n{extracted_text[:300]}..."

        # Display chatbot response
        st.success("🤖 Chatbot Response:")
        st.info(response)

# -------------------------------
# FOOTER SECTION
# -------------------------------
st.markdown("---")
colA, colB, colC = st.columns(3)
with colA:
    st.markdown("**Smart OCR Chatbot © 2025**")
with colB:
    st.markdown("Developed by: Santhiya & Team 🎓")
with colC:
    st.markdown("[MIT License](https://opensource.org/licenses/MIT)")

st.caption("🚀 A Final Milestone Submission for Infosys Springboard Virtual Internship 6.0")
