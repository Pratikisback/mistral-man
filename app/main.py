from fastapi import FastAPI
from app.api.routes import query, ingest

app = FastAPI(title="Mistral RAG API")

app.include_router(query.router, prefix="/api")
app.include_router(ingest.router, prefix="/api")

     
@app.get("/")
def root():
    return {"status": "running"}

