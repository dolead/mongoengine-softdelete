install:
	poetry update

test:
	pytest

pep8:
	pycodestyle --ignore=E126,E127,E128,W503 mongoengine_softdelete/

mypy:
	mypy mongoengine_softdelete --ignore-missing-imports

lint: pep8 mypy

clean:
	rm -rf build dist

build: clean
	poetry build

publish:
	poetry publish
