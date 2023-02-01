# Builds PEP files to HTML using sphinx

PYTHON=python3
VENVDIR=.venv
JOBS=8
OUTPUT_DIR=build
RENDER_COMMAND=$(VENVDIR)/bin/python3 build.py -j $(JOBS) -o $(OUTPUT_DIR)

## html           to render PEPs to "pep-NNNN.html" files
.PHONY: html
html: venv
	$(RENDER_COMMAND)

## dirhtml        to render PEPs to "index.html" files within "pep-NNNN" directories
.PHONY: dirhtml
dirhtml: venv rss
	$(RENDER_COMMAND) --build-dirs

## fail-warning   to render PEPs to "pep-NNNN.html" files and fail the Sphinx build on any warning
.PHONY: fail-warning
fail-warning: venv
	$(RENDER_COMMAND) --fail-on-warning

## check-links    to check validity of links within PEP sources
.PHONY: check-links
check-links: venv
	$(RENDER_COMMAND) --check-links

## rss            to generate the peps.rss file
.PHONY: rss
rss: venv
	$(VENVDIR)/bin/python3 generate_rss.py -o $(OUTPUT_DIR)

## clean          to remove the venv and build files
.PHONY: clean
clean: clean-venv
	-rm -rf build topic

## clean-venv     to remove the venv
.PHONY: clean-venv
clean-venv:
	rm -rf $(VENVDIR)

## venv           to create a venv with necessary tools
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

## lint           to lint all the files
.PHONY: lint
lint: venv
	$(VENVDIR)/bin/python3 -m pre_commit --version > /dev/null || $(VENVDIR)/bin/python3 -m pip install pre-commit
	$(VENVDIR)/bin/python3 -m pre_commit run --all-files

## test           to test the Sphinx extensions for PEPs
.PHONY: test
test: venv
	$(VENVDIR)/bin/python3 -bb -X dev -W error -m pytest

## spellcheck     to check spelling
.PHONY: spellcheck
spellcheck: venv
	$(VENVDIR)/bin/python3 -m pre_commit --version > /dev/null || $(VENVDIR)/bin/python3 -m pip install pre-commit
	$(VENVDIR)/bin/python3 -m pre_commit run --all-files --hook-stage manual codespell

## render         (deprecated: use 'make html' alias instead)
.PHONY: render
render: html
	@echo "\033[0;33mWarning:\033[0;31m 'make render' \033[0;33mis deprecated, use\033[0;32m 'make html' \033[0;33malias instead\033[0m"

## pages          (deprecated: use 'make dirhtml' alias instead)
.PHONY: pages
pages: dirhtml
	@echo "\033[0;33mWarning:\033[0;31m 'make pages' \033[0;33mis deprecated, use\033[0;32m 'make dirhtml' \033[0;33malias instead\033[0m"

.PHONY: help
help : Makefile
	@echo "Please use \`make <target>' where <target> is one of"
	@sed -n 's/^##//p' $<
