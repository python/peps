import datetime
from pathlib import Path
import subprocess

from docutils import nodes
from docutils import transforms
from docutils.transforms import misc

from pep_sphinx_extensions import config


class PEPFooter(transforms.Transform):
    """Footer transforms for PEPs.

     - Removes the References section if it is empty when rendered.
     - Creates a link to the (GitHub) source text.

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
        reference_section = None

        # Iterate through sections from the end of the document
        for i, section in enumerate(reversed(doc)):
            if not isinstance(section, nodes.section):
                continue
            title_words = section[0].astext().lower().split()
            if "references" in title_words:
                reference_section = section
                break

        # Remove references section if there are no displayed footnotes
        if reference_section:
            pending = nodes.pending(misc.CallBack, details={"callback": _cleanup_callback})
            reference_section.append(pending)
            self.document.note_pending(pending, priority=1)

        # Add link to source text and last modified date
        if pep_source_path.stem != "pep-0000":
            self.document += _add_source_link(pep_source_path)
            self.document += _add_commit_history_info(pep_source_path)


def _cleanup_callback(pending: nodes.pending) -> None:
    """Remove an empty "References" section."""
    for ref_node in pending.parent:
        # Don't remove section if has more than title, link targets and pending
        if not isinstance(
                ref_node, (nodes.title, nodes.target, nodes.pending)):
            return
    pending.parent.parent.remove(pending.parent)


def _add_source_link(pep_source_path: Path) -> nodes.paragraph:
    """Add link to source text on VCS (GitHub)"""
    source_link = config.pep_vcs_url + pep_source_path.name
    link_node = nodes.reference("", source_link, refuri=source_link)
    return nodes.paragraph("", "Source: ", link_node)


def _add_commit_history_info(pep_source_path: Path) -> nodes.paragraph:
    """Use local git history to find last modified date."""
    args = ["git", "--no-pager", "log", "-1", "--format=%at", pep_source_path.name]
    try:
        file_modified = subprocess.check_output(args)
        since_epoch = file_modified.decode("utf-8").strip()
        dt = datetime.datetime.utcfromtimestamp(float(since_epoch))
    except (subprocess.CalledProcessError, ValueError):
        return nodes.paragraph()

    commit_link = config.pep_commits_url + pep_source_path.name
    link_node = nodes.reference("", f"{dt.isoformat(sep=' ')} GMT", refuri=commit_link)
    return nodes.paragraph("", "Last modified: ", link_node)
