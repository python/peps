#!/usr/bin/env python3.9
"""Convert PEPs to (X)HTML - courtesy of /F

Usage: %(PROGRAM)s [options] [<peps> ...]

Options:

-q, --quiet
    Turn off verbose messages.

-h, --help
    Print this help message and exit.

The optional arguments ``peps`` are either pep numbers, .rst or .txt files.
"""

import sys
import os
import re
import glob
import getopt
import errno
import time
from io import open
from pathlib import Path

from docutils import core, nodes, utils
from docutils.readers import standalone
from docutils.transforms import frontmatter, peps, Transform
from docutils.parsers import rst
from docutils.parsers.rst import roles

class DataError(Exception):
    pass

PROGRAM = sys.argv[0]
PEPCVSURL = ('https://hg.python.org/peps/file/tip/pep-%04d.txt')

def usage(code, msg=''):
    """Print usage message and exit.  Uses stderr if code != 0."""
    if code == 0:
        out = sys.stdout
    else:
        out = sys.stderr
    print(__doc__ % globals(), file=out)
    if msg:
        print(msg, file=out)
    sys.exit(code)

EXPLICIT_TITLE_RE = re.compile(r'^(.+?)\s*(?<!\x00)<(.*?)>$', re.DOTALL)

def _pep_reference_role(role, rawtext, text, lineno, inliner,
                        options={}, content=[]):
    matched = EXPLICIT_TITLE_RE.match(text)
    if matched:
        title = utils.unescape(matched.group(1))
        target = utils.unescape(matched.group(2))
    else:
        target = utils.unescape(text)
        title = "PEP " + utils.unescape(text)
    pep_str, _, fragment = target.partition("#")
    try:
        pepnum = int(pep_str)
        if pepnum < 0 or pepnum > 9999:
            raise ValueError
    except ValueError:
        msg = inliner.reporter.error(
            'PEP number must be a number from 0 to 9999; "%s" is invalid.'
            % pep_str, line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]
    # Base URL mainly used by inliner.pep_reference; so this is correct:
    ref = (inliner.document.settings.pep_base_url
           + inliner.document.settings.pep_file_url_template % pepnum)
    if fragment:
        ref += "#" + fragment
    roles.set_classes(options)
    return [nodes.reference(rawtext, title, refuri=ref, **options)], []
def _rfc_reference_role(role, rawtext, text, lineno, inliner,
                        options={}, content=[]):
    matched = EXPLICIT_TITLE_RE.match(text)
    if matched:
        title = utils.unescape(matched.group(1))
        target = utils.unescape(matched.group(2))
    else:
        target = utils.unescape(text)
        title = "RFC " + utils.unescape(text)
    pep_str, _, fragment = target.partition("#")
    try:
        rfcnum = int(pep_str)
        if rfcnum < 0 or rfcnum > 9999:
            raise ValueError
    except ValueError:
        msg = inliner.reporter.error(
            'RFC number must be a number from 0 to 9999; "%s" is invalid.'
            % pep_str, line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]
    # Base URL mainly used by inliner.pep_reference; so this is correct:
    ref = (inliner.document.settings.rfc_base_url + inliner.rfc_url % rfcnum)
    if fragment:
        ref += "#" + fragment
    roles.set_classes(options)
    return [nodes.reference(rawtext, title, refuri=ref, **options)], []

roles.register_canonical_role("pep-reference", _pep_reference_role)
roles.register_canonical_role("rfc-reference", _rfc_reference_role)

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
        pep = None
        for field in header:
            if field[0].astext().lower() == 'pep': # should be the first field
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
            if name in ('author', 'bdfl-delegate', 'pep-delegate', 'sponsor'):
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
                para[:] = newbody[:-1] # drop trailing space
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


class PEPFooter(Transform):
    """Remove the References/Footnotes section if it is empty when rendered."""

    # Set low priority so ref targets aren't removed before they are needed
    default_priority = 999

    def apply(self):
        pep_source_path = Path(self.document['source'])
        if not pep_source_path.match('pep-*'):
            return  # not a PEP file, exit early

        # Iterate through sections from the end of the document
        for section in reversed(self.document):
            if not isinstance(section, nodes.section):
                continue
            title_words = {*section[0].astext().lower().split()}
            if {"references", "footnotes"} & title_words:
                # Remove references/footnotes sections if there is no displayed
                # content (i.e. they only have title & link target nodes)
                if all(isinstance(ref_node, (nodes.title, nodes.target))
                       for ref_node in section):
                    section.parent.remove(section)


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
        transforms.extend([PEPHeaders, peps.Contents, PEPFooter])
        return transforms

    settings_default_overrides = {'pep_references': 1, 'rfc_references': 1}

    inliner_class = rst.states.Inliner

    def __init__(self, parser=None, parser_name=None):
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
    except IOError as e:
        if e.errno != errno.ENOENT: raise
        print('Error: Skipping missing PEP file:', e.filename, file=sys.stderr)
        sys.stderr.flush()
        return None
    lines = infile.read().splitlines(1) # handles x-platform line endings
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
    # defaults
    verbose = 1

    if argv is None:
        argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(
            argv, 'hq:',
            ['help', 'quiet'])
    except getopt.error as msg:
        usage(1, msg)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(0)
        elif opt in ('-q', '--quiet'):
            verbose = 0

    if args:
        for pep in args:
            file = find_pep(pep)
            make_html(file, verbose=verbose)
    else:
        # do them all
        files = glob.glob("pep-*.txt") + glob.glob("pep-*.rst")
        files.sort()
        for file in files:
            make_html(file, verbose=verbose)

if __name__ == "__main__":
    main()
