from pathlib import Path

from docutils import nodes
from docutils import transforms
from docutils.transforms import parts


class PEPContents(transforms.Transform):
    """Add TOC placeholder and horizontal rule after PEP title and headers."""

    # Use same priority as docutils.transforms.Contents
    default_priority = 380

    def apply(self) -> None:
        if not Path(self.document["source"]).match("pep-*"):
            return  # not a PEP file, exit early

        # Create the contents placeholder section
        title = nodes.title("", "Contents")
        contents_topic = nodes.topic("", title, classes=["contents"])
        if not self.document.has_name("contents"):
            contents_topic["names"].append("contents")
        self.document.note_implicit_target(contents_topic)

        # Add a table of contents builder
        pending = nodes.pending(Contents)
        contents_topic += pending
        self.document.note_pending(pending)

        # Insert the toc after title and PEP headers
        self.document.children[0].insert(2, contents_topic)

        # Add a horizontal rule before contents
        transition = nodes.transition()
        self.document[0].insert(2, transition)


class Contents(parts.Contents):
    """Build Table of Contents from document."""
    def __init__(self, document, startnode=None):
        super().__init__(document, startnode)

        # used in parts.Contents.build_contents
        self.toc_id = None
        self.backlinks = None

    def apply(self) -> None:
        # used in parts.Contents.build_contents
        self.toc_id = self.startnode.parent["ids"][0]
        self.backlinks = self.document.settings.toc_backlinks

        # let the writer (or output software) build the contents list?
        if getattr(self.document.settings, "use_latex_toc", False):
            # move customisation settings to the parent node
            self.startnode.parent.attributes.update(self.startnode.details)
            self.startnode.parent.remove(self.startnode)
        else:
            contents = self.build_contents(self.document[0])
            if contents:
                self.startnode.replace_self(contents)
            else:
                # if no contents, remove the empty placeholder
                self.startnode.parent.parent.remove(self.startnode.parent)
