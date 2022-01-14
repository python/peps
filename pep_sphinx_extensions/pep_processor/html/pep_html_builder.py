from pathlib import Path

from docutils import nodes
from docutils.frontend import OptionParser
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.writers.html import HTMLWriter

from sphinx.builders.dirhtml import DirectoryHTMLBuilder


class FileBuilder(StandaloneHTMLBuilder):
    copysource = False  # Prevent unneeded source copying - we link direct to GitHub
    search = False  # Disable search

    # Things we don't use but that need to exist:
    indexer = None
    relations = {}
    _script_files = _css_files = []
    globalcontext = {"script_files": [], "css_files": []}

    def prepare_writing(self, _doc_names: set[str]) -> None:
        self.docwriter = HTMLWriter(self)
        _opt_parser = OptionParser([self.docwriter], defaults=self.env.settings, read_config_files=True)
        self.docsettings = _opt_parser.get_default_values()

    def get_doc_context(self, docname: str, body: str, _metatags: str) -> dict:
        """Collect items for the template context of a page."""
        try:
            title = self.env.longtitles[docname].astext()
        except KeyError:
            title = ""

        # source filename
        file_is_rst = Path(self.env.srcdir, docname + ".rst").exists()
        source_name = f"{docname}.rst" if file_is_rst else f"{docname}.txt"

        # local table of contents
        toc_tree = self.env.tocs[docname].deepcopy()
        if len(toc_tree[0]) > 1:
            toc_tree = toc_tree[0][1]  # don't include document title
            for node in toc_tree.traverse(nodes.reference):
                node["refuri"] = node["anchorname"] or '#'  # fix targets
            toc = self.render_partial(toc_tree)["fragment"]
        else:
            toc = ""  # PEPs with no sections -- 9, 210

        return {"title": title, "sourcename": source_name, "toc": toc, "body": body}


class DirectoryBuilder(FileBuilder):
    # sync all overwritten things from DirectoryHTMLBuilder
    name = DirectoryHTMLBuilder.name
    get_target_uri = DirectoryHTMLBuilder.get_target_uri
    get_outfilename = DirectoryHTMLBuilder.get_outfilename
