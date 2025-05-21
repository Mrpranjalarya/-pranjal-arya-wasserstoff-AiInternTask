# backend/app/services/llm_service.py

import os
import json
import logging
from typing import Dict, List, Any

from langchain.chains import RetrievalQA, LLMChain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.vectorstores.base import VectorStoreRetriever
from langchain_core.documents import Document as LangDocument

from app.services.vector_store import load_vector_store

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

_cached_llm: ChatGroq = None

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")

MAX_INPUT_TOKENS = 512
MAX_THEME_TOKENS = 256

def truncate_text(text: str, max_tokens: int = MAX_INPUT_TOKENS) -> str:
    words = text.split()
    return ' '.join(words[:max_tokens])

def get_llm() -> ChatGroq:
    global _cached_llm
    if _cached_llm:
        return _cached_llm

    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set in the environment.")

    logger.debug(f"[get_llm] Using Groq model: {GROQ_MODEL}")
    _cached_llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model_name=GROQ_MODEL,
        temperature=0.7
    )
    return _cached_llm

# Prompts and Chains
doc_qa_prompt = PromptTemplate(
    input_variables=["doc_text", "question"],
    template='''You are a legal assistant.
Document:
"""{doc_text}"""
Question: {question}

Give:
- Extracted Answer (short)
- Citation (e.g. "Page 2, Para 1")

Respond in JSON: {{ "answer": "...", "citation": "..." }}
'''
)
doc_qa_chain = LLMChain(llm=get_llm(), prompt=doc_qa_prompt)

synth_prompt = PromptTemplate(
    input_variables=["findings_list"],
    template='''Summarize the findings below into clear themes. Group documents by IDs.

Findings:
{findings_list}

Return a markdown summary grouped by theme.
'''
)
synth_chain = LLMChain(llm=get_llm(), prompt=synth_prompt)

# Main method
def generate_answer(vector_store_path: str, question: str) -> Dict[str, Any]:
    logger.debug(f"[generate_answer] Received question: {question}")
    try:
        db = load_vector_store(vector_store_path)
        try:
            count = db._collection.count()
            logger.debug(f"[generate_answer] Vector store contains {count} vectors")
        except Exception:
            pass
    except Exception as e:
        logger.error(f"[generate_answer] Failed to load vector store: {e}")
        return fallback_answer("Vector store could not be loaded.")

    try:
        retriever: VectorStoreRetriever = db.as_retriever(search_kwargs={"k": 4})
        docs = retriever.get_relevant_documents(question)
        logger.debug(f"[generate_answer] Retrieved {len(docs)} documents")
        for i, doc in enumerate(docs):
            snippet = doc.page_content[:80].replace("\n", " ")
            logger.debug(f"  Doc {i}: id={doc.metadata.get('doc_id')} snippet='{snippet}'")
        if not docs:
            return fallback_answer("No relevant documents found.")
    except Exception as e:
        logger.error(f"[generate_answer] Retriever error: {e}")
        return fallback_answer("Failed to retrieve relevant documents.")

    try:
        llm = get_llm()
        qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)
        answer = qa_chain.run(question)
        logger.debug(f"[generate_answer] QA chain returned: {answer!r}")
        if not answer:
            answer = "No answer could be generated."
    except Exception as e:
        logger.error(f"[generate_answer] LLM generation failed: {e}", exc_info=True)
        return fallback_answer("Failed to generate answer.")

    citations: List[Dict[str, Any]] = []
    for i, chunk in enumerate(docs):
        md = chunk.metadata
        citations.append({
            "doc_id": md.get("doc_id", f"doc_{i}"),
            "chunk_id": md.get("chunk_id", f"chunk_{i}"),
            "start_char": md.get("start"),
            "end_char": md.get("end"),
            "snippet": chunk.page_content[:200]
        })

    try:
        themes = identify_themes(answer)
        logger.debug(f"[generate_answer] Identified themes: {themes}")
    except Exception as e:
        logger.warning(f"[generate_answer] Theme extraction failed: {e}")
        themes = []

    try:
        doc_answers = qa_per_document(docs, question)
        summary = synthesize_findings(doc_answers)
    except Exception as e:
        logger.warning(f"[generate_answer] Per-document QA or synthesis failed: {e}")
        doc_answers, summary = [], ""

    return {
        "answer": answer,
        "citations": citations,
        "themes": themes,
        "doc_table": doc_answers,
        "synthesized_summary": summary
    }

def fallback_answer(error_msg: str) -> Dict[str, Any]:
    return {
        "answer": f"Error: {error_msg}",
        "citations": [],
        "themes": [],
        "doc_table": [],
        "synthesized_summary": ""
    }

def qa_per_document(docs: List[LangDocument], question: str) -> List[Dict[str, Any]]:
    results = []
    for doc in docs:
        try:
            doc_text = doc.page_content
            response = doc_qa_chain.run({"doc_text": doc_text, "question": question})
            try:
                parsed = json.loads(response)
            except Exception:
                parsed = {"answer": response, "citation": ""}
            results.append({
                "doc_id": doc.metadata.get("doc_id"),
                "chunk_id": doc.metadata.get("chunk_id"),
                "answer": parsed.get("answer", ""),
                "citation": parsed.get("citation", ""),
                "snippet": doc_text[:200]
            })
        except Exception as e:
            logger.warning(f"[qa_per_document] Failed for doc_id={doc.metadata.get('doc_id')}: {e}")
            results.append({
                "doc_id": doc.metadata.get("doc_id"),
                "chunk_id": doc.metadata.get("chunk_id"),
                "answer": "",
                "citation": "",
                "snippet": doc.page_content[:200]
            })
    return results

def synthesize_findings(doc_answers: List[Dict[str, Any]]) -> str:
    findings_list = []
    for doc in doc_answers:
        findings_list.append(
            f"Doc ID: {doc.get('doc_id')}, Chunk ID: {doc.get('chunk_id')}, "
            f"Answer: {doc.get('answer')}, Citation: {doc.get('citation')}"
        )
    findings_str = "\n".join(findings_list)
    try:
        summary = synth_chain.run({"findings_list": findings_str})
        return summary
    except Exception as e:
        logger.warning(f"[synthesize_findings] Synthesis failed: {e}")
        return ""

def identify_themes(full_text: str) -> List[str]:
    truncated = truncate_text(full_text, max_tokens=MAX_THEME_TOKENS)
    prompt = (
        "Analyze the following answer and extract the key themes as a simple list:\n\n"
        f"{truncated}\n\nReturn the themes as one theme per line."
    )
    try:
        llm = get_llm()
        response = llm.invoke(prompt)
        response_text = str(response)
        logger.debug(f"[identify_themes] Raw LLM response for themes: {response_text}")
    except Exception as e:
        logger.error(f"[identify_themes] Theme extraction error: {e}")
        return []

    return [line.strip("-•* \t") for line in response_text.splitlines() if line.strip()]
