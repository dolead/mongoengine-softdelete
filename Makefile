RUN=poetry run

install:
	poetry update

test:
	$(RUN) pytest --cov=mongoengine_softdelete

pep8:
	$(RUN) pycodestyle --ignore=E126,E127,E128,W503 mongoengine_softdelete/

mypy:
	$(RUN) mypy mongoengine_softdelete --ignore-missing-imports

lint: pep8 mypy

clean:
	rm -rf build dist .coverage tests_coverage/ .mypy_cache .pytest_cache

build: clean
	poetry build

publish:
	poetry publish
