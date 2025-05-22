import streamlit as st
import requests
from PyPDF2 import PdfReader
from io import BytesIO
import os
import base64
import uuid
import pandas as pd

st.set_page_config(page_title="Document Chatbot", layout="wide")

# ✨ CUSTOM CSS FOR CREATIVE UI ✨
st.markdown("""
    <style>
    body {
        background-color: #f4f6f9;
    }
    .reportview-container {
        background: linear-gradient(to bottom, #f8fbff, #e0f0ff);
    }
    .sidebar .sidebar-content {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    h1, h2, h3 {
        color: #003366;
    }
    .stButton>button {
        color: white;
        background: linear-gradient(to right, #1f77b4, #3aafc9);
        border-radius: 8px;
        border: none;
        padding: 0.4em 1em;
    }
    .stButton>button:hover {
        background: #005f8e;
        color: white;
    }
    .chat-box {
        background-color: #ffffff;
        border-left: 5px solid #3aafc9;
        padding: 1em;
        margin-bottom: 10px;
        border-radius: 10px;
        box-shadow: 1px 2px 6px rgba(0,0,0,0.1);
    }
    .chat-question {
        color: #1f3b57;
        font-weight: bold;
    }
    .chat-answer {
        margin-top: 0.5em;
        color: #333333;
    }
    .uploaded-file-box {
        background-color: #ffffff;
        padding: 0.7em;
        border-left: 4px solid #0077b6;
        margin-bottom: 0.5em;
        border-radius: 8px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
    }
    a.download-button {
        display: inline-block;
        background: #1f77b4;
        color: white;
        padding: 0.6em 1.2em;
        text-decoration: none;
        border-radius: 8px;
        margin-top: 10px;
    }
    a.download-button:hover {
        background: #0d5d9f;
    }
    </style>
""", unsafe_allow_html=True)

# Backend URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

#BACKEND_URL = os.getenv("BACKEND_URL", "https://pranjal-arya-wasserstoff-aiinterntask.onrender.com")


# Initialize session state
def init_state(key, default):
    if key not in st.session_state:
        st.session_state[key] = default

init_state("chat_history", [])
init_state("recent_docs", [])

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712027.png", width=100)
    st.markdown("### Options")
    
    if st.button("Clear Chat"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Session cleared. Ready for fresh upload.")
        try:
            st.experimental_rerun()
        except AttributeError:
            st.info("Please refresh the page to start a new session.")
    
    st.markdown("---")
    st.markdown("### Recent Activity")
    for doc in st.session_state.recent_docs[-5:][::-1]:
        st.markdown(f"📄 {doc}")
    st.markdown("---")
    st.markdown("### Info")
    st.info("Gen-AI Internship Task — Document Chatbot")

# Header
st.markdown("## 📚 Document Upload and Q&A Chatbot")

# Document Upload Section
st.subheader("Step 1: Upload Documents")
uploaded_files = st.file_uploader(
    "Choose documents (PDF, JPG, PNG, DOCX)",
    type=["pdf", "jpg", "jpeg", "png", "docx"],
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded in uploaded_files:
        ext = os.path.splitext(uploaded.name)[1].lower()
        buffer = BytesIO(uploaded.read())
        file_id = str(uuid.uuid4())

        try:
            if ext == ".pdf":
                reader = PdfReader(buffer)
                num_pages = len(reader.pages)
            else:
                num_pages = "-"
            size_kb = len(buffer.getvalue()) / 1024
            st.markdown(f"""
            <div class="uploaded-file-box">
                <strong>📄 {uploaded.name}</strong><br>
                Pages: {num_pages} | Size: {size_kb:.1f} KB
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error reading file: {e}")
            continue

        buffer.seek(0)
        content_type = {
            ".pdf": "application/pdf",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        }.get(ext, "application/octet-stream")
        files = {"file": (uploaded.name, buffer, content_type)}

        with st.spinner("Uploading and processing..."):
            try:
                resp = requests.post(f"{BACKEND_URL}/upload/", files=files)
            except Exception as e:
                st.error(f"Backend error: {e}")
                continue

        buffer.close()
        if resp and resp.ok:
            data = resp.json()
            doc_id = data.get("doc_id")
            full_text = data.get("full_text", "")

            st.success(f"Uploaded: {uploaded.name} (ID: {doc_id})")
            st.session_state.recent_docs.append(uploaded.name)

            with st.expander(f"📄 View extracted text from {uploaded.name}", expanded=False):
                if full_text.strip():
                    st.write(full_text)
                else:
                    st.warning("No text was extracted from this document.")
        else:
            st.error(resp.text if resp else "Unknown upload error")

# Question Section
st.markdown("---")
st.subheader("Step 2: Ask a Question")
question = st.text_input("What do you want to know from the uploaded documents?")
if st.button("Ask Question"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        payload = {"question": question.strip(), "top_k": 5}
        with st.spinner("Thinking..."):
            try:
                resp = requests.post(f"{BACKEND_URL}/query/", json=payload)
            except Exception as e:
                st.error(f"Query failed: {e}")
                resp = None

        if resp and resp.ok:
            result = resp.json()
            st.session_state.chat_history.append((question, result))
            st.success("Answer generated below ⬇️")
        elif resp:
            st.error(resp.text)

# Display Chat History and Enhanced Responses
if st.session_state.chat_history:
    for q, res in reversed(st.session_state.chat_history):
        st.markdown(f"""
        <div class="chat-box">
            <div class="chat-question">❓ Q: {q}</div>
        """, unsafe_allow_html=True)

        # 1. Show per-document table if available
        if table := res.get("doc_table"):
            df = pd.DataFrame(table)
            df = df.rename(columns={
                "doc_id": "Document ID",
                "answer": "Extracted Answer",
                "citation": "Citation"
            })
            st.table(df)

        # 2. Show synthesized summary
        if summary := res.get("synthesized_summary"):
            st.markdown(f'<div class="chat-answer">🧠 <strong>Synthesized Response:</strong> {summary}</div>', unsafe_allow_html=True)

        # 3. Fallback plain answer
        if not table and res.get("answer"):
            st.markdown(f'<div class="chat-answer">💬 A: {res.get("answer")}</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)  # Close chat-box
        st.markdown("---")

# Optional: download entire chat history
if st.session_state.chat_history:
    combined = "\n".join([f"Q: {q}\nA: {r.get('answer')}\n" for q, r in st.session_state.chat_history])
    b64 = base64.b64encode(combined.encode()).decode()
    st.markdown(
        f'<a class="download-button" href="data:file/txt;base64,{b64}" download="chat_history.txt">📥 Download Chat History</a>',
        unsafe_allow_html=True
    )
