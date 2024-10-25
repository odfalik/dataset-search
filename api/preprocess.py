from typing import List
from api.data_models import Dataset
from api.clients import openai_client, index, EMBEDDING_MODEL, ada_002_encoding
from api.logging import logger


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
        f"Upserted dataset embeddings for {', '.join([dataset.dataset_name for dataset in datasets])}"
    )
