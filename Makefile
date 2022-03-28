# Builds PEP files to HTML using sphinx

PYTHON=python3
VENVDIR=.venv
JOBS=8
RENDER_COMMAND=$(VENVDIR)/bin/python3 build.py -j $(JOBS)

render: venv
	$(RENDER_COMMAND)

pages: venv rss
	$(RENDER_COMMAND) --build-dirs

fail-warning: venv
	$(RENDER_COMMAND) --fail-on-warning

check-links: venv
	$(RENDER_COMMAND) --check-links

rss: venv
	$(VENVDIR)/bin/python3 generate_rss.py

clean: clean-venv
	-rm -rf build

clean-venv:
	rm -rf $(VENVDIR)

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

lint: venv
	$(VENVDIR)/bin/python3 -m pre_commit --version > /dev/null || $(VENVDIR)/bin/python3 -m pip install pre-commit
	$(VENVDIR)/bin/python3 -m pre_commit run --all-files

spellcheck: venv
	$(VENVDIR)/bin/python3 -m pre_commit --version > /dev/null || $(VENVDIR)/bin/python3 -m pip install pre-commit
	$(VENVDIR)/bin/python3 -m pre_commit run --all-files --hook-stage manual codespell
