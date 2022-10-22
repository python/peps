# Builds PEP files to HTML using sphinx

PYTHON=python3
VENVDIR=.venv
JOBS=8
OUTPUT_DIR=build
RENDER_COMMAND=$(VENVDIR)/bin/python3 build.py -j $(JOBS) -o $(OUTPUT_DIR)

.PHONY: render
render: venv
	$(RENDER_COMMAND)

.PHONY: pages
pages: venv rss
	$(RENDER_COMMAND) --build-dirs

.PHONY: fail-warning
fail-warning: venv
	$(RENDER_COMMAND) --fail-on-warning

.PHONY: check-links
check-links: venv
	$(RENDER_COMMAND) --check-links

.PHONY: rss
rss: venv
	$(VENVDIR)/bin/python3 generate_rss.py

.PHONY: clean
clean: clean-venv
	-rm -rf build topic

.PHONY: clean-venv
clean-venv:
	rm -rf $(VENVDIR)

.PHONY: venv
venv:
	@if [ -d $(VENVDIR) ] ; then \
		echo "venv already exists."; \
		echo "To recreate it, remove it first with \`make clean-venv'."; \
	else \
		$(PYTHON) -m venv $(VENVDIR); \
		$(VENVDIR)/bin/python3 -m pip install -U pip wheel; \
		$(VENVDIR)/bin/python3 -m pip install -r requirements.txt; \
		echo "The venv has been created in the $(VENVDIR) directory"; \
	fi

.PHONY: lint
lint: venv
	$(VENVDIR)/bin/python3 -m pre_commit --version > /dev/null || $(VENVDIR)/bin/python3 -m pip install pre-commit
	$(VENVDIR)/bin/python3 -m pre_commit run --all-files

.PHONY: test
test: venv
	$(VENVDIR)/bin/python3 -bb -X dev -W error -m pytest

.PHONY: spellcheck
spellcheck: venv
	$(VENVDIR)/bin/python3 -m pre_commit --version > /dev/null || $(VENVDIR)/bin/python3 -m pip install pre-commit
	$(VENVDIR)/bin/python3 -m pre_commit run --all-files --hook-stage manual codespell
