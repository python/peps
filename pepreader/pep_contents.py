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
        title = nodes.title('', 'contents')
        topic = nodes.topic('', title, classes=['contents'])
        name = nodes.fully_normalize_name('contents')
        if not self.document.has_name(name):
            topic['names'].append(name)
        self.document.note_implicit_target(topic)
        pending = nodes.pending(parts.Contents)
        topic += pending
        self.document.children[0].insert(2, topic)
        self.document.note_pending(pending)
