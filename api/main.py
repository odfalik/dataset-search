from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI
from fastapi.responses import FileResponse
from api.config import settings
from api.clients import openai_client, index, EMBEDDING_MODEL
from api.data_models import SearchQuery
from api.preprocess import process_all_datasets
from api.logging import logger
from api.utils import reword_search_query


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
async def search_datasets(body: SearchQuery) -> List[str]:
    """
    Searches for datasets based on the provided query.

    Note that this is not RESTful, as the search query is sent as a POST request,
    but it makes cURL testing easier as the query doesn't need to be URL-encoded.
    """
    NUM_RESULTS = 5

    logger.info(f"Searching for datasets with query: {body.query}")

    reworded_query = reword_search_query(body.query)

    logger.info(f"Reworded query: {reworded_query}")

    query_embedding = (
        openai_client.embeddings.create(
            input=[reworded_query],
            model=EMBEDDING_MODEL,
        )
        .data[0]
        .embedding
    )

    vector_query_response = index.query(
        vector=query_embedding,
        top_k=NUM_RESULTS,
    )

    num_matches = len(vector_query_response.matches)
    logger.info(f"Found {num_matches} results")

    if num_matches == 0:
        raise ValueError("No results found. Database is likely empty.")

    return [result["id"] for result in vector_query_response.matches]


@app.get("/")
async def read_index():
    """Serves the index.html file at the root path"""
    return FileResponse("static/index.html")
