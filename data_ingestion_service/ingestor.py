import os
import json
from pathlib import Path
from openai import OpenAI
from sqlalchemy import create_engine, Column, String, Float, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy_utils import database_exists, create_database

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIM = 1536 if "large" in EMBEDDING_MODEL else 1536

PG_URI = os.getenv("PG_URI", "postgresql://postgres:postgres@db:5432/postgres")

Base = declarative_base()


class ProductEmbedding(Base):
    __tablename__ = "fosils_embeddings"

    id = Column(String, primary_key=True)
    name = Column(String)
    url = Column(String)
    price = Column(Float)
    chunk_index = Column(Integer)
    text = Column(String)
    embedding = Column(ARRAY(DOUBLE_PRECISION))


class DataIngestor:
    def __init__(self, processed_dir="/data/processed/fosili"):
        self.processed_dir = Path(processed_dir)
        self.client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

        self.engine = create_engine(PG_URI)
        if not database_exists(self.engine.url):
            create_database(self.engine.url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def embed_text(self, text: str) -> list:
        resp = self.client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return resp.data[0].embedding

    def ingest_file(self, filepath: Path):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        session = self.Session()

        for idx, chunk in enumerate(data.get("chunks", [])):
            embedding = self.embed_text(chunk)
            record = ProductEmbedding(
                id=f"{data['id']}_{idx}",
                name=data["name"],
                url=data["url"],
                price=data["price"],
                chunk_index=idx,
                text=chunk,
                embedding=embedding
            )
            session.add(record)

        session.commit()
        session.close()
        print(f"Ingested {filepath.name} ({len(data.get('chunks', []))} chunks)")

    def run(self):
        files = list(self.processed_dir.glob("*.json"))
        for file in files:
            self.ingest_file(file)
