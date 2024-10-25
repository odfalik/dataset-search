from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI
import json
from api.config import settings
from api.clients import openai_client, index, EMBEDDING_MODEL
from api.data_models import Dataset, SearchQuery
from api.preprocess import upsert_dataset_embedding_batch
from api.logging import logger


async def process_all_datasets():
    """Loads dataset metadata, embeds, and upserts all datasets"""
    BATCH_SIZE = 100
    logger.info("Starting process_all_datasets")

    with open("data/dataset_metadata.json") as f:
        datasets = [Dataset(**dataset) for dataset in json.load(f)[:10]]

        # Upsert dataset embeddings in batches
        for i in range(0, len(datasets), BATCH_SIZE):
            logger.info(f"Processing batch {i} to {i + BATCH_SIZE}")
            await upsert_dataset_embedding_batch(datasets[i : i + BATCH_SIZE])

    logger.info("Completed process_all_datasets")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI handler for startup and shutdown events"""
    # Process datasets on startup only if flag is enabled
    if str(settings.PROCESS_DATASETS).__str__().lower() == "true":
        await process_all_datasets()
    yield
    # Nothing to clean up on shutdown


# Initialize FastAPI app
app = FastAPI(lifespan=lifespan)


@app.post("/search")
async def search_datasets(query: SearchQuery) -> List[str]:
    NUM_RESULTS = 5
    # TODO consider search query re-wording (e.g. hypothetical document)

    query_embedding = (
        openai_client.embeddings.create(
            input=[query.query],
            model=EMBEDDING_MODEL,
        )
        .data[0]
        .embedding
    )

    vector_query_response = index.query(
        vector=query_embedding,
        top_k=NUM_RESULTS,
    )

    if len(vector_query_response.matches) == 0:
        raise ValueError("No results found. Database is likely empty.")

    return [result["id"] for result in vector_query_response.matches]
