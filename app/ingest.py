import re
from pdf_loader import extract_text
from chunking import chunk_text
from vector_store import store_chunks

def clean_text(text):
    text = re.sub(r"http\S+", "", text) 
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def ingest():
    pdf_path = "../LLM/data/sample.pdf"
    text = extract_text(pdf_path)
    text = clean_text(text)
    chunks = chunk_text(text)
    store_chunks(chunks)