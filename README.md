# dataset-search

## Overview

`dataset-search` is a FastAPI-based application that processes dataset metadata, generates embeddings using OpenAI's API, and stores them in Pinecone for efficient vector search. The application provides endpoints to search datasets based on query embeddings, with an additional static UI to interact with the search functionality.

## Prerequisites

- Python 3.8+
- [just](https://just.systems/)

### Code Structure

- `api/`: Contains the main application code.
  - `main.py`: FastAPI application setup and route definitions.
  - `preprocess.py`: Functions for processing and embedding datasets.
  - `clients.py`: Initializes OpenAI and Pinecone clients.
  - `config.py`: Configuration settings.
  - `data_models.py`: Pydantic models for JSON interfaces.
  - `logging.py`: Logger setup.
- `data/`: Contains the source dataset data (`dataset_metadata.json`).
- `static/`: Contains static files like `index.html`.

## Usage

To start the FastAPI server locally, simply run:

```sh
just serve
```

## API Endpoints

### Search Datasets

- **Endpoint:** `/search`
- **Method:** `POST`
- **Request Body:**

```json
{
     "query": "your search query here"
}
```

- **Response:** Names of 5 most relevant datasets.

```json
[
     "dataset_id_1",
     "dataset_id_2",
     ...
]
```

### Static UI

- **Endpoint:** `/`
- **Method:** `GET`
- **Description:** Serves the `index.html` file from the `static` directory.