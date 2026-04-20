from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from vector_store import retrieve_chunks
from rag_pipeline import build_prompt, ask_llm_stream
from cache import get_cached_answer, set_cached_answer

app = FastAPI()


def stream_answer(query: str):
    #  1. Check cache
    cached = get_cached_answer(query)

    if cached:
        yield f"data: {cached}\n\n"
        return

    # 🔹 2. Retrieve + prompt
    contexts = retrieve_chunks(query, top_k=2)
    prompt = build_prompt(query, contexts)

    full_answer = ""

    #  3. Stream from LLM
    for partial in ask_llm_stream(prompt):
        full_answer = partial
        yield f"data: {partial}\n\n"

    #  4. Cache final answer
    set_cached_answer(query, full_answer)


@app.get("/ask")
def ask(query: str):
    return StreamingResponse(
        stream_answer(query),
        media_type="text/event-stream"
    )