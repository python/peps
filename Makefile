# Rules to only make the required HTML versions, not all of them,
# without the user having to keep track of which.
#
# Not really important, but convenient.

PEP2HTML=./pep2html.py

.SUFFIXES: .txt .html

.txt.html:
	$(PEP2HTML) $<

TARGETS=$(patsubst %.txt,%.html,$(wildcard pep-*.txt))

all:	$(TARGETS)

$(TARGETS): pep2html.py

install:
	echo "Installing is not necessary anymore. It will be done in post-commit."

clean:
	-rm *.html

update:
	svn update
