# Rules to only make the required HTML versions, not all of them,
# without the user having to keep track of which.
#
# Not really important, but convenient.

PEP2HTML=pep2html.py

PYTHON=python3

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
	-rm pep-0000.txt
	-rm *.html
	-rm -rf build

update:
	git pull https://github.com/python/peps.git

venv:
	$(PYTHON) -m venv venv
	./venv/bin/python -m pip install -U docutils

package: all rss
	mkdir -p build/peps
	cp pep-*.txt build/peps/
	cp pep-*.rst build/peps/
	cp *.html build/peps/
	cp *.png build/peps/
	cp *.rss build/peps/
	tar -C build -czf build/peps.tar.gz peps
