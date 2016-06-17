# Rules to only make the required HTML versions, not all of them,
# without the user having to keep track of which.
#
# Not really important, but convenient.

PEP2HTML=pep2html.py
PEP2RSS=pep2rss.py
GENPEPINDEX=genpepindex.py

PEPDIR=peps
OUTPUTDIR=output

PYTHON=python

.SUFFIXES: .txt .html

.txt.html:
	@$(PYTHON) $(PEP2HTML) $<

TARGETS=$(patsubst %.txt,%.html,$(wildcard $(PEPDIR)/pep-????.txt)) $(OUTPUTDIR)/pep-0000.html

all: pep-0000.txt $(TARGETS)

$(TARGETS): $(PEP2HTML)

pep-0000.txt: $(wildcard $(PEPDIR)/pep-????.txt) $(wildcard $(PEPDIR)/pep0/*.py)
	$(PYTHON) $(GENPEPINDEX) $(PEPDIR)

rss:
	$(PYTHON) $(PEP2RSS) $(PEPDIR)

install:
	echo "Installing is not necessary anymore. It will be done in post-commit."

clean:
	-rm -r $(OUTPUTDIR)

update:
	git pull https://github.com/python/peps.git

venv:
	$(PYTHON) -m venv venv
	./venv/bin/python -m pip install -U docutils
