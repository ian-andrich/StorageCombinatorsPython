SHELL=/bin/bash

.PHONY: env docs backends_up backends_stop backends_clean docs_html docs_latex docs_doctest tests
env: .refresh_env

.refresh_env: env.yml
	conda env create -f env.yml || conda env update -f env.yml
	touch .refresh_env

docs: backends_up docs_html docs_latex

docs_html: docs_doctest env
	(cd docs; make html)

docs_latex: docs_doctest env
	(cd docs; make latexpdf)

docs_doctest: src/* backends_up env
	(cd docs; make doctest)

backends_up: .backend_up

backends_stop:
	(cd tests/backends/; make stop)
	rm .backend_up

backends_clean:
	(cd tests/backends/; make clean_all)

test_libs: backends_up env
	python -m pytest tests/libs

.backend_up:
	(cd tests/backends/; make up)
	touch .backend_up
