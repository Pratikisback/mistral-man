import ollama

def get_embedding(text):
    response = ollama.embeddings(model="nomic-embed-text", prompt=text)
    embedding = response.get("embedding")

    if not embedding or not isinstance(embedding, list):
        raise ValueError(f"Invalid embedding: {response}")
    return response["embedding"]