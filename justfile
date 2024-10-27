project_id := 'dataset-search-439522'
venv_bin := './.venv/bin'

@_default:
  just --list

# Set up the virtual environment and install dependencies
setup:
  python3 -m venv .venv
  {{venv_bin}}/pip install -r requirements.txt

# Run the API and site server
serve: setup
  {{venv_bin}}/uvicorn api.main:app --reload

# Format the code
format: setup
  {{venv_bin}}/ruff format .

# Build the Docker image
build: setup
  docker build --platform linux/amd64 -t dataset-search .
  docker tag dataset-search gcr.io/{{project_id}}/dataset-search

# Deploy the Docker image to Cloud Run
deploy: build
  docker push gcr.io/{{project_id}}/dataset-search
  gcloud run deploy dataset-search --image gcr.io/{{project_id}}/dataset-search --platform managed --region us-west1 --allow-unauthenticated --port 8000