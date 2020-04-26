# Build script for Sphinx documentation

from pathlib import Path
from sphinx.application import Sphinx

if __name__ == '__main__':
    root_directory = Path('.').absolute()
    source_directory = root_directory
    configuration_directory = source_directory
    build_directory = root_directory / 'build'
    doctree_directory = build_directory / '.doctrees'
    builder = 'html'

    app = Sphinx(source_directory, configuration_directory, build_directory, doctree_directory, builder)
    app.build()
