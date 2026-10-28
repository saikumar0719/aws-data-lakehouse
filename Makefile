.PHONY: run test compile

run:
	PYTHONPATH=. python run_pipeline.py

test:
	PYTHONPATH=. python -m pytest -q

compile:
	python -m py_compile src/*.py tests/*.py airflow/dags/*.py run_pipeline.py
