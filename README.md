# 📚 Real-Time RAG-Based Documents, Research and Thematic Analysis-chatbot-

Real-Time RAG-Based Document Research and Thematic Analysis Chatbot
This project implements a real-time chatbot powered by Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs) to perform intelligent document research across large datasets. It enables users to:
Upload and process multiple document types (PDF, DOCX, Images)
Perform semantic search across document content
Identify key themes and group related information
Generate detailed, cited responses to natural language queries
Explore insights interactively via a modern chat interface



A full-stack AI-powered chatbot that lets you upload documents (PDF, DOCX, images), extracts their content, stores embeddings, and allows you to ask questions about them using a Streamlit frontend and a FastAPI backend.

---

## 🚀 Features

- Upload and process PDF, DOCX, JPG, PNG files
- OCR for scanned documents and images
- Embedding and vector storage (ChromaDB)
- LLM-powered question answering (OpenAI, Groq, HuggingFace, etc.)
- Document and answer citation tracking
- Download extracted text and answers
- Database logging with SQLAlchemy and Alembic migrations

---

## 🗂️ Project Structure

```
chatbot_theme_identifier/
│
├── .env
├── requirements.txt
├── venv/
│
├── backend/
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── utils.py
│       ├── api/
│       │   ├── upload.py
│       │   ├── query.py
│       │   └── document_routes.py
│       ├── core/
│       │   ├── ocr.py
│       │   ├── embed.py
│       │   ├── wrapper.py
│       │   └── word.py
│       ├── db/
│       │   ├── session.py
│       │   └── models.py
│       ├── services/
│       │   ├── llm_service.py
│       │   └── vector_store.py
│      
│  
|   
│   
│   
│
├── alembic/
│   └── versions/
│
├──ui/
|    ├── app.py
|    ├── requirements.txt
|    └── Dockerfile
| 
└──  ├── alembic.ini
│    ├── requirements.txt
│    ├── Dockerfile
│    ├── test.db  






(add any additional files or folders here as needed)
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd chatbot_theme_identifier
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
.\venv\Scripts\activate   # On Windows
# source venv/bin/activate  # On macOS/Linux
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r backend/requirements.txt
pip install -r ui/requirements.txt
```

### 4. Configure Environment Variables

Edit `.env` in the project root and set your keys and paths, e.g.:
```
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
HF_TOKEN=your_huggingface_token
CHROMA_PERSIST_PATH=./chroma_store
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
SQLALCHEMY_DATABASE_URL=sqlite:///./test.db
```

### 5. (Optional) Set Up Database Migrations

If you change models, use Alembic:
```bash
cd backend
alembic revision --autogenerate -m "Describe your change"
alembic upgrade head
```

### 6. Start the Backend

```bash
cd backend
uvicorn app.main:app --reload
```

### 7. Start the Frontend

```bash
cd ui
streamlit run app.py
```

---

## 📝 Usage

- **Upload documents** in the Streamlit UI.
- **Ask questions** about the uploaded documents.
- **View answers, citations, and download results**.

---

## 🛠️ Troubleshooting

- **500 Internal Server Error**: Check backend logs for missing dependencies or database schema mismatches.
- **No such column error**: If you change models, run Alembic migrations or delete `test.db` for a fresh start.
- **Model access errors**: Make sure you have access to the Hugging Face model and have set your token.

---

## 📦 Tech Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **Database**: SQLite (SQLAlchemy ORM, Alembic migrations)
- **Vector Store**: ChromaDB
- **LLM**: Groq, HuggingFace
- **OCR**: pytesseract, pdf2image, Poppler

---

## 📄 License


---

## 🙋‍♂️ Contact

For questions or support, open an issue or contact the maintainer.