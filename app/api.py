from fastapi import FastAPI, Query, UploadFile, File
from fastapi.responses import StreamingResponse
import json
from ingest import ingest
import shutil, tempfile
from vector_store import retrieve_chunks, get_all_documents, document_exists
from rag_pipeline import build_prompt, ask_llm_stream
from cache import get_cached_answer, set_cached_answer

app = FastAPI()


def format_sse(event: str, data: dict):
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def stream_answer(query: str, document_id: str | None):

    # 🔒 Guard
    if not query or not query.strip():
        yield format_sse("error", {"message": "Query cannot be empty"})
        return

    cache_key = f"{document_id}:{query}"

    # ⚡ Cache
    cached = get_cached_answer(cache_key)
    if cached:
        yield format_sse("start", {"cached": True})
        yield format_sse("chunk", {"text": cached})
        yield format_sse("end", {"done": True})
        return

    yield format_sse("start", {"cached": False})

    # 🔍 Retrieve
    contexts = retrieve_chunks(
        query,
        top_k=3,
        document_id=document_id
    )
    print("\n==== DEBUG START ====")
    print("Query:", query)
    print("Selected doc ID:", document_id)
    print("Contexts count:", len(contexts))

    for i, ctx in enumerate(contexts):
        print(f"\n--- Context {i+1} ---")
        print(ctx[:200])  # print first 200 chars only

    print("==== DEBUG END ====\n")

    if not contexts:
        yield format_sse("end", {
            "answer": "No relevant data found."
        })
        return

    prompt = build_prompt(query, contexts)

    full_answer = ""

    try:
        # ⚡ Stream LLM response
        for partial in ask_llm_stream(prompt):
            full_answer = partial

            yield format_sse("chunk", {
                "text": partial
            })

        # 💾 Cache final answer
        set_cached_answer(cache_key, full_answer)

        yield format_sse("end", {
            "done": True
        })

    except Exception as e:
        yield format_sse("error", {
            "message": str(e)
        })



@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if document_exists(file.filename):
        return {"message": "already_exists", "name": file.filename}
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    ingest(tmp_path)
    return {"message": "ingested", "name": file.filename}

@app.get("/documents")
def list_documents():
    docs = get_all_documents()
    return [{"id": doc_id, "name": name} for doc_id, name in docs]




@app.get("/ask")
def ask(
    query: str = Query(...),
    document_id: str | None = Query(default=None)
):
    return StreamingResponse(
        stream_answer(query, document_id),
        media_type="text/event-stream"
    )