activate:
  source .venv/bin/activate

install: activate
  pip install -r requirements.txt

serve: activate install
  uvicorn api.main:app --reload

format: activate
  ruff format .
