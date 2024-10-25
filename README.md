# dataset-search

first `source .venv/bin/activate` to activate the virtual environment

```sh
curl -X POST "http://localhost:8000/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "your search query here"}'
```