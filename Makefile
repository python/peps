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
	$(PEP2HTML) -i

clean:
	-rm *.html

update:
	cvs update -P -d
