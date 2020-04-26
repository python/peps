# Rules to only make the required HTML versions, not all of them,
# without the user having to keep track of which.
#
# Not really important, but convenient.

PYTHON=python3

all: sphinx

sphinx:
	sphinx-build -j auto -b html . build

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
	$(PYTHON) -m venv venv
	./venv/bin/python -m pip install -U docutils sphinx

package: all rss
	mkdir -p package/peps
	cp -R build/. package/peps
	cp *.rss package/peps
	tar -C package -czf package/peps.tar.gz peps
