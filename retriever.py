"""
rag/retriever.py
RAG retrieval layer — loads FAISS index and retrieves relevant chunks.
Caches vector store in Streamlit session to avoid reloading on every request.
"""

import streamlit as st
from pathlib import Path
from utils.logger import logger, log_rag

VECTOR_STORE_PATH = "rag/vector_store"
EMBEDDING_MODEL   = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K             = 4   # number of chunks to retrieve

try:
    from langchain_community.vectorstores import FAISS
    from langchain_community.embeddings import HuggingFaceEmbeddings
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False


@st.cache_resource(show_spinner="📚 Loading Celonis knowledge base…")
def load_vector_store():
    """Load FAISS vector store — cached across all sessions."""
    if not RAG_AVAILABLE:
        logger.warning("LangChain/FAISS not installed — RAG disabled")
        return None

    store_path = Path(VECTOR_STORE_PATH)
    if not store_path.exists():
        logger.warning(f"Vector store not found at {store_path}. Run: python -m rag.ingest")
        return None

    try:
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        vs = FAISS.load_local(
            str(store_path),
            embeddings,
            allow_dangerous_deserialization=True,
        )
        logger.info(f"Vector store loaded from {store_path}")
        return vs
    except Exception as e:
        logger.error(f"Failed to load vector store: {e}")
        return None


def retrieve_context(query: str, top_k: int = TOP_K) -> tuple[str, list[dict]]:
    """
    Retrieve relevant Celonis doc chunks for a query.

    Returns:
        context_text: formatted string to inject into LLM prompt
        sources:      list of {content, url, score} dicts
    """
    vs = load_vector_store()
    if vs is None:
        return "", []

    try:
        docs_and_scores = vs.similarity_search_with_score(query, k=top_k)

        sources = []
        chunks  = []

        for doc, score in docs_and_scores:
            relevance = 1 - score   # FAISS returns L2 distance; invert for score
            sources.append({
                "content": doc.page_content,
                "url":     doc.metadata.get("url", "docs.celonis.com"),
                "score":   round(relevance, 3),
            })
            chunks.append(doc.page_content)

        top_score = sources[0]["score"] if sources else 0
        log_rag(query, len(sources), top_score)

        if not chunks:
            return "", []

        context_text = (
            "### 📚 Relevant Celonis Documentation\n\n"
            + "\n\n---\n\n".join(
                f"**Source:** {s['url']}\n\n{s['content']}"
                for s in sources
            )
        )
        return context_text, sources

    except Exception as e:
        logger.error(f"RAG retrieval error: {e}")
        return "", []


def is_rag_available() -> bool:
    """Check if RAG vector store is ready to use."""
    return RAG_AVAILABLE and Path(VECTOR_STORE_PATH).exists()
