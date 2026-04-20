from db import get_connection
from embeddings import get_embedding
from rag_pipeline import build_prompt, ask_llm
def store_chunks(chunks):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            for chunk in chunks:
                embedding = get_embedding(chunk)
                cursor.execute(
                    "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
                    (chunk, embedding)
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
def retrieve_chunks(query, top_k=3):
    query_embedding = get_embedding(query)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT content
                FROM documents
                ORDER BY embedding <-> %s::vector
                LIMIT %s
                """,
                (query_embedding, top_k)
            )

            results = cursor.fetchall()

    return [r[0] for r in results]

def ask_question(query):
    contexts = retrieve_chunks(query)

    prompt = build_prompt(query, contexts)

    answer = ask_llm(prompt)

    return answer