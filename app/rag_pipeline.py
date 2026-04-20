
import requests
import json


def build_prompt(query, contexts):
    context_text = "\n\n".join(contexts)

    prompt = f"""
        Answer the question based ONLY on the context below.
        If no matching data, return, no such information available
        Context:
        {context_text}

        Question:
        {query}

        Answer:
        """
    return prompt

def ask_llm(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]

def ask_llm_stream(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": True
        },
        stream=True
    )

    full_response = ""

    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            chunk = data.get("response", "")
            full_response += chunk
            yield full_response