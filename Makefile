# Builds PEP files to HTML using sphinx

# You can set these variables from the command line.
PYTHON       = python3
VENVDIR      = .venv
SPHINXBUILD  = PATH=$(VENVDIR)/bin:$$PATH sphinx-build
BUILDER      = html
JOBS         = 8
SOURCES      =
# synchronise with render.yml -> deploy step
OUTPUT_DIR   = build
SPHINXERRORHANDLING = -W --keep-going -w sphinx-warnings.txt

ALLSPHINXOPTS = -b $(BUILDER) -j $(JOBS) \
                $(SPHINXOPTS) $(SPHINXERRORHANDLING) peps $(OUTPUT_DIR) $(SOURCES)

## html           to render PEPs to "pep-NNNN.html" files
.PHONY: html
html: venv
	$(SPHINXBUILD) $(ALLSPHINXOPTS)

## htmlview       to open the index page built by the html target in your browser
.PHONY: htmlview
htmlview: html
	$(PYTHON) -c "import os, webbrowser; webbrowser.open('file://' + os.path.realpath('build/index.html'))"

## dirhtml        to render PEPs to "index.html" files within "pep-NNNN" directories
.PHONY: dirhtml
dirhtml: BUILDER = dirhtml
dirhtml: venv
	$(SPHINXBUILD) $(ALLSPHINXOPTS)

## check-links    to check validity of links within PEP sources
.PHONY: check-links
check-links: BUILDER = linkcheck
check-links: venv
	$(SPHINXBUILD) $(ALLSPHINXOPTS)

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

.PHONY: help
help : Makefile
	@echo "Please use \`make <target>' where <target> is one of"
	@sed -n 's/^##//p' $<
