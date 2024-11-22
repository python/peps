import time
from pathlib import Path
import subprocess

from docutils import nodes
from docutils import transforms


class PEPFooter(transforms.Transform):
    """Footer transforms for PEPs.

     - Remove the References/Footnotes section if it is empty when rendered.
     - Create a link to the (GitHub) source text.

    Source Link:
        Create the link to the source file from the document source path,
        and append the text to the end of the document.

    """

    # Uses same priority as docutils.transforms.TargetNotes
    default_priority = 520

    def apply(self) -> None:
        pep_source_path = Path(self.document["source"])
        if not pep_source_path.match("pep-????.???"):
            return  # not a PEP file, exit early

        # Iterate through sections from the end of the document
        for section in reversed(self.document[0]):
            if not isinstance(section, nodes.section):
                continue
            title_words = {*section[0].astext().lower().split()}
            if {"references", "footnotes"} & title_words:
                # Remove references/footnotes sections if there is no displayed
                # content (i.e. they only have title & link target nodes)
                to_hoist = []
                types = set()
                for node in section:
                    types.add(type(node))
                    if isinstance(node, nodes.target):
                        to_hoist.append(node)
                if types <= {nodes.title, nodes.target, nodes.system_message}:
                    section.parent.extend(to_hoist)
                    section.parent.remove(section)

        # Add link to source text and last modified date
        if pep_source_path.stem != "pep-0000":
            if pep_source_path.stem != "pep-0210":  # 210 is entirely empty, skip
                self.document += nodes.transition()
            self.document += _add_source_link(pep_source_path)
            self.document += _add_commit_history_info(pep_source_path)


def _add_source_link(pep_source_path: Path) -> nodes.paragraph:
    """Add link to source text on VCS (GitHub)"""
    source_link = f"https://github.com/python/peps/blob/main/peps/{pep_source_path.name}"
    link_node = nodes.reference("", source_link, refuri=source_link)
    return nodes.paragraph("", "Source: ", link_node)


def _add_commit_history_info(pep_source_path: Path) -> nodes.paragraph:
    """Use local git history to find last modified date."""
    try:
        iso_time = _LAST_MODIFIED_TIMES[pep_source_path.stem]
    except KeyError:
        return nodes.paragraph()

    commit_link = f"https://github.com/python/peps/commits/main/peps/{pep_source_path.name}"
    link_node = nodes.reference("", f"{iso_time} GMT", refuri=commit_link)
    return nodes.paragraph("", "Last modified: ", link_node)


def _get_last_modified_timestamps():
    # get timestamps and changed files from all commits (without paging results)
    args = ("git", "--no-pager", "log", "--format=#%at", "--name-only")
    ret = subprocess.run(args, stdout=subprocess.PIPE, text=True, encoding="utf-8")
    if ret.returncode:  # non-zero return code
        return {}
    all_modified = ret.stdout

    # remove "peps/" prefix from file names
    all_modified = all_modified.replace("\npeps/", "\n")

    # set up the dictionary with the *current* files
    peps_dir = Path(__file__, "..", "..", "..", "..", "peps").resolve()
    last_modified = {path.stem: "" for path in peps_dir.glob("pep-????.rst")}

    # iterate through newest to oldest, updating per file timestamps
    change_sets = all_modified.removeprefix("#").split("#")
    for change_set in change_sets:
        timestamp, files = change_set.split("\n", 1)
        for file in files.strip().split("\n"):
            if not file.startswith("pep-") or not file.endswith((".rst", ".txt")):
                continue  # not a PEP
            file = file[:-4]
            if last_modified.get(file) != "":
                continue  # most recent modified date already found
            try:
                y, m, d, hh, mm, ss, *_ = time.gmtime(float(timestamp))
            except ValueError:
                continue  # if float conversion fails
            last_modified[file] = f"{y:04}-{m:02}-{d:02} {hh:02}:{mm:02}:{ss:02}"

    return last_modified


_LAST_MODIFIED_TIMES = _get_last_modified_timestamps()
