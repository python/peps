#!/usr/bin/env python
"""Convert PEPs to (X)HTML - courtesy of /F

Usage: %(PROGRAM)s [options] [<peps> ...]

Options:

-u, --user
    python.org username

-b, --browse
    After generating the HTML, direct your web browser to view it
    (using the Python webbrowser module).  If both -i and -b are
    given, this will browse the on-line HTML; otherwise it will
    browse the local HTML.  If no pep arguments are given, this
    will browse PEP 0.

-i, --install
    After generating the HTML, install it and the plaintext source file
    (.txt) on python.org.  In that case the user's name is used in the scp
    and ssh commands, unless "-u username" is given (in which case, it is
    used instead).  Without -i, -u is ignored.

-l, --local
    Same as -i/--install, except install on the local machine.  Use this
    when logged in to the python.org machine (dinsdale).

-q, --quiet
    Turn off verbose messages.

-h, --help
    Print this help message and exit.

The optional arguments ``peps`` are either pep numbers, .rst or .txt files.
"""
import getopt
import glob
import os
import re
import sys
import time

from docutils import core, nodes, utils
from docutils.parsers import rst
from docutils.readers import standalone
from docutils.transforms import peps, frontmatter, Transform


class DataError(Exception):
    pass


PEPCVSURL = 'https://hg.python.org/peps/file/tip/pep-%04d.txt'


class PEPHeaders(Transform):
    """
    Process fields in a PEP's initial RFC-2822 header.
    """

    default_priority = 360

    pep_url = 'pep-%04d'
    pep_cvs_url = PEPCVSURL
    rcs_keyword_substitutions = (
        (re.compile(r'\$' r'RCSfile: (.+),v \$$', re.IGNORECASE), r'\1'),
        (re.compile(r'\$[a-zA-Z]+: (.+) \$$'), r'\1'),)

    def apply(self):
        if not len(self.document):
            # @@@ replace these DataErrors with proper system messages
            raise DataError('Document tree is empty.')
        header = self.document[0]
        if not isinstance(header, nodes.field_list) or \
                'rfc2822' not in header['classes']:
            raise DataError('Document does not begin with an RFC-2822 '
                            'header; it is not a PEP.')
        pep = cvs_url = None
        for field in header:
            if field[0].astext().lower() == 'pep':  # should be the first field
                value = field[1].astext()
                try:
                    pep = int(value)
                    cvs_url = self.pep_cvs_url % pep
                except ValueError:
                    pep = value
                    cvs_url = None
                    msg = self.document.reporter.warning(
                        '"PEP" header must contain an integer; "%s" is an '
                        'invalid value.' % pep, base_node=field)
                    msgid = self.document.set_id(msg)
                    prb = nodes.problematic(value, value or '(none)',
                                            refid=msgid)
                    prbid = self.document.set_id(prb)
                    msg.add_backref(prbid)
                    if len(field[1]):
                        field[1][0][:] = [prb]
                    else:
                        field[1] += nodes.paragraph('', '', prb)
                break
        if pep is None:
            raise DataError('Document does not contain an RFC-2822 "PEP" '
                            'header.')
        if pep == 0:
            # Special processing for PEP 0.
            pending = nodes.pending(peps.PEPZero)
            self.document.insert(1, pending)
            self.document.note_pending(pending)
        if len(header) < 2 or header[1][0].astext().lower() != 'title':
            raise DataError('No title!')
        for field in header:
            name = field[0].astext().lower()
            body = field[1]
            if len(body) > 1:
                raise DataError('PEP header field body contains multiple '
                                'elements:\n%s' % field.pformat(level=1))
            elif len(body) == 1:
                if not isinstance(body[0], nodes.paragraph):
                    raise DataError('PEP header field body may only contain '
                                    'a single paragraph:\n%s'
                                    % field.pformat(level=1))
            elif name == 'last-modified':
                date = time.strftime(
                    '%d-%b-%Y',
                    time.localtime(os.stat(self.document['source'])[8]))
                if cvs_url:
                    body += nodes.paragraph(
                        '', '', nodes.reference('', date, refuri=cvs_url))
            else:
                # empty
                continue
            para = body[0]
            if name in ('author', 'bdfl-delegate', 'sponsor'):
                for node in para:
                    if isinstance(node, nodes.reference):
                        node.replace_self(peps.mask_email(node))
            elif name == 'discussions-to':
                for node in para:
                    if isinstance(node, nodes.reference):
                        node.replace_self(peps.mask_email(node, pep))
            elif name in ('replaces', 'superseded-by', 'requires'):
                newbody = []
                space = nodes.Text(' ')
                for refpep in re.split(r',?\s+', body.astext()):
                    pepno = int(refpep)
                    newbody.append(nodes.reference(
                        refpep, refpep,
                        refuri=(self.document.settings.pep_base_url
                                + self.pep_url % pepno)))
                    newbody.append(space)
                para[:] = newbody[:-1]  # drop trailing space
            elif name == 'last-modified':
                utils.clean_rcs_keywords(para, self.rcs_keyword_substitutions)
                if cvs_url:
                    date = para.astext()
                    para[:] = [nodes.reference('', date, refuri=cvs_url)]
            elif name == 'content-type':
                pep_type = para.astext()
                uri = self.document.settings.pep_base_url + self.pep_url % 12
                para[:] = [nodes.reference('', pep_type, refuri=uri)]
            elif name == 'version' and len(body):
                utils.clean_rcs_keywords(para, self.rcs_keyword_substitutions)


class PEPReader(standalone.Reader):
    supported = ('pep',)
    """Contexts this reader supports."""

    settings_spec = (
        'PEP Reader Option Defaults',
        'The --pep-references and --rfc-references options (for the '
        'reStructuredText parser) are on by default.',
        ())

    config_section = 'pep reader'
    config_section_dependencies = ('readers', 'standalone reader')

    def get_transforms(self):
        transforms = standalone.Reader.get_transforms(self)
        # We have PEP-specific frontmatter handling.
        transforms.remove(frontmatter.DocTitle)
        transforms.remove(frontmatter.SectionSubTitle)
        transforms.remove(frontmatter.DocInfo)
        transforms.extend([PEPHeaders, peps.Contents, peps.TargetNotes])
        return transforms

    settings_default_overrides = {'pep_references': 1, 'rfc_references': 1}

    inliner_class = rst.states.Inliner

    def __init__(self, parser=None, _parser_name=None):
        """`parser` should be ``None``."""
        if parser is None:
            parser = rst.Parser(rfc2822=True, inliner=self.inliner_class())
        standalone.Reader.__init__(self, parser, '')


def fix_rst_pep(inpath, input_lines, outfile):
    output = core.publish_string(
        source=''.join(input_lines),
        source_path=inpath,
        destination_path=outfile.name,
        reader=PEPReader(),
        parser_name='restructuredtext',
        writer_name='pep_html',
        settings=None,
        # Allow Docutils traceback if there's an exception:
        settings_overrides={'traceback': 1, 'halt_level': 2})
    outfile.write(output.decode('utf-8'))


def get_input_lines(inpath):
    try:
        infile = open(inpath, encoding='utf-8')
    except FileNotFoundError as e:
        print('Error: Skipping missing PEP file:', e.filename, file=sys.stderr)
        sys.stderr.flush()
        return None
    lines = infile.read().splitlines(True)  # handles x-platform line endings
    infile.close()
    return lines


def find_pep(pep_str):
    """Find the .rst or .txt file indicated by a cmd line argument"""
    if os.path.exists(pep_str):
        return pep_str
    num = int(pep_str)
    rstpath = "pep-%04d.rst" % num
    if os.path.exists(rstpath):
        return rstpath
    return "pep-%04d.txt" % num


def make_html(inpath, verbose=0):
    input_lines = get_input_lines(inpath)
    if input_lines is None:
        return None
    outpath = os.path.splitext(inpath)[0] + ".html"
    if verbose:
        print(inpath, "(text/x-rst)", "->", outpath)
        sys.stdout.flush()
    outfile = open(outpath, "w", encoding='utf-8')
    fix_rst_pep(inpath, input_lines, outfile)
    outfile.close()
    os.chmod(outfile.name, 0o664)
    return outpath


def main(argv=None):
    verbose = 1

    if argv is None:
        argv = sys.argv[1:]

    opts, args = getopt.getopt(argv, 'bilhqu:', ['browse', 'install', 'local', 'help', 'quiet', 'user='])

    if args:
        pep_list = []
        html = []
        for pep in args:
            file = find_pep(pep)
            pep_list.append(file)
            newfile = make_html(file, verbose=verbose)
            if newfile:
                html.append(newfile)
    else:
        # do them all
        pep_list = []
        html = []
        files = glob.glob("pep-*.txt") + glob.glob("pep-*.rst")
        files.sort()
        for file in files:
            pep_list.append(file)
            newfile = make_html(file, verbose=verbose)
            if newfile:
                html.append(newfile)


if __name__ == "__main__":
    main()
