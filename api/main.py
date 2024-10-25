from contextlib import asynccontextmanager
import sys
from typing import List
from api.config import Settings
from fastapi import FastAPI
import tiktoken
import json
from pinecone import Pinecone
import openai
import logging

from api.models import Dataset, SearchQuery

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
stream_handler.setFormatter(log_formatter)
logger.addHandler(stream_handler)

settings = Settings()  # type: ignore

openai.api_key = settings.OPENAI_API_KEY
openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX)

EMBEDDING_MODEL = "text-embedding-ada-002"
ada_002_encoding = tiktoken.encoding_for_model(EMBEDDING_MODEL)


def format_dataset_embedding_input(dataset: Dataset):
    """Reformats dataset JSON into text that can be embedded"""
    return f"""ID: {dataset.dataset_name}
Name: {dataset.readable_name}
Description: {dataset.dataset_description}
Category: {dataset.category}
Subcategories: {', '.join(dataset.subcategories)}
Columns: {', '.join(dataset.columns)}
"""


async def upsert_dataset_embedding_batch(datasets: List[Dataset]):
    """
    Embeds and upserts embeddings for a batch of datasets into vector store
    """
    dataset_embedding_inputs = [
        format_dataset_embedding_input(dataset) for dataset in datasets
    ]

    max_token = max(
        len(ada_002_encoding.encode(input)) for input in dataset_embedding_inputs
    )
    if max_token > 8191:
        raise ValueError("Input exceeds max supported token limit of 8191")

    embeddings = [
        # We sort the results to match the input order b/c OpenAI
        # batch embedding API doesn't guarantee order
        result.embedding
        for result in sorted(
            openai_client.embeddings.create(
                input=dataset_embedding_inputs,
                model=EMBEDDING_MODEL,
            ).data,
            key=lambda result: result.index,
        )
    ]

    # Store dataset embedding
    index.upsert(
        vectors=list(
            zip(
                [dataset.dataset_name for dataset in datasets],
                embeddings,
            )
        )
    )

    logger.info(
        f"Upserted dataset embeddings for {', '.join([
            dataset.dataset_name for dataset in datasets
        ])}"
    )


async def process_all_datasets():
    """Loads dataset metadata and stores embeddings in the vector store"""
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
    # await process_all_datasets()
    yield


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

    results = index.query(
        vector=query_embedding,
        top_k=NUM_RESULTS,
    )

    return [result["id"] for result in results.matches]
