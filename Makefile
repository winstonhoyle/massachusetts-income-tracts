.PHONY: data test serve

.venv/.deps: pyproject.toml
	test -d .venv || python3 -m venv .venv
	.venv/bin/pip install -q --upgrade pip
	.venv/bin/pip install -q --group test
	@touch $@

# Reads CENSUS_API_KEY from .env (see .env.sample)
data: .venv/.deps
	set -a && . ./.env && .venv/bin/python format_data.py

test: .venv/.deps
	.venv/bin/python -m pytest -q

serve:
	python3 -m http.server -d app 8000
