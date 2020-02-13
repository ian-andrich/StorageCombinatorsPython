SHELL=/bin/bash

.PHONY: env
env: .refresh_env

.refresh_env: env.yml
	conda env create -f env.yml || conda env update -f env.yml
	touch .refresh_env

docs: src/* docs/**.rst docs/conf.py
	(cd tests/backends/; make up)
	(if (cd docs; make doctest && make html && make latexpdf) then (cd tests/backends/; make stop) else (cd tests/backends/; make stop; fail) fi)
