SHELL=/bin/bash

.PHONY: env docs backends_up backends_down docs_html docs_latex docs_doctest tests
env: .refresh_env

.refresh_env: env.yml
	conda env create -f env.yml || conda env update -f env.yml
	touch .refresh_env

docs: backends_up docs_html docs_latex

docs_html: docs_doctest
	(cd docs; make html)

docs_latex: docs_doctest
	(cd docs; make latexpdf)

docs_doctest: src/* backends_up
	(cd docs; make doctest)

backends_up: .backend_up

backends_down:
	(cd tests/backends/; make stop)
	rm .backend_up

.backend_up:
	(cd tests/backends/; make up)
	touch .backend_up
