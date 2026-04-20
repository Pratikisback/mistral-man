import ollama

def get_embedding(text):
    response = ollama.embeddings(model="nomic-embed-text", prompt=text)
    return response["embedding"]