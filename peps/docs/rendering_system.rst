:author: Adam Turner

..
   We can't use :pep:`N` references in this document, as they use links relative
   to the current file, which doesn't work in a subdirectory like this one.


An Overview of the PEP Rendering System
=======================================

This document provides an overview of the PEP rendering system, as a companion
to `PEP 676 <https://peps.python.org/pep-0676/>`__.


1. Configuration
----------------

Configuration is stored in three files:

- ``peps/conf.py`` contains the majority of the Sphinx configuration
- ``peps/contents.rst`` contains the compulsory table of contents directive
- ``pep_sphinx_extensions/pep_theme/theme.conf`` sets the Pygments themes

The configuration:

- registers the custom Sphinx extension
- sets the ``.rst`` suffix to be parsed as PEPs
- tells Sphinx which source files to use
- registers the PEP theme, maths renderer, and template
- disables some default settings that are covered in the extension
- sets the default and "dark mode" code formatter styles


2. Orchestration
----------------

``build.py`` manages the rendering process.
Usage is covered in :doc:`Building PEPs Locally <./build>`.


3. Extension
------------

The Sphinx extension and theme are contained in the ``pep_sphinx_extensions``
directory.
The following is a brief overview of the stages of the PEP rendering process,
and how the extension functions at each point.


3.1 Extension setup
'''''''''''''''''''

The extension registers several objects:

- ``FileBuilder`` and ``DirectoryBuilder`` run the build process for file- and
  directory-based building, respectively.
- ``PEPParser`` registers the custom document transforms and parses PEPs to
  a Docutils document.
- ``PEPTranslator`` converts a Docutils document into HTML.
- ``PEPRole`` handles ``:pep:`` roles in the reStructuredText source.

The extension also patches default behaviour:

- updating the default settings
- updating the Docutils inliner
- using HTML maths display over MathJax


3.2 Builder initialised
'''''''''''''''''''''''

After the Sphinx builder object is created and initialised, we ensure the
configuration is correct for the builder chosen.

Currently this involves updating the relative link template.
See ``_update_config_for_builder`` in ``pep_sphinx_extensions/__init__.py``.


3.3 Before documents are read
'''''''''''''''''''''''''''''

The ``create_pep_zero`` hook is called. See `5. PEP 0`_.


3.4 Read document
'''''''''''''''''

Parsing the document is handled by ``PEPParser``
(``pep_sphinx_extensions.pep_processor.parsing.pep_parser.PEPParser``), a
lightweight wrapper over ``sphinx.parsers.RSTParser``.

``PEPParser`` reads the document with leading :rfc:`2822` headers and registers
the transforms we want to apply.
These are:

- ``PEPHeaders``
- ``PEPTitle``
- ``PEPContents``
- ``PEPFooter``

Transforms are then applied in priority order.


3.4.1 ``PEPRole`` role
**********************

This overrides the built-in ``:pep:`` role to return the correct URL.


3.4.2 ``PEPHeaders`` transform
******************************

PEPs start with a set of :rfc:`2822` headers,
per `PEP 1 <https://peps.python.org/pep-0001/>`__.
This transform validates that the required headers are present and of the
correct data type, and removes headers not for display.
It must run before the ``PEPTitle`` transform.


3.4.3 ``PEPTitle`` transform
****************************

We generate the title node from the parsed title in the PEP headers, and make
all nodes in the document children of the new title node.
This transform must also handle parsing reStructuredText markup within PEP
titles, such as `PEP 604 <https://peps.python.org/pep-0604/>`__.


3.4.4 ``PEPContents`` transform
*******************************

The automatic table of contents (TOC) is inserted in this transform in a
two-part process.

First, the transform inserts a placeholder for the TOC and a horizontal rule
after the document title and PEP headers.
A callback transform then recursively walks the document to create the TOC,
starting from after the placeholder node.
Whilst walking the document, all reference nodes in the titles are removed, and
titles are given a self-link.


3.4.5 ``PEPFooter`` transform
*****************************

This first builds a map of file modification times from a single git call, as
a speed-up. This will return incorrect results on a shallow checkout of the
repository, as is the default on continuous integration systems.

We then attempt to remove any empty references sections, and append metadata in
the footer (source link and last modified timestamp).


3.5 Prepare for writing
''''''''''''''''''''''''

``pep_html_builder.FileBuilder.prepare_writing`` initialises the bare minimum
of the Docutils writer and the settings for writing documents.
This provides a significant speed-up over the base Sphinx implementation, as
most of the data automatically initialised was unused.


3.6 Translate Docutils to HTML
'''''''''''''''''''''''''''''''

``PEPTranslator`` overrides paragraph and reference logic to replicate
processing from the previous ``docutils.writers.pep``-based system.
Paragraphs are made compact where possible by omitting ``<p>`` tags, and
footnote references are be enclosed in square brackets.


3.7 Prepare for export to Jinja
'''''''''''''''''''''''''''''''

Finally in ``pep_html_builder``, we gather all the parts to be passed to the
Jinja template.
This is also where we create the sidebar table of contents.

The HTML files are then written out to the build directory.


4. Theme
--------

The theme is comprised of the HTML template in
``pep_sphinx_extensions/pep_theme/templates/page.html`` and the stylesheets in
``pep_sphinx_extensions/pep_theme/static``.

The template is entirely self-contained, not relying on any default behaviour
from Sphinx.
It specifies the CSS files to include, the favicon, and basic semantic
information for the document structure.

The styles are defined in two parts:

- ``style.css`` handles the meat of the layout
- ``mq.css`` adds media queries for a responsive design


5. \PEP 0
---------

The generation of the index, PEP 0, happens in three phases.
The reStructuredText source file is generated, it is then added to Sphinx, and
finally the data is post processed.


5.1 File creation
'''''''''''''''''

``pep-0000.rst`` is created during a callback, before documents are loaded by
Sphinx.

We first parse the individual PEP files to get the :rfc:`2822` header, and then
parse and validate that metadata.

After collecting and validating all the PEP data, the index itself is created in
three steps:

1. Output the header text
2. Output the category and numerical indices
3. Output the author index

We then add the newly created PEP 0 file to two Sphinx variables so that it will
be processed as a normal source document.


5.2 Post processing
'''''''''''''''''''

The ``PEPHeaders`` transform schedules the \PEP 0 post-processing code.
This serves two functions: masking email addresses and linking numeric
PEP references to the actual documents.


6. RSS Feed
-----------

The RSS feed is created by extracting the header metadata and abstract from the
ten most recent PEPs.
