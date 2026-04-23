from fastapi import APIRouter, UploadFile, File
import shutil
import tempfile
from app.db.vector_store import get_all_documents
from app.services.ingestion_service import ingest_pdf

router = APIRouter()


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    # save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    # call service
    result = ingest_pdf(tmp_path, file.filename)

    return result

@router.get("/documents")
def list_documents():
    docs = get_all_documents()
    return [{"id": d[0], "name": d[1]} for d in docs]