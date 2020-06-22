from pathlib import Path
from docutils import nodes
from docutils import transforms
from docutils.transforms import parts


class PEPContents(transforms.Transform):

    """
    Insert an empty table of contents topic and a transform placeholder into
    the document after the RFC 2822 header.
    """

    default_priority = 380

    def apply(self):
        if not Path(self.document["source"]).match("pep-*"):
            # not a PEP file
            return
        title = nodes.title('', 'Contents')
        topic = nodes.topic('', title, classes=['contents'])
        name = nodes.fully_normalize_name('contents')
        if not self.document.has_name(name):
            topic['names'].append(name)
        self.document.note_implicit_target(topic)
        pending = nodes.pending(Contents)
        topic += pending
        self.document.children[0].insert(2, topic)
        self.document.note_pending(pending)

        # Add horizontal rule before contents
        transition = nodes.transition()
        self.document[0].insert(2, transition)


class Contents(parts.Contents):
    def __init__(self, document, startnode=None):
        super().__init__(document, startnode)
        self.toc_id = None
        self.backlinks = None

    def apply(self):
        # let the writer (or output software) build the contents list?
        try:
            toc_by_writer = self.document.settings.use_latex_toc
        except AttributeError:
            toc_by_writer = False

        details = self.startnode.details
        startnode = self.document[0]
        self.toc_id = self.startnode.parent['ids'][0]
        self.backlinks = self.document.settings.toc_backlinks

        if toc_by_writer:
            # move customization settings to the parent node
            self.startnode.parent.attributes.update(details)
            self.startnode.parent.remove(self.startnode)
        else:
            contents = self.build_contents(startnode)
            if len(contents):
                self.startnode.replace_self(contents)
            else:
                self.startnode.parent.parent.remove(self.startnode.parent)
