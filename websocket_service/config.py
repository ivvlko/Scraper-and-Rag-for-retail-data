import os

rag_configs = {
    "EMBEDDING_MODEL": os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
    "LLM_MODEL": "gpt-4o-mini",
    "OPEN_AI_API_KEY": os.getenv("OPEN_AI_API_KEY"),
    "TOP_K": 3,
    "SYSTEM_PROMPT": "Answer the question concisely"
}
