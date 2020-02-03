SHELL=/bin/bash

.PHONY: browser_docs
browser_docs: docs
	firefox docs/_build/html/index.html 2>&1 > /dev/null &

.PHONY: docs
docs: $(find . -name "*.py")
	cd ./docs/ && \
	sphinx-apidoc -f -o src/ ../ && \
	$(MAKE) html # && \
	# $(MAKE) latexpdf

.PHONY: env
env: .refresh_env

.refresh_env: env.yml
	conda env create -f env.yml || conda env update -f env.yml
	touch .refresh_env
