# Builds PEP files to HTML using sphinx

# You can set these variables from the command line.
PYTHON       = python3
VENVDIR      = .venv
# synchronise with render.yml -> deploy step
BUILDDIR     = build
SPHINXBUILD  = PATH=$(VENVDIR)/bin:$$PATH sphinx-build
BUILDER      = html
JOBS         = auto
SOURCES      =
SPHINXERRORHANDLING = -W --keep-going -w sphinx-warnings.txt

ALLSPHINXOPTS = -b $(BUILDER) \
                -j $(JOBS) \
                $(SPHINXOPTS) $(SPHINXERRORHANDLING) \
                peps $(BUILDDIR) $(SOURCES)

## html           to render PEPs to "pep-NNNN.html" files
.PHONY: html
html: venv
	$(SPHINXBUILD) $(ALLSPHINXOPTS)

## htmlview       to open the index page built by the html target in your browser
.PHONY: htmlview
htmlview: html
	$(PYTHON) -c "import os, webbrowser; webbrowser.open('file://' + os.path.realpath('build/index.html'))"

## htmllive       to rebuild and reload HTML files in your browser
.PHONY: htmllive
htmllive: SPHINXBUILD = $(VENVDIR)/bin/sphinx-autobuild
htmllive: SPHINXERRORHANDLING = --re-ignore="/\.idea/|/venv/|/pep-0000.rst|/topic/" --open-browser --delay 0
htmllive: html

## dirhtml        to render PEPs to "index.html" files within "pep-NNNN" directories
.PHONY: dirhtml
dirhtml: BUILDER = dirhtml
dirhtml: html

## linkcheck      to check validity of links within PEP sources
.PHONY: linkcheck
check-links: BUILDER = linkcheck
check-links: html

## check-links    (deprecated: use 'make linkcheck' alias instead)
.PHONY: pages
check-links: linkcheck
	@echo "\033[0;33mWarning:\033[0;31m 'make check-links' \033[0;33mis deprecated, use\033[0;32m 'make linkcheck' \033[0;33malias instead\033[0m"

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
		echo "Creating venv in $(VENVDIR)"; \
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
