import streamlit as st
from vector_store import retrieve_chunks
from rag_pipeline import build_prompt
from cache import get_cached_answer, set_cached_answer
from rag_pipeline import ask_llm_stream  # streaming version

st.set_page_config(page_title="PDF Q&A", layout="centered")

st.title("RAG PDF Q&A")
st.write("Ask questions based on your uploaded PDF")

# Input
query = st.text_input("Ask a question:")

if st.button("Ask") and query:

    placeholder = st.empty()

    try:
        # 1. Check cache
        cached = get_cached_answer(query)

        if cached:
            st.success("⚡ Instant Answer (Cache Hit)")
            placeholder.write(cached)

        else:
            st.info("🐢 Generating answer... (streaming)")

            # Retrieve + prompt
            contexts = retrieve_chunks(query, top_k=2)
            prompt = build_prompt(query, contexts)

            full_answer = ""

            # 2. Stream response
            for partial in ask_llm_stream(prompt):
                full_answer = partial
                placeholder.write(partial)

            # 3. Save to cache
            set_cached_answer(query, full_answer)

    except Exception as e:
        st.error(f"Error: {e}")