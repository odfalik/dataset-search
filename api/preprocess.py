import json
from typing import List
from api.data_models import Dataset
from api.clients import (
    EMBEDDING_MODEL_MAX_TOKENS,
    openai_client,
    index,
    EMBEDDING_MODEL,
    ada_002_encoding,
)
from api.logging import logger


async def process_all_datasets():
    """Loads dataset metadata, embeds, and upserts all datasets"""
    BATCH_SIZE = 100
    logger.info("Starting process_all_datasets")

    with open("data/dataset_metadata.json") as f:
        datasets = [Dataset(**dataset) for dataset in json.load(f)]

        # Upsert dataset embeddings in batches
        for i in range(0, len(datasets), BATCH_SIZE):
            logger.info(f"Processing batch {i} to {i + BATCH_SIZE}")
            await upsert_dataset_embedding_batch(datasets[i : i + BATCH_SIZE])

    logger.info("Completed process_all_datasets")


def format_dataset_embedding_input(dataset: Dataset) -> str:
    """Reformats dataset JSON into text that can be embedded"""
    return f"""ID: {dataset.dataset_name}
Name: {dataset.readable_name}
Description: {dataset.dataset_description}
Category: {dataset.category}
Subcategories: {', '.join(dataset.subcategories)}
Columns: {', '.join(dataset.columns)}
"""


def upsert_dataset_embedding_batch(datasets: List[Dataset]) -> None:
    """
    Embeds and upserts embeddings for a batch of datasets into vector store
    """
    dataset_embedding_inputs = [
        format_dataset_embedding_input(dataset) for dataset in datasets
    ]

    max_token = max(
        len(ada_002_encoding.encode(input)) for input in dataset_embedding_inputs
    )
    if max_token > EMBEDDING_MODEL_MAX_TOKENS:
        raise ValueError(
            f"Input exceeds max supported token limit of {EMBEDDING_MODEL_MAX_TOKENS}"
        )

    embeddings = [
        result.embedding
        # We sort the results to match the input order b/c OpenAI
        # batch embedding API doesn't guarantee order
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
        f"Upserted dataset embeddings for {', '.join([dataset.dataset_name for dataset in datasets])}"
    )
