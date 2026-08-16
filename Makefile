install:
	python -m pip install -r requirements.txt

test:
	pytest -q

run:
	uvicorn app:app --reload

docker:
	docker compose up --build

check:
	python -m compileall app.py hirelens
	pytest -q
