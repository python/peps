# Builds PEP files to HTML using sphinx

# You can set these variables from the command line.
PYTHON       = python3
VENVDIR      = .venv
UV           = uv
# synchronise with render.yml -> deploy step
BUILDDIR     = build
SPHINXBUILD  = PATH=$(VENVDIR)/bin:$$PATH sphinx-build
BUILDER      = html
JOBS         = auto
SOURCES      =
REQUIREMENTS = requirements.txt
SPHINXERRORHANDLING = --fail-on-warning --keep-going --warning-file sphinx-warnings.txt

ALLSPHINXOPTS = --builder $(BUILDER) \
                --jobs $(JOBS) \
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
htmllive: SPHINXBUILD = PATH=$(VENVDIR)/bin:$$PATH sphinx-autobuild
# Arbitrarily selected ephemeral port between 49152–65535
# to avoid conflicts with other processes:
htmllive: SPHINXERRORHANDLING = --re-ignore="/\.idea/|/venv/|/numerical.rst|/pep-0000.rst|/topic/" --open-browser --delay 0 --port 55302
htmllive: _ensure-sphinx-autobuild html

## dirhtml        to render PEPs to "index.html" files within "pep-NNNN" directories
.PHONY: dirhtml
dirhtml: BUILDER = dirhtml
dirhtml: html
	mv $(BUILDDIR)/404/index.html $(BUILDDIR)/404.html

## linkcheck      to check validity of links within PEP sources
.PHONY: linkcheck
linkcheck: BUILDER = linkcheck
linkcheck: html

## clean          to remove the venv and build files
.PHONY: clean
clean: clean-venv
	-rm -rf $(BUILDDIR)

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
		if $(UV) --version >/dev/null 2>&1; then \
			$(UV) venv --python=$(PYTHON) $(VENVDIR); \
			VIRTUAL_ENV=$(VENVDIR) $(UV) pip install -r $(REQUIREMENTS); \
		else \
			$(PYTHON) -m venv $(VENVDIR); \
			$(VENVDIR)/bin/python3 -m pip install --upgrade pip; \
			$(VENVDIR)/bin/python3 -m pip install -r $(REQUIREMENTS); \
		fi; \
		echo "The venv has been created in the $(VENVDIR) directory"; \
	fi

.PHONY: _ensure-package
_ensure-package: venv
	if $(UV) --version >/dev/null 2>&1; then \
		VIRTUAL_ENV=$(VENVDIR) $(UV) pip install $(PACKAGE); \
	else \
		$(VENVDIR)/bin/python3 -m pip install $(PACKAGE); \
	fi

.PHONY: _ensure-pre-commit
_ensure-pre-commit:
	$(MAKE) _ensure-package PACKAGE=pre-commit

.PHONY: _ensure-sphinx-autobuild
_ensure-sphinx-autobuild:
	$(MAKE) _ensure-package PACKAGE=sphinx-autobuild

## lint           to lint all the files
.PHONY: lint
lint: _ensure-pre-commit
	$(VENVDIR)/bin/python3 -m pre_commit run --all-files

## test           to test the Sphinx extensions for PEPs
.PHONY: test
test: venv
	$(VENVDIR)/bin/python3 -bb -X dev -W error -m pytest

## spellcheck     to check spelling
.PHONY: spellcheck
spellcheck: _ensure-pre-commit
	$(VENVDIR)/bin/python3 -m pre_commit run --all-files --hook-stage manual codespell

.PHONY: help
help : Makefile
	@echo "Please use \`make <target>' where <target> is one of"
	@sed -n 's/^##//p' $<
