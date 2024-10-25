from api.clients import (
    openai_client,
    EMBEDDING_MODEL_ENCODING,
    EMBEDDING_MODEL_MAX_TOKENS,
)
from api.logging import logger


def reword_search_query(query: str) -> str:
    """
    Calls an LLM to reword a search query so that it can better be embedded into a vector.
    """

    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "Your job is to reword or reformat the following search query so that it can be embedded into a vector and used to search for datasets."
                    + " These datasets are embedded with information about their names, descriptions, categories, subcategories, and columns."
                    + " If the search query is a sentence or question, reword it in a concise way that preserves its intent."
                ),
            },
            {"role": "user", "content": query},
        ],
    )
    reworded_query = response.choices[0].message.content

    reworded_query_num_tokens = len(EMBEDDING_MODEL_ENCODING.encode(reworded_query))

    # Make sure we're not exceeding the max token limit for the embedding model.
    # If we are, log an error and return the original query (if it's also within the limit).
    if reworded_query_num_tokens > EMBEDDING_MODEL_MAX_TOKENS:
        logger.error(
            f"Reworded query exceeds max supported token limit of {EMBEDDING_MODEL_MAX_TOKENS}"
        )
        original_query_num_tokens = len(EMBEDDING_MODEL_ENCODING.encode(query))
        if original_query_num_tokens > EMBEDDING_MODEL_MAX_TOKENS:
            raise ValueError(
                f"Original query also exceeds max supported token limit of {EMBEDDING_MODEL_MAX_TOKENS}"
            )
        else:
            return query

    return reworded_query
