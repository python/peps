import datetime
from pathlib import Path
import subprocess

from docutils import nodes
from docutils import transforms
from docutils.transforms import misc
from docutils.transforms import references

from pep_sphinx_extensions import config


class PEPFooter(transforms.Transform):
    """Footer transforms for PEPs.

     - Appends external links to footnotes.
     - Creates a link to the (GitHub) source text.

    TargetNotes:
        Locate the `References` section, insert a placeholder at the end
        for an external target footnote insertion transform, and schedule
        the transform to run immediately.

    Source Link:
        Create the link to the source file from the document source path,
        and append the text to the end of the document.

    """

    # Uses same priority as docutils.transforms.TargetNotes
    default_priority = 520

    def apply(self) -> None:
        pep_source_path = Path(self.document["source"])
        if not pep_source_path.match("pep-*"):
            return  # not a PEP file, exit early

        doc = self.document[0]
        reference_section = copyright_section = None

        # Iterate through sections from the end of the document
        num_sections = len(doc)
        for i, section in enumerate(reversed(doc)):
            if not isinstance(section, nodes.section):
                continue
            title_words = section[0].astext().lower().split()
            if "references" in title_words:
                reference_section = section
                break
            elif "copyright" in title_words:
                copyright_section = num_sections - i - 1

        # Add a references section if we didn't find one
        if not reference_section:
            reference_section = nodes.section()
            reference_section += nodes.title("", "References")
            self.document.set_id(reference_section)
            if copyright_section:
                # Put the new "References" section before "Copyright":
                doc.insert(copyright_section, reference_section)
            else:
                # Put the new "References" section at end of doc:
                doc.append(reference_section)

        # Add and schedule execution of the TargetNotes transform
        pending = nodes.pending(references.TargetNotes)
        reference_section.append(pending)
        self.document.note_pending(pending, priority=0)

        # If there are no references after TargetNotes has finished, remove the
        # references section
        pending = nodes.pending(misc.CallBack, details={"callback": self.cleanup_callback})
        reference_section.append(pending)
        self.document.note_pending(pending, priority=1)

        # Add link to source text and last modified date
        self.add_source_link(pep_source_path)
        self.add_commit_history_info(pep_source_path)

    @staticmethod
    def cleanup_callback(pending: nodes.pending) -> None:
        """Remove an empty "References" section.

        Called after the `references.TargetNotes` transform is complete.

        """
        if len(pending.parent) == 2:  # <title> and <pending>
            pending.parent.parent.remove(pending.parent)

    def add_source_link(self, pep_source_path: Path) -> None:
        """Add link to source text on VCS (GitHub)"""
        source_link = config.pep_vcs_url + pep_source_path.name
        link_node = nodes.reference("", source_link, refuri=source_link)
        span_node = nodes.inline("", "Source: ", link_node)
        self.document.append(span_node)

    def add_commit_history_info(self, pep_source_path: Path) -> None:
        """Use local git history to find last modified date."""
        args = ["git", "--no-pager", "log", "-1", "--format=%at", pep_source_path.name]
        try:
            file_modified = subprocess.check_output(args)
            since_epoch = file_modified.decode("utf-8").strip()
            dt = datetime.datetime.utcfromtimestamp(float(since_epoch))
        except (subprocess.CalledProcessError, ValueError):
            return None

        commit_link = config.pep_commits_url + pep_source_path.name
        link_node = nodes.reference("", f"{dt.isoformat()}Z", refuri=commit_link)
        span_node = nodes.inline("", "Last modified: ", link_node)
        self.document.append(nodes.line("", "", classes=["zero-height"]))
        self.document.append(span_node)
