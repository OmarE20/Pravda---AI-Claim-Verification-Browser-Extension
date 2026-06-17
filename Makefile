.PHONY: install serve seed-corpus eval test docker extension

install:
	cd backend && python -m venv .venv
	cd backend && .venv/bin/pip install -r requirements.txt
	cd extension && bun install || npm install

serve:
	cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000

seed-corpus:
	backend/.venv/bin/python -m eval.seed_corpus

eval:
	backend/.venv/bin/python -m eval.run_eval

test:
	cd backend && .venv/bin/python -m pytest -q

docker:
	docker compose up --build

extension:
	cd extension && bun run build || npm run build
