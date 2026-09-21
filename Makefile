PYTHON ?= python3
DATA ?= data/fin_crime_data.csv.zip

.PHONY: setup analyse dashboard test verify

setup:
	$(PYTHON) -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

analyse:
	.venv/bin/python run.py analyse --data "$(DATA)" --output outputs

dashboard:
	.venv/bin/python run.py dashboard --data "$(DATA)" --port 8501

test:
	.venv/bin/python -m pytest

verify:
	.venv/bin/python scripts/verify_supplied_data.py --data "$(DATA)"
