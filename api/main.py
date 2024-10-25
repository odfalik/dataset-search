from contextlib import asynccontextmanager
from api.config import Settings
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from pinecone import Pinecone
import openai


settings = Settings()

openai.api_key = settings.OPENAI_API_KEY
pc = Pinecone(api_key=settings.PINECONE_API_KEY)


async def upsert_dataset_embeddings():
    """Load dataset metadata and store embeddings in the vector store"""
    with open("data/dataset_metadata.json") as f:
        datasets = json.load(f)
        print(len(datasets))
        # TODO Generate embeddings in parallel and upsert to vector store


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI handler for startup and shutdown events"""
    await upsert_dataset_embeddings()
    yield


# Initialize FastAPI app
app = FastAPI(lifespan=lifespan)


# Generate embeddings using OpenAI
async def generate_embedding(text):
    """Generate embeddings for a given text using OpenAI's GPT-3 model"""
    # TODO chunking?
    # TODO reformat before embedding?
    # TODO embed
    pass


class Query(BaseModel):
    query: str


@app.post("/search")
async def search_datasets(query: Query) -> list[str]:
    raise HTTPException(status_code=501, detail="Not implemented")
    # TODO consider search query re-wording (e.g. hypothetical document)
    # query_embedding = await generate_embedding(query.query)

    # TODO
    # top_dataset_names = [row["dataset_name"] for row in rows]
    # return top_dataset_names
