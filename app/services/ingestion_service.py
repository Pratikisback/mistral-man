import re
from app.db.vector_store import retrieve_chunks, get_all_documents, document_exists, rerank_chunks, deduplicate_chunks
from app.db.vector_store import store_chunks, create_document, document_exists
from app.ingestion.chunking import chunk_text
from app.ingestion.pdf_loader import extract_text


def ingest_pdf(pdf_path: str, filename: str | None):
    # check existing
    existing = document_exists(filename)
    if existing:
        return {
            "message": "already_exists",
            "document_id": existing
        }

    # create doc
    document_id = create_document(filename)
    # extract + process
    text = extract_text(pdf_path)
    text = clean_text(text)
    chunks = chunk_text(text)

    # store
    store_chunks(document_id, chunks)

    return {
        "message": "ingested",
        "document_id": document_id
    }

def clean_text(text):
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()