

from vector_store import store_chunks, search, retrieve_chunks
from rag_pipeline import build_prompt, ask_llm, ask_llm_stream
from cache import get_cached_answer, set_cached_answer

def ask_question(query):

    # Checking in the cache
    cached = get_cached_answer(query)
    if cached:
        print("⚡ Cache hit")
        return cached
    print("1. Retrieving chunks...")
    contexts = retrieve_chunks(query)

    print("2. Building prompt...")
    prompt = build_prompt(query, contexts)

    print("3. Calling LLM...")
    answer = ask_llm(prompt)

    print("4. Got response")
    return answer

if __name__ == "__main__":
    question = "Why are elephants important?"

    answer = ask_question(question)

    print("\n=== ANSWER ===\n")
    print(answer)

def ask_question_stream(query):
    cached = get_cached_answer(query)

    if cached:
        yield cached
        return

    contexts = retrieve_chunks(query, top_k=2)
    prompt = build_prompt(query, contexts)

    full_answer = ""

    for partial in ask_llm_stream(prompt):
        full_answer = partial
        yield partial

    # store final answer
    set_cached_answer(query, full_answer)