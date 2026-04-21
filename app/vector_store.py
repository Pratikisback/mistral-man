from db import get_connection
from embeddings import get_embedding
from rag_pipeline import build_prompt, ask_llm
import uuid

def create_document(name):
    doc_id = str(uuid.uuid4())

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO documents (id, name) VALUES (%s, %s)",
                (doc_id, name)
            )

    return doc_id


def document_exists(name):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM documents WHERE name = %s LIMIT 1",
                (name,)
            )
            row = cursor.fetchone()
            return row[0] if row else None
        

def store_chunks(doc_id, chunks):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            for chunk in chunks:
                embedding = get_embedding(chunk)
                cursor.execute(
                    """
                    INSERT INTO chunks (document_id, content, embedding)
                    VALUES (%s, %s, %s)
                    """,
                    (doc_id, chunk, embedding)
                )

def search(query):
    query_embedding = get_embedding(query)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT content
                FROM documents
                ORDER BY embedding <-> %s::vector
                LIMIT 2
                """,
                (query_embedding,)
            )

            return cursor.fetchall()
        

# Retrieving the top 3 matching chunks
def retrieve_chunks(query, top_k=3, document_id=None):

    if not query or not query.strip():
        return []
    
    query_embedding = get_embedding(query)
    
    with get_connection() as conn:
        with conn.cursor() as cursor:

            if document_id:
                cursor.execute(
                    """
                    SELECT content
                    FROM chunks
                    WHERE document_id = %s
                    ORDER BY embedding <-> %s::vector
                    LIMIT %s
                    """,
                    (document_id, query_embedding, top_k)
                )
            else:
                cursor.execute(
                    """
                    SELECT content
                    FROM chunks
                    ORDER BY embedding <-> %s::vector
                    LIMIT %s
                    """,
                    (query_embedding, top_k)
                )

            results = cursor.fetchall()

    return [r[0] for r in results]

def get_all_documents():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name FROM documents")
            return cursor.fetchall()