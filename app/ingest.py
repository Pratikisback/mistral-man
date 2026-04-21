import re
from pdf_loader import extract_text
from chunking import chunk_text
from vector_store import store_chunks, create_document

def clean_text(text):
    text = re.sub(r"http\S+", "", text) 
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def ingest(pdf_path):
    name = pdf_path.split("/")[-1] 
    document_id = create_document(name)
    text = extract_text(pdf_path)
    text = clean_text(text)
    chunks = chunk_text(text)

    store_chunks(document_id, chunks)