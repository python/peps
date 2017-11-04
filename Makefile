# Rules to only make the required HTML versions, not all of them,
# without the user having to keep track of which.
#
# Not really important, but convenient.

PEP2HTML=pep2html.py

PYTHON=python3

.SUFFIXES: .html .rst

.rst.html:
	@$(PYTHON) $(PEP2HTML) $<

TARGETS= $(patsubst %.rst,%.html,$(wildcard pep-????.rst)) $(patsubst %.rst,%.html,$(wildcard pep-????.rst))  pep-0000.html

all: pep-0000.rst $(TARGETS)

$(TARGETS): pep2html.py

pep-0000.rst: $(wildcard pep-????.rst) $(wildcard pep-????.rst) $(wildcard pep0/*.py)
	$(PYTHON) genpepindex.py .

rss:
	$(PYTHON) pep2rss.py .

install:
	echo "Installing is not necessary anymore. It will be done in post-commit."

clean:
	-rm pep-0000.rst
	-rm *.html

update:
	git pull https://github.com/python/peps.git

venv:
	$(PYTHON) -m venv venv
	./venv/bin/python -m pip install -U docutils
