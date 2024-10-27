project_id := 'dataset-search-439522'

@_default:
  just --list

setup:
  python3 -m venv .venv
  ./.venv/bin/pip install -r requirements.txt

serve: setup
  ./.venv/bin/uvicorn api.main:app --reload

format: setup
  ./.venv/bin/ruff format .

build: setup
  docker build --platform linux/amd64 -t dataset-search .
  docker tag dataset-search gcr.io/{{project_id}}/dataset-search

deploy: build
  docker push gcr.io/{{project_id}}/dataset-search
  gcloud run deploy dataset-search --image gcr.io/{{project_id}}/dataset-search --platform managed --region us-west1 --allow-unauthenticated --port 8000