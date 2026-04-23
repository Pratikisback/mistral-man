from typing import Generator, Optional, Dict, Any

from app.db.vector_store import retrieve_chunks
from app.llm.rag_pipeline import build_prompt, ask_llm, ask_llm_stream
from app.core.cache import get_cached_answer, set_cached_answer


class RAGService:

    def __init__(self, top_k: int = 5):
        self.top_k = top_k

  
    # Internal Helpers
    def _get_cache_key(self, query: str, document_id: Optional[str]) -> str:
        return f"{document_id}:{query}"

    def _retrieve(self, query: str, document_id: Optional[str]):
        return retrieve_chunks(
            query,
            top_k=self.top_k,
            document_id=document_id
        )

    def _build_prompt(self, query: str, contexts):
        return build_prompt(query, contexts)

   
    # Non-stream API

    def run(
        self,
        query: str,
        document_id: Optional[str] = None
    ) -> str:

        cache_key = self._get_cache_key(query, document_id)

        
        cached = get_cached_answer(cache_key) # 1. cache
        if cached:
            return cached   
           
        contexts = self._retrieve(query, document_id) # 2. retrieve
        if not contexts:
            return "No relevant data found."    
            
        prompt = self._build_prompt(query, contexts)# 3. prompt        
        answer = ask_llm(prompt) # 4. LLM       
        set_cached_answer(cache_key, answer) # 5. cache

        return answer

    # For API stream
    def stream(
        self,
        query: str,
        document_id: Optional[str] = None
    ) -> Generator[Dict[str, Any], None, None]:

        cache_key = self._get_cache_key(query, document_id)

        # 1. cache
        cached = get_cached_answer(cache_key)
        if cached:
            yield {"type": "start", "cached": True}
            yield {"type": "chunk", "text": cached}
            yield {"type": "end"}
            return

        yield {"type": "start", "cached": False}

        # 2. retrieve
        contexts = self._retrieve(query, document_id)

        if not contexts:
            yield {"type": "end", "text": "No relevant data found."}
            return

        # 3. prompt
        prompt = self._build_prompt(query, contexts)

        full_answer = ""

        # 4. stream LLM
        for chunk in ask_llm_stream(prompt):
            full_answer += chunk

            yield {
                "type": "chunk",
                "text": chunk
            }

        # 5. cache
        set_cached_answer(cache_key, full_answer)

        yield {"type": "end"}