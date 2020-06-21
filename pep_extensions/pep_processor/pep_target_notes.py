from pathlib import Path

from docutils import nodes
from docutils import transforms
from docutils.transforms import misc
from docutils.transforms import references


class PEPTargetNotes(transforms.Transform):

    """
    Locate the "References" section, insert a placeholder for an external
    target footnote insertion transform at the end, and schedule the
    transform to run immediately.
    """

    default_priority = 520

    def apply(self):
        if not Path(self.document["source"]).match("pep-*"):
            # not a PEP file
            return

        doc = self.document[0]
        i = len(doc) - 1
        reference_section = copyright = None
        while i >= 0 and isinstance(doc[i], nodes.section):
            title_words = doc[i][0].astext().lower().split()
            if 'references' in title_words:
                reference_section = doc[i]
                break
            elif 'copyright' in title_words:
                copyright = i
            i -= 1
        if not reference_section:
            reference_section = nodes.section()
            reference_section += nodes.title('', 'References')
            self.document.set_id(reference_section)
            if copyright:
                # Put the new "References" section before "Copyright":
                doc.insert(copyright, reference_section)
            else:
                # Put the new "References" section at end of doc:
                doc.append(reference_section)
        pending = nodes.pending(references.TargetNotes)
        reference_section.append(pending)
        self.document.note_pending(pending, 0)
        pending = nodes.pending(misc.CallBack, details={'callback': self.cleanup_callback})
        reference_section.append(pending)
        self.document.note_pending(pending, 1)

    @staticmethod
    def cleanup_callback(pending):
        """
        Remove an empty "References" section.

        Called after the `references.TargetNotes` transform is complete.
        """
        if len(pending.parent) == 2:    # <title> and <pending>
            pending.parent.parent.remove(pending.parent)
