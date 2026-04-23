import streamlit as st
import os

from vector_store import retrieve_chunks, get_all_documents, document_exists, rerank_chunks, deduplicate_chunks
from rag_pipeline import build_prompt, ask_llm_stream
from cache import get_cached_answer, set_cached_answer
from ingest import ingest  
import os

DATA_DIR = "../LLM/data"
os.makedirs(DATA_DIR, exist_ok=True)

st.set_page_config(page_title="PDF Q&A", layout="centered")

st.title("📄 RAG PDF Q&A")

# =========================
# 📤 Upload PDF
# =========================
if "ingested_files" not in st.session_state:
    st.session_state.ingested_files = set()

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:
    file_path = os.path.join(DATA_DIR, uploaded_file.name)
    existing_id = document_exists(uploaded_file.name)

    if not existing_id:
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        with st.spinner("Ingesting PDF..."):
            ingest(file_path)

        st.success(f"✅ {uploaded_file.name} uploaded and indexed!")
    else:
        st.info(f"📎 {uploaded_file.name} already indexed.")

# =========================
# 📚 Document Selection
# =========================
docs = get_all_documents()

doc_map = {name: doc_id for doc_id, name in docs}

selected_doc_name = st.selectbox(
    "Select document (optional)",
    ["All Documents"] + list(doc_map.keys())
)

selected_doc_id = None
if selected_doc_name != "All Documents":
    selected_doc_id = doc_map[selected_doc_name]


# =========================
# ❓ Ask Question
# =========================
query = st.text_input("Ask a question:")
placeholder = st.empty()
status = st.empty()

try:
    if query:
        cache_key = f"{selected_doc_id}:{query}"
        cached = get_cached_answer(cache_key)

        if cached:
            st.success("⚡ Cache Hit")
            placeholder.write(cached)

        else:
            status.info("🐢 Generating answer...")

            contexts = retrieve_chunks(
                query,
                top_k=20,
                document_id=selected_doc_id
            )
            candidates = retrieve_chunks(query, top_k=15)
            candidates = deduplicate_chunks(candidates)
            top_chunks = rerank_chunks(candidates, query, top_n=5)

            prompt = build_prompt(query, top_chunks)

            full_answer = ""

            for partial in ask_llm_stream(prompt):
                full_answer = partial
                placeholder.write(partial)

            # ✅ remove the message
            status.empty()

            set_cached_answer(cache_key, full_answer)

except Exception as e:
    status.empty()  # also clear on error
    st.error(f"Error: {e}")