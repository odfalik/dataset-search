project_id := 'dataset-search-439522'

init_venv:
  python3 -m venv .venv

activate: init_venv
  source .venv/bin/activate

install: activate
  pip install -r requirements.txt

serve: activate install
  uvicorn api.main:app --reload

format: activate
  ruff format .

build:
  docker build --platform linux/amd64 -t dataset-search .
  docker tag dataset-search gcr.io/{{project_id}}/dataset-search

deploy: build
  docker push gcr.io/{{project_id}}/dataset-search
  gcloud run deploy dataset-search --image gcr.io/{{project_id}}/dataset-search --platform managed --region us-west1 --allow-unauthenticated --port 8000