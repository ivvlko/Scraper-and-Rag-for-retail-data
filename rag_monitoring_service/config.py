import os

rag_configs = {
    "EMBEDDING_MODEL": os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
    "LLM_MODEL": os.getenv("LLM_MODEL", "gpt-4o-mini"),
    "OPEN_AI_API_KEY": os.getenv("OPEN_AI_API_KEY"),
    "TOP_K": int(os.getenv("TOP_K", "5")),
    "SYSTEM_PROMPT": os.getenv("SYSTEM_PROMPT", "Answer the questions only within the products (fosils) context.")
}
