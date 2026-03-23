"""
rag/ingest.py
Celonis Docs RAG Ingestion Pipeline.

1. Scrapes key pages from docs.celonis.com
2. Chunks text intelligently
3. Embeds with sentence-transformers
4. Saves to FAISS index on disk

Run once:  python -m rag.ingest
Then the vector store is reused across app restarts.
"""

import os
import json
import time
import requests
from bs4 import BeautifulSoup
from pathlib import Path

# Lazy imports — only needed during ingestion
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import FAISS
    from langchain_community.embeddings import HuggingFaceEmbeddings
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from utils.logger import logger

# ── Config ────────────────────────────────────────────────────────────────────
VECTOR_STORE_PATH = "rag/vector_store"
EMBEDDING_MODEL   = "sentence-transformers/all-MiniLM-L6-v2"   # fast, free, good quality
CHUNK_SIZE        = 600
CHUNK_OVERLAP     = 80

# Key Celonis doc pages to ingest (add more as needed)
CELONIS_PAGES = [
    # Core platform
    "https://docs.celonis.com/en/getting-started-with-the-celonis-platform.html",
    # Studio
    "https://docs.celonis.com/en/studio.html",
    "https://docs.celonis.com/en/views.html",
    "https://docs.celonis.com/en/olap-table.html",
    # PQL
    "https://docs.celonis.com/en/pql-function-overview.html",
    "https://docs.celonis.com/en/aggregation-functions.html",
    "https://docs.celonis.com/en/process-query-language.html",
    # Data model
    "https://docs.celonis.com/en/data-models.html",
    "https://docs.celonis.com/en/activity-tables.html",
    # Connectors
    "https://docs.celonis.com/en/connectors.html",
    "https://docs.celonis.com/en/sap-erp-connector.html",
    # Process Explorer
    "https://docs.celonis.com/en/process-explorer.html",
    # Action Engine
    "https://docs.celonis.com/en/action-engine.html",
    # ML
    "https://docs.celonis.com/en/ml-workbench.html",
]


def scrape_page(url: str) -> str:
    """Scrape a Celonis docs page and return clean text."""
    try:
        headers = {"User-Agent": "CelonisAIAgent/1.0 (research bot)"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove nav, scripts, styles, footers
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # Get main content area (Celonis docs uses article/main tags)
        main = soup.find("article") or soup.find("main") or soup.find("div", class_="content")
        text = (main or soup).get_text(separator="\n", strip=True)

        # Clean whitespace
        lines   = [l.strip() for l in text.splitlines() if l.strip()]
        cleaned = "\n".join(lines)

        logger.info(f"Scraped {url} → {len(cleaned)} chars")
        return cleaned

    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")
        return ""


def build_vector_store(pages: list[str] = None, force_rebuild: bool = False):
    """
    Build or load FAISS vector store from Celonis docs.
    Skips if vector store already exists (unless force_rebuild=True).
    """
    if not LANGCHAIN_AVAILABLE:
        logger.error("LangChain not installed. Run: pip install langchain langchain-community faiss-cpu sentence-transformers")
        return None

    store_path = Path(VECTOR_STORE_PATH)

    if store_path.exists() and not force_rebuild:
        logger.info(f"Loading existing vector store from {store_path}")
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        return FAISS.load_local(
            str(store_path),
            embeddings,
            allow_dangerous_deserialization=True,
        )

    logger.info("Building new vector store from Celonis docs...")
    pages = pages or CELONIS_PAGES

    # Scrape all pages
    all_docs = []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    for url in pages:
        text = scrape_page(url)
        if not text:
            continue

        chunks = splitter.create_documents(
            texts=[text],
            metadatas=[{"source": url, "url": url}],
        )
        all_docs.extend(chunks)
        time.sleep(0.5)   # polite crawl delay

    if not all_docs:
        logger.error("No documents scraped — check URLs and network access")
        return None

    logger.info(f"Creating embeddings for {len(all_docs)} chunks...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vector_store = FAISS.from_documents(all_docs, embeddings)

    # Save to disk
    store_path.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(str(store_path))
    logger.info(f"Vector store saved → {store_path} ({len(all_docs)} chunks)")

    return vector_store


if __name__ == "__main__":
    print("🔄 Building Celonis RAG vector store...")
    vs = build_vector_store(force_rebuild=True)
    if vs:
        print(f"✅ Done! Vector store ready at {VECTOR_STORE_PATH}")
    else:
        print("❌ Failed — check logs/errors.log")
