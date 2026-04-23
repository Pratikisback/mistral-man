from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
import json

from app.services.rag_service import RAGService

router = APIRouter()

service = RAGService()


def format_sse(event: str, data: dict):
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@router.get("/ask")
def ask(
    query: str = Query(...),
    document_id: str | None = Query(default=None)
):
    def event_stream():
        for item in service.stream(query, document_id):
            yield format_sse(item["type"], item)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )