# Builds PEP files to HTML using docutils or sphinx
# Also contains testing targets

PEP2HTML=pep2html.py

PYTHON=python3

VENV_DIR=venv

.SUFFIXES: .txt .html .rst

.txt.html:
	@$(PYTHON) $(PEP2HTML) $<

.rst.html:
	@$(PYTHON) $(PEP2HTML) $<

TARGETS= $(patsubst %.rst,%.html,$(wildcard pep-????.rst)) $(patsubst %.txt,%.html,$(wildcard pep-????.txt)) pep-0000.html

all: pep-0000.rst $(TARGETS)

$(TARGETS): pep2html.py

pep-0000.rst: $(wildcard pep-????.txt) $(wildcard pep-????.rst) $(wildcard pep0/*.py) genpepindex.py
	$(PYTHON) genpepindex.py .

rss:
	$(PYTHON) pep2rss.py .

install:
	echo "Installing is not necessary anymore. It will be done in post-commit."

clean:
	-rm pep-0000.rst
	-rm *.html
	-rm -rf build

update:
	git pull https://github.com/python/peps.git

venv:
	$(PYTHON) -m venv $(VENV_DIR)
	./$(VENV_DIR)/bin/python -m pip install -r requirements.txt

package: all rss
	mkdir -p build/peps
	cp pep-*.txt build/peps/
	cp pep-*.rst build/peps/
	cp *.html build/peps/
	cp *.png build/peps/
	cp *.rss build/peps/
	tar -C build -czf build/peps.tar.gz peps

lint:
	pre-commit --version > /dev/null || python3 -m pip install pre-commit
	pre-commit run --all-files

# New Sphinx targets:

SPHINX_JOBS=8
SPHINX_BUILD=$(PYTHON) build.py -j $(SPHINX_JOBS)

# TODO replace `rss:` with this when merged & tested
pep_rss:
	$(PYTHON) generate_rss.py

pages: pep_rss
	$(SPHINX_BUILD) --build-dirs --index-file

sphinx:
	$(SPHINX_BUILD)

fail-warning:
	$(SPHINX_BUILD) --fail-on-warning

check-links:
	$(SPHINX_BUILD) --check-links
