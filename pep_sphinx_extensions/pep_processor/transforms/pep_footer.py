import datetime
from pathlib import Path
import subprocess

from docutils import nodes
from docutils import transforms


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

        # Iterate through sections from the end of the document
        for section in reversed(self.document[0]):
            if not isinstance(section, nodes.section):
                continue
            title_words = section[0].astext().lower().split()
            if "references" in title_words:
                # Remove references section if there are no displayed
                # footnotes (it only has title & link target nodes)
                if all(isinstance(ref_node, (nodes.title, nodes.target))
                       for ref_node in section):
                    section.parent.remove(section)
                break

        # Add link to source text and last modified date
        if pep_source_path.stem != "pep-0000":
            self.document += _add_source_link(pep_source_path)
            self.document += _add_commit_history_info(pep_source_path)


def _add_source_link(pep_source_path: Path) -> nodes.paragraph:
    """Add link to source text on VCS (GitHub)"""
    source_link = f"https://github.com/python/peps/blob/main/{pep_source_path.name}"
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

    commit_link = f"https://github.com/python/peps/commits/main/{pep_source_path.name}"
    link_node = nodes.reference("", dt.isoformat(sep=" ") + " GMT", refuri=commit_link)
    return nodes.paragraph("", "Last modified: ", link_node)
