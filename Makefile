# Builds PEP files to HTML using sphinx
# Also contains testing targets

all: sphinx

PYTHON=python3

sphinx:
	$(PYTHON) build.py

fail_on_warning:
	$(PYTHON) build.py -f

check_links:
	$(PYTHON) build.py -c

rss:
	$(PYTHON) pep2rss.py .

update:
	git pull https://github.com/python/peps.git

venv:
	$(PYTHON) -m venv venv
	./venv/bin/python -m pip install -U docutils sphinx

package: all rss
	mkdir -p package/peps
	$(PYTHON) package.py
	cp pep-*.txt build/peps/
	cp pep-*.rst build/peps/
	cp *.png build/peps/
	cp *.rss package/peps
	tar -C package -czf package/peps.tar.gz peps
