# Build script for Sphinx documentation

from pathlib import Path
from sphinx.application import Sphinx

if __name__ == '__main__':
    root_directory = Path('.').absolute()
    docs_directory = Path(root_directory, 'peps')
    source_directory = configuration_directory = docs_directory
    build_directory = Path(root_directory, '_build')
    doctree_directory = Path(build_directory, '.doctrees')
    builder = 'html'

    app = Sphinx(source_directory, configuration_directory, build_directory, doctree_directory, builder)
    app.build(force_all=True)
