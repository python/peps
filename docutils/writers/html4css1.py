# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
Simple HyperText Markup Language document tree Writer.

The output conforms to the HTML 4.01 Transitional DTD and to the Extensible
HTML version 1.0 Transitional DTD (*almost* strict).  The output contains a
minimum of formatting information.  A cascading style sheet ("default.css" by
default) is required for proper viewing with a modern graphical browser.
"""

__docformat__ = 'reStructuredText'


import sys
import os
import time
import re
from types import ListType
import docutils
from docutils import nodes, utils, writers, languages


class Writer(writers.Writer):

    supported = ('html', 'html4css1', 'xhtml')
    """Formats this writer supports."""

    settings_spec = (
        'HTML-Specific Options',
        None,
        (('Specify a stylesheet URL, used verbatim.  Default is '
          '"default.css".',
          ['--stylesheet'],
          {'default': 'default.css', 'metavar': '<URL>'}),
         ('Specify a stylesheet file, relative to the current working '
          'directory.  The path is adjusted relative to the output HTML '
          'file.  Overrides --stylesheet.',
          ['--stylesheet-path'],
          {'metavar': '<file>'}),
         ('Link to the stylesheet in the output HTML file.  This is the '
          'default.',
          ['--link-stylesheet'],
          {'dest': 'embed_stylesheet', 'action': 'store_false'}),
         ('Embed the stylesheet in the output HTML file.  The stylesheet '
          'file must be accessible during processing (--stylesheet-path is '
          'recommended).  The stylesheet is embedded inside a comment, so it '
          'must not contain the text "--" (two hyphens).  Default: link the '
          'stylesheet, do not embed it.',
          ['--embed-stylesheet'],
          {'action': 'store_true'}),
         ('Format for footnote references: one of "superscript" or '
          '"brackets".  Default is "superscript".',
          ['--footnote-references'],
          {'choices': ['superscript', 'brackets'], 'default': 'superscript',
           'metavar': '<FORMAT>'}),
         ('Remove extra vertical whitespace between items of bullet lists '
          'and enumerated lists, when list items are "simple" (i.e., all '
          'items each contain one paragraph and/or one "simple" sublist '
          'only).  Default: enabled.',
          ['--compact-lists'],
          {'default': 1, 'action': 'store_true'}),
         ('Disable compact simple bullet and enumerated lists.',
          ['--no-compact-lists'],
          {'dest': 'compact_lists', 'action': 'store_false'}),))

    relative_path_settings = ('stylesheet_path',)

    output = None
    """Final translated form of `document`."""

    def __init__(self):
        writers.Writer.__init__(self)
        self.translator_class = HTMLTranslator

    def translate(self):
        visitor = self.translator_class(self.document)
        self.document.walkabout(visitor)
        self.output = visitor.astext()
        self.head_prefix = visitor.head_prefix
        self.stylesheet = visitor.stylesheet
        self.head = visitor.head
        self.body_prefix = visitor.body_prefix
        self.body_pre_docinfo = visitor.body_pre_docinfo
        self.docinfo = visitor.docinfo
        self.body = visitor.body
        self.body_suffix = visitor.body_suffix


class HTMLTranslator(nodes.NodeVisitor):

    """
    This HTML writer has been optimized to produce visually compact
    lists (less vertical whitespace).  HTML's mixed content models
    allow list items to contain "<li><p>body elements</p></li>" or
    "<li>just text</li>" or even "<li>text<p>and body
    elements</p>combined</li>", each with different effects.  It would
    be best to stick with strict body elements in list items, but they
    affect vertical spacing in browsers (although they really
    shouldn't).

    Here is an outline of the optimization:

    - Check for and omit <p> tags in "simple" lists: list items
      contain either a single paragraph, a nested simple list, or a
      paragraph followed by a nested simple list.  This means that
      this list can be compact:

          - Item 1.
          - Item 2.

      But this list cannot be compact:

          - Item 1.

            This second paragraph forces space between list items.

          - Item 2.

    - In non-list contexts, omit <p> tags on a paragraph if that
      paragraph is the only child of its parent (footnotes & citations
      are allowed a label first).

    - Regardless of the above, in definitions, table cells, field
      bodies, option descriptions, and list items, mark the first
      child with 'class="first"' if it is a paragraph.  The stylesheet
      sets the top margin to 0 for these paragraphs.

    The ``no_compact_lists`` setting (``--no-compact-lists`` command-line
    option) disables list whitespace optimization.
    """

    xml_declaration = '<?xml version="1.0" encoding="%s" ?>\n'
    doctype = ('<!DOCTYPE html' 
               ' PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"'
               ' "http://www.w3.org/TR/xhtml1/DTD/'
               'xhtml1-transitional.dtd">\n')
    html_head = ('<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="%s" '
                 'lang="%s">\n<head>\n')
    content_type = ('<meta http-equiv="Content-Type" content="text/html; '
                    'charset=%s" />\n')
    generator = ('<meta name="generator" content="Docutils %s: '
                 'http://docutils.sourceforge.net/" />\n')
    stylesheet_link = '<link rel="stylesheet" href="%s" type="text/css" />\n'
    embedded_stylesheet = '<style type="text/css"><!--\n\n%s\n--></style>\n'
    named_tags = {'a': 1, 'applet': 1, 'form': 1, 'frame': 1, 'iframe': 1,
                  'img': 1, 'map': 1}
    words_and_spaces = re.compile(r'\S+| +|\n')

    def __init__(self, document):
        nodes.NodeVisitor.__init__(self, document)
        self.settings = settings = document.settings
        lcode = settings.language_code
        self.language = languages.get_language(lcode)
        self.head_prefix = [
              self.xml_declaration % settings.output_encoding,
              self.doctype,
              self.html_head % (lcode, lcode),
              self.content_type % settings.output_encoding,
              self.generator % docutils.__version__]
        self.head = []
        if settings.embed_stylesheet:
            stylesheet = self.get_stylesheet_reference(os.getcwd())
            stylesheet_text = open(stylesheet).read()
            self.stylesheet = [self.embedded_stylesheet % stylesheet_text]
        else:
            stylesheet = self.get_stylesheet_reference()
            if stylesheet:
                self.stylesheet = [self.stylesheet_link % stylesheet]
            else:
                self.stylesheet = []
        self.body_prefix = ['</head>\n<body>\n']
        self.body_pre_docinfo = []
        self.docinfo = []
        self.body = []
        self.body_suffix = ['</body>\n</html>\n']
        self.section_level = 0
        self.context = []
        self.topic_class = ''
        self.colspecs = []
        self.compact_p = 1
        self.compact_simple = None
        self.in_docinfo = None

    def get_stylesheet_reference(self, relative_to=None):
        settings = self.settings
        if settings.stylesheet_path:
            if relative_to == None:
                relative_to = settings._destination
            return utils.relative_path(relative_to, settings.stylesheet_path)
        else:
            return settings.stylesheet

    def astext(self):
        return ''.join(self.head_prefix + self.head + self.stylesheet
                       + self.body_prefix + self.body_pre_docinfo
                       + self.docinfo + self.body + self.body_suffix)

    def encode(self, text):
        """Encode special characters in `text` & return."""
        # @@@ A codec to do these and all other HTML entities would be nice.
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace('"', "&quot;")
        text = text.replace(">", "&gt;")
        text = text.replace("@", "&#64;") # may thwart some address harvesters
        return text

    def attval(self, text,
               whitespace=re.compile('[\n\r\t\v\f]')):
        """Cleanse, HTML encode, and return attribute value text."""
        return self.encode(whitespace.sub(' ', text))

    def starttag(self, node, tagname, suffix='\n', infix='', **attributes):
        """
        Construct and return a start tag given a node (id & class attributes
        are extracted), tag name, and optional attributes.
        """
        tagname = tagname.lower()
        atts = {}
        for (name, value) in attributes.items():
            atts[name.lower()] = value
        for att in ('class',):          # append to node attribute
            if node.has_key(att) or atts.has_key(att):
                atts[att] = \
                      (node.get(att, '') + ' ' + atts.get(att, '')).strip()
        for att in ('id',):             # node attribute overrides
            if node.has_key(att):
                atts[att] = node[att]
        if atts.has_key('id') and self.named_tags.has_key(tagname):
            atts['name'] = atts['id']   # for compatibility with old browsers
        attlist = atts.items()
        attlist.sort()
        parts = [tagname]
        for name, value in attlist:
            if value is None:           # boolean attribute
                # According to the HTML spec, ``<element boolean>`` is good,
                # ``<element boolean="boolean">`` is bad.
                # (But the XHTML (XML) spec says the opposite.  <sigh>)
                parts.append(name.lower())
            elif isinstance(value, ListType):
                values = [str(v) for v in value]
                parts.append('%s="%s"' % (name.lower(),
                                          self.attval(' '.join(values))))
            else:
                parts.append('%s="%s"' % (name.lower(),
                                          self.attval(str(value))))
        return '<%s%s>%s' % (' '.join(parts), infix, suffix)

    def emptytag(self, node, tagname, suffix='\n', **attributes):
        """Construct and return an XML-compatible empty tag."""
        return self.starttag(node, tagname, suffix, infix=' /', **attributes)

    def visit_Text(self, node):
        self.body.append(self.encode(node.astext()))

    def depart_Text(self, node):
        pass

    def visit_address(self, node):
        self.visit_docinfo_item(node, 'address', meta=None)
        self.body.append(self.starttag(node, 'pre', CLASS='address'))

    def depart_address(self, node):
        self.body.append('\n</pre>\n')
        self.depart_docinfo_item()

    def visit_admonition(self, node, name):
        self.body.append(self.starttag(node, 'div', CLASS=name))
        self.body.append('<p class="admonition-title">'
                         + self.language.labels[name] + '</p>\n')

    def depart_admonition(self):
        self.body.append('</div>\n')

    def visit_attention(self, node):
        self.visit_admonition(node, 'attention')

    def depart_attention(self, node):
        self.depart_admonition()

    def visit_author(self, node):
        self.visit_docinfo_item(node, 'author')

    def depart_author(self, node):
        self.depart_docinfo_item()

    def visit_authors(self, node):
        pass

    def depart_authors(self, node):
        pass

    def visit_block_quote(self, node):
        self.body.append(self.starttag(node, 'blockquote'))

    def depart_block_quote(self, node):
        self.body.append('</blockquote>\n')

    def check_simple_list(self, node):
        """Check for a simple list that can be rendered compactly."""
        visitor = SimpleListChecker(self.document)
        try:
            node.walk(visitor)
        except nodes.NodeFound:
            return None
        else:
            return 1

    def visit_bullet_list(self, node):
        atts = {}
        old_compact_simple = self.compact_simple
        self.context.append((self.compact_simple, self.compact_p))
        self.compact_p = None
        self.compact_simple = (self.settings.compact_lists and
                               (self.compact_simple
                                or self.topic_class == 'contents'
                                or self.check_simple_list(node)))
        if self.compact_simple and not old_compact_simple:
            atts['class'] = 'simple'
        self.body.append(self.starttag(node, 'ul', **atts))

    def depart_bullet_list(self, node):
        self.compact_simple, self.compact_p = self.context.pop()
        self.body.append('</ul>\n')

    def visit_caption(self, node):
        self.body.append(self.starttag(node, 'p', '', CLASS='caption'))

    def depart_caption(self, node):
        self.body.append('</p>\n')

    def visit_caution(self, node):
        self.visit_admonition(node, 'caution')

    def depart_caution(self, node):
        self.depart_admonition()

    def visit_citation(self, node):
        self.body.append(self.starttag(node, 'table', CLASS='citation',
                                       frame="void", rules="none"))
        self.body.append('<colgroup><col class="label" /><col /></colgroup>\n'
                         '<col />\n'
                         '<tbody valign="top">\n'
                         '<tr>')
        self.footnote_backrefs(node)

    def depart_citation(self, node):
        self.body.append('</td></tr>\n'
                         '</tbody>\n</table>\n')

    def visit_citation_reference(self, node):
        href = ''
        if node.has_key('refid'):
            href = '#' + node['refid']
        elif node.has_key('refname'):
            href = '#' + self.document.nameids[node['refname']]
        self.body.append(self.starttag(node, 'a', '[', href=href,
                                       CLASS='citation-reference'))

    def depart_citation_reference(self, node):
        self.body.append(']</a>')

    def visit_classifier(self, node):
        self.body.append(' <span class="classifier-delimiter">:</span> ')
        self.body.append(self.starttag(node, 'span', '', CLASS='classifier'))

    def depart_classifier(self, node):
        self.body.append('</span>')

    def visit_colspec(self, node):
        self.colspecs.append(node)

    def depart_colspec(self, node):
        pass

    def write_colspecs(self):
        width = 0
        for node in self.colspecs:
            width += node['colwidth']
        for node in self.colspecs:
            colwidth = int(node['colwidth'] * 100.0 / width + 0.5)
            self.body.append(self.emptytag(node, 'col',
                                           width='%i%%' % colwidth))
        self.colspecs = []

    def visit_comment(self, node,
                      sub=re.compile('-(?=-)').sub):
        """Escape double-dashes in comment text."""
        self.body.append('<!-- %s -->\n' % sub('- ', node.astext()))
        # Content already processed:
        raise nodes.SkipNode

    def visit_contact(self, node):
        self.visit_docinfo_item(node, 'contact', meta=None)

    def depart_contact(self, node):
        self.depart_docinfo_item()

    def visit_copyright(self, node):
        self.visit_docinfo_item(node, 'copyright')

    def depart_copyright(self, node):
        self.depart_docinfo_item()

    def visit_danger(self, node):
        self.visit_admonition(node, 'danger')

    def depart_danger(self, node):
        self.depart_admonition()

    def visit_date(self, node):
        self.visit_docinfo_item(node, 'date')

    def depart_date(self, node):
        self.depart_docinfo_item()

    def visit_decoration(self, node):
        pass

    def depart_decoration(self, node):
        pass

    def visit_definition(self, node):
        self.body.append('</dt>\n')
        self.body.append(self.starttag(node, 'dd', ''))
        if len(node):
            node[0].set_class('first')
            node[-1].set_class('last')

    def depart_definition(self, node):
        self.body.append('</dd>\n')

    def visit_definition_list(self, node):
        self.body.append(self.starttag(node, 'dl'))

    def depart_definition_list(self, node):
        self.body.append('</dl>\n')

    def visit_definition_list_item(self, node):
        pass

    def depart_definition_list_item(self, node):
        pass

    def visit_description(self, node):
        self.body.append(self.starttag(node, 'td', ''))
        if len(node):
            node[0].set_class('first')
            node[-1].set_class('last')

    def depart_description(self, node):
        self.body.append('</td>')

    def visit_docinfo(self, node):
        self.context.append(len(self.body))
        self.body.append(self.starttag(node, 'table', CLASS='docinfo',
                                       frame="void", rules="none"))
        self.body.append('<col class="docinfo-name" />\n'
                         '<col class="docinfo-content" />\n'
                         '<tbody valign="top">\n')
        self.in_docinfo = 1

    def depart_docinfo(self, node):
        self.body.append('</tbody>\n</table>\n')
        self.in_docinfo = None
        start = self.context.pop()
        self.body_pre_docinfo = self.body[:start]
        self.docinfo = self.body[start:]
        self.body = []

    def visit_docinfo_item(self, node, name, meta=1):
        if meta:
            self.head.append('<meta name="%s" content="%s" />\n'
                             % (name, self.attval(node.astext())))
        self.body.append(self.starttag(node, 'tr', ''))
        self.body.append('<th class="docinfo-name">%s:</th>\n<td>'
                         % self.language.labels[name])
        if len(node):
            if isinstance(node[0], nodes.Element):
                node[0].set_class('first')
            if isinstance(node[0], nodes.Element):
                node[-1].set_class('last')

    def depart_docinfo_item(self):
        self.body.append('</td></tr>\n')

    def visit_doctest_block(self, node):
        self.body.append(self.starttag(node, 'pre', CLASS='doctest-block'))

    def depart_doctest_block(self, node):
        self.body.append('\n</pre>\n')

    def visit_document(self, node):
        self.body.append(self.starttag(node, 'div', CLASS='document'))

    def depart_document(self, node):
        self.body.append('</div>\n')

    def visit_emphasis(self, node):
        self.body.append('<em>')

    def depart_emphasis(self, node):
        self.body.append('</em>')

    def visit_entry(self, node):
        if isinstance(node.parent.parent, nodes.thead):
            tagname = 'th'
        else:
            tagname = 'td'
        atts = {}
        if node.has_key('morerows'):
            atts['rowspan'] = node['morerows'] + 1
        if node.has_key('morecols'):
            atts['colspan'] = node['morecols'] + 1
        self.body.append(self.starttag(node, tagname, '', **atts))
        self.context.append('</%s>\n' % tagname.lower())
        if len(node) == 0:              # empty cell
            self.body.append('&nbsp;')
        else:
            node[0].set_class('first')
            node[-1].set_class('last')

    def depart_entry(self, node):
        self.body.append(self.context.pop())

    def visit_enumerated_list(self, node):
        """
        The 'start' attribute does not conform to HTML 4.01's strict.dtd, but
        CSS1 doesn't help. CSS2 isn't widely enough supported yet to be
        usable.
        """
        atts = {}
        if node.has_key('start'):
            atts['start'] = node['start']
        if node.has_key('enumtype'):
            atts['class'] = node['enumtype']
        # @@@ To do: prefix, suffix. How? Change prefix/suffix to a
        # single "format" attribute? Use CSS2?
        old_compact_simple = self.compact_simple
        self.context.append((self.compact_simple, self.compact_p))
        self.compact_p = None
        self.compact_simple = (self.settings.compact_lists and
                               (self.compact_simple
                                or self.topic_class == 'contents'
                                or self.check_simple_list(node)))
        if self.compact_simple and not old_compact_simple:
            atts['class'] = (atts.get('class', '') + ' simple').strip()
        self.body.append(self.starttag(node, 'ol', **atts))

    def depart_enumerated_list(self, node):
        self.compact_simple, self.compact_p = self.context.pop()
        self.body.append('</ol>\n')

    def visit_error(self, node):
        self.visit_admonition(node, 'error')

    def depart_error(self, node):
        self.depart_admonition()

    def visit_field(self, node):
        self.body.append(self.starttag(node, 'tr', '', CLASS='field'))

    def depart_field(self, node):
        self.body.append('</tr>\n')

    def visit_field_body(self, node):
        self.body.append(self.starttag(node, 'td', '', CLASS='field-body'))
        if len(node):
            node[0].set_class('first')
            node[-1].set_class('last')

    def depart_field_body(self, node):
        self.body.append('</td>\n')

    def visit_field_list(self, node):
        self.body.append(self.starttag(node, 'table', frame='void',
                                       rules='none', CLASS='field-list'))
        self.body.append('<col class="field-name" />\n'
                         '<col class="field-body" />\n'
                         '<tbody valign="top">\n')

    def depart_field_list(self, node):
        self.body.append('</tbody>\n</table>\n')

    def visit_field_name(self, node):
        atts = {}
        if self.in_docinfo:
            atts['class'] = 'docinfo-name'
        else:
            atts['class'] = 'field-name'
        if len(node.astext()) > 14:
            atts['colspan'] = 2
            self.context.append('</tr>\n<tr><td>&nbsp;</td>')
        else:
            self.context.append('')
        self.body.append(self.starttag(node, 'th', '', **atts))

    def depart_field_name(self, node):
        self.body.append(':</th>')
        self.body.append(self.context.pop())

    def visit_figure(self, node):
        self.body.append(self.starttag(node, 'div', CLASS='figure'))

    def depart_figure(self, node):
        self.body.append('</div>\n')

    def visit_footer(self, node):
        self.context.append(len(self.body))

    def depart_footer(self, node):
        start = self.context.pop()
        footer = (['<hr class="footer"/>\n',
                   self.starttag(node, 'div', CLASS='footer')]
                  + self.body[start:] + ['</div>\n'])
        self.body_suffix[:0] = footer
        del self.body[start:]

    def visit_footnote(self, node):
        self.body.append(self.starttag(node, 'table', CLASS='footnote',
                                       frame="void", rules="none"))
        self.body.append('<colgroup><col class="label" /><col /></colgroup>\n'
                         '<tbody valign="top">\n'
                         '<tr>')
        self.footnote_backrefs(node)

    def footnote_backrefs(self, node):
        if self.settings.footnote_backlinks and node.hasattr('backrefs'):
            backrefs = node['backrefs']
            if len(backrefs) == 1:
                self.context.append('')
                self.context.append('<a class="fn-backref" href="#%s" '
                                    'name="%s">' % (backrefs[0], node['id']))
            else:
                i = 1
                backlinks = []
                for backref in backrefs:
                    backlinks.append('<a class="fn-backref" href="#%s">%s</a>'
                                     % (backref, i))
                    i += 1
                self.context.append('<em>(%s)</em> ' % ', '.join(backlinks))
                self.context.append('<a name="%s">' % node['id'])
        else:
            self.context.append('')
            self.context.append('<a name="%s">' % node['id'])

    def depart_footnote(self, node):
        self.body.append('</td></tr>\n'
                         '</tbody>\n</table>\n')

    def visit_footnote_reference(self, node):
        href = ''
        if node.has_key('refid'):
            href = '#' + node['refid']
        elif node.has_key('refname'):
            href = '#' + self.document.nameids[node['refname']]
        format = self.settings.footnote_references
        if format == 'brackets':
            suffix = '['
            self.context.append(']')
        elif format == 'superscript':
            suffix = '<sup>'
            self.context.append('</sup>')
        else:                           # shouldn't happen
            suffix = '???'
            self.content.append('???')
        self.body.append(self.starttag(node, 'a', suffix, href=href,
                                       CLASS='footnote-reference'))

    def depart_footnote_reference(self, node):
        self.body.append(self.context.pop() + '</a>')

    def visit_generated(self, node):
        pass

    def depart_generated(self, node):
        pass

    def visit_header(self, node):
        self.context.append(len(self.body))

    def depart_header(self, node):
        start = self.context.pop()
        self.body_prefix.append(self.starttag(node, 'div', CLASS='header'))
        self.body_prefix.extend(self.body[start:])
        self.body_prefix.append('<hr />\n</div>\n')
        del self.body[start:]

    def visit_hint(self, node):
        self.visit_admonition(node, 'hint')

    def depart_hint(self, node):
        self.depart_admonition()

    def visit_image(self, node):
        atts = node.attributes.copy()
        atts['src'] = atts['uri']
        del atts['uri']
        if not atts.has_key('alt'):
            atts['alt'] = atts['src']
        if isinstance(node.parent, nodes.TextElement):
            self.context.append('')
        else:
            self.body.append('<p>')
            self.context.append('</p>\n')
        self.body.append(self.emptytag(node, 'img', '', **atts))

    def depart_image(self, node):
        self.body.append(self.context.pop())

    def visit_important(self, node):
        self.visit_admonition(node, 'important')

    def depart_important(self, node):
        self.depart_admonition()

    def visit_interpreted(self, node):
        # @@@ Incomplete, pending a proper implementation on the
        # Parser/Reader end.
        self.body.append('<span class="interpreted">')

    def depart_interpreted(self, node):
        self.body.append('</span>')

    def visit_label(self, node):
        self.body.append(self.starttag(node, 'td', '%s[' % self.context.pop(),
                                       CLASS='label'))

    def depart_label(self, node):
        self.body.append(']</a></td><td>%s' % self.context.pop())

    def visit_legend(self, node):
        self.body.append(self.starttag(node, 'div', CLASS='legend'))

    def depart_legend(self, node):
        self.body.append('</div>\n')

    def visit_line_block(self, node):
        self.body.append(self.starttag(node, 'pre', CLASS='line-block'))

    def depart_line_block(self, node):
        self.body.append('\n</pre>\n')

    def visit_list_item(self, node):
        self.body.append(self.starttag(node, 'li', ''))
        if len(node):
            node[0].set_class('first')

    def depart_list_item(self, node):
        self.body.append('</li>\n')

    def visit_literal(self, node):
        """Process text to prevent tokens from wrapping."""
        self.body.append(self.starttag(node, 'tt', '', CLASS='literal'))
        text = node.astext()
        for token in self.words_and_spaces.findall(text):
            if token.strip():
                # Protect text like "--an-option" from bad line wrapping:
                self.body.append('<span class="pre">%s</span>'
                                 % self.encode(token))
            elif token in ('\n', ' '):
                # Allow breaks at whitespace:
                self.body.append(token)
            else:
                # Protect runs of multiple spaces; the last space can wrap:
                self.body.append('&nbsp;' * (len(token) - 1) + ' ')
        self.body.append('</tt>')
        # Content already processed:
        raise nodes.SkipNode

    def visit_literal_block(self, node):
        self.body.append(self.starttag(node, 'pre', CLASS='literal-block'))

    def depart_literal_block(self, node):
        self.body.append('\n</pre>\n')

    def visit_meta(self, node):
        self.head.append(self.starttag(node, 'meta', **node.attributes))

    def depart_meta(self, node):
        pass

    def visit_note(self, node):
        self.visit_admonition(node, 'note')

    def depart_note(self, node):
        self.depart_admonition()

    def visit_option(self, node):
        if self.context[-1]:
            self.body.append(', ')

    def depart_option(self, node):
        self.context[-1] += 1

    def visit_option_argument(self, node):
        self.body.append(node.get('delimiter', ' '))
        self.body.append(self.starttag(node, 'var', ''))

    def depart_option_argument(self, node):
        self.body.append('</var>')

    def visit_option_group(self, node):
        atts = {}
        if len(node.astext()) > 14:
            atts['colspan'] = 2
            self.context.append('</tr>\n<tr><td>&nbsp;</td>')
        else:
            self.context.append('')
        self.body.append(self.starttag(node, 'td', **atts))
        self.body.append('<kbd>')
        self.context.append(0)          # count number of options

    def depart_option_group(self, node):
        self.context.pop()
        self.body.append('</kbd></td>\n')
        self.body.append(self.context.pop())

    def visit_option_list(self, node):
        self.body.append(
              self.starttag(node, 'table', CLASS='option-list',
                            frame="void", rules="none"))
        self.body.append('<col class="option" />\n'
                         '<col class="description" />\n'
                         '<tbody valign="top">\n')

    def depart_option_list(self, node):
        self.body.append('</tbody>\n</table>\n')

    def visit_option_list_item(self, node):
        self.body.append(self.starttag(node, 'tr', ''))

    def depart_option_list_item(self, node):
        self.body.append('</tr>\n')

    def visit_option_string(self, node):
        self.body.append(self.starttag(node, 'span', '', CLASS='option'))

    def depart_option_string(self, node):
        self.body.append('</span>')

    def visit_organization(self, node):
        self.visit_docinfo_item(node, 'organization')

    def depart_organization(self, node):
        self.depart_docinfo_item()

    def visit_paragraph(self, node):
        # Omit <p> tags if this is an only child and optimizable.
        if (self.compact_simple or
            self.compact_p and (len(node.parent) == 1 or
                                len(node.parent) == 2 and
                                isinstance(node.parent[0], nodes.label))):
            self.context.append('')
        else:
            self.body.append(self.starttag(node, 'p', ''))
            self.context.append('</p>\n')

    def depart_paragraph(self, node):
        self.body.append(self.context.pop())

    def visit_problematic(self, node):
        if node.hasattr('refid'):
            self.body.append('<a href="#%s" name="%s">' % (node['refid'],
                                                           node['id']))
            self.context.append('</a>')
        else:
            self.context.append('')
        self.body.append(self.starttag(node, 'span', '', CLASS='problematic'))

    def depart_problematic(self, node):
        self.body.append('</span>')
        self.body.append(self.context.pop())

    def visit_raw(self, node):
        if node.get('format') == 'html':
            self.body.append(node.astext())
        # Keep non-HTML raw text out of output:
        raise nodes.SkipNode

    def visit_reference(self, node):
        if node.has_key('refuri'):
            href = node['refuri']
        elif node.has_key('refid'):
            href = '#' + node['refid']
        elif node.has_key('refname'):
            href = '#' + self.document.nameids[node['refname']]
        self.body.append(self.starttag(node, 'a', '', href=href,
                                       CLASS='reference'))

    def depart_reference(self, node):
        self.body.append('</a>')

    def visit_revision(self, node):
        self.visit_docinfo_item(node, 'revision', meta=None)

    def depart_revision(self, node):
        self.depart_docinfo_item()

    def visit_row(self, node):
        self.body.append(self.starttag(node, 'tr', ''))

    def depart_row(self, node):
        self.body.append('</tr>\n')

    def visit_section(self, node):
        self.section_level += 1
        self.body.append(self.starttag(node, 'div', CLASS='section'))

    def depart_section(self, node):
        self.section_level -= 1
        self.body.append('</div>\n')

    def visit_status(self, node):
        self.visit_docinfo_item(node, 'status', meta=None)

    def depart_status(self, node):
        self.depart_docinfo_item()

    def visit_strong(self, node):
        self.body.append('<strong>')

    def depart_strong(self, node):
        self.body.append('</strong>')

    def visit_substitution_definition(self, node):
        """Internal only."""
        raise nodes.SkipNode

    def visit_substitution_reference(self, node):
        self.unimplemented_visit(node)

    def visit_subtitle(self, node):
        self.body.append(self.starttag(node, 'h2', '', CLASS='subtitle'))

    def depart_subtitle(self, node):
        self.body.append('</h2>\n')

    def visit_system_message(self, node):
        if node['level'] < self.document.reporter['writer'].report_level:
            # Level is too low to display:
            raise nodes.SkipNode
        self.body.append(self.starttag(node, 'div', CLASS='system-message'))
        self.body.append('<p class="system-message-title">')
        attr = {}
        backref_text = ''
        if node.hasattr('id'):
            attr['name'] = node['id']
        if node.hasattr('backrefs'):
            backrefs = node['backrefs']
            if len(backrefs) == 1:
                backref_text = ('; <em><a href="#%s">backlink</a></em>'
                                % backrefs[0])
            else:
                i = 1
                backlinks = []
                for backref in backrefs:
                    backlinks.append('<a href="#%s">%s</a>' % (backref, i))
                    i += 1
                backref_text = ('; <em>backlinks: %s</em>'
                                % ', '.join(backlinks))
        if node.hasattr('line'):
            line = ', line %s' % node['line']
        else:
            line = ''
        if attr:
            a_start = self.starttag({}, 'a', '', **attr)
            a_end = '</a>'
        else:
            a_start = a_end = ''
        self.body.append('System Message: %s%s/%s%s (<tt>%s</tt>%s)%s</p>\n'
                         % (a_start, node['type'], node['level'], a_end,
                            node['source'], line, backref_text))

    def depart_system_message(self, node):
        self.body.append('</div>\n')

    def visit_table(self, node):
        self.body.append(
              self.starttag(node, 'table', CLASS="table",
                            frame='border', rules='all'))

    def depart_table(self, node):
        self.body.append('</table>\n')

    def visit_target(self, node):
        if not (node.has_key('refuri') or node.has_key('refid')
                or node.has_key('refname')):
            self.body.append(self.starttag(node, 'a', '', CLASS='target'))
            self.context.append('</a>')
        else:
            self.context.append('')

    def depart_target(self, node):
        self.body.append(self.context.pop())

    def visit_tbody(self, node):
        self.write_colspecs()
        self.body.append(self.context.pop()) # '</colgroup>\n' or ''
        self.body.append(self.starttag(node, 'tbody', valign='top'))

    def depart_tbody(self, node):
        self.body.append('</tbody>\n')

    def visit_term(self, node):
        self.body.append(self.starttag(node, 'dt', ''))

    def depart_term(self, node):
        """
        Leave the end tag to `self.visit_definition()`, in case there's a
        classifier.
        """
        pass

    def visit_tgroup(self, node):
        # Mozilla needs <colgroup>:
        self.body.append(self.starttag(node, 'colgroup'))
        # Appended by thead or tbody:
        self.context.append('</colgroup>\n')

    def depart_tgroup(self, node):
        pass

    def visit_thead(self, node):
        self.write_colspecs()
        self.body.append(self.context.pop()) # '</colgroup>\n'
        # There may or may not be a <thead>; this is for <tbody> to use:
        self.context.append('')
        self.body.append(self.starttag(node, 'thead', valign='bottom'))

    def depart_thead(self, node):
        self.body.append('</thead>\n')

    def visit_tip(self, node):
        self.visit_admonition(node, 'tip')

    def depart_tip(self, node):
        self.depart_admonition()

    def visit_title(self, node):
        """Only 6 section levels are supported by HTML."""
        if isinstance(node.parent, nodes.topic):
            self.body.append(
                  self.starttag(node, 'p', '', CLASS='topic-title'))
            if node.parent.hasattr('id'):
                self.body.append(
                    self.starttag({}, 'a', '', name=node.parent['id']))
                self.context.append('</a></p>\n')
            else:
                self.context.append('</p>\n')
        elif self.section_level == 0:
            # document title
            self.head.append('<title>%s</title>\n'
                             % self.encode(node.astext()))
            self.body.append(self.starttag(node, 'h1', '', CLASS='title'))
            self.context.append('</h1>\n')
        else:
            self.body.append(
                  self.starttag(node, 'h%s' % self.section_level, ''))
            atts = {}
            if node.parent.hasattr('id'):
                atts['name'] = node.parent['id']
            if node.hasattr('refid'):
                atts['class'] = 'toc-backref'
                atts['href'] = '#' + node['refid']
            self.body.append(self.starttag({}, 'a', '', **atts))
            self.context.append('</a></h%s>\n' % (self.section_level))

    def depart_title(self, node):
        self.body.append(self.context.pop())

    def visit_topic(self, node):
        self.body.append(self.starttag(node, 'div', CLASS='topic'))
        self.topic_class = node.get('class')

    def depart_topic(self, node):
        self.body.append('</div>\n')
        self.topic_class = ''

    def visit_transition(self, node):
        self.body.append(self.emptytag(node, 'hr'))

    def depart_transition(self, node):
        pass

    def visit_version(self, node):
        self.visit_docinfo_item(node, 'version', meta=None)

    def depart_version(self, node):
        self.depart_docinfo_item()

    def visit_warning(self, node):
        self.visit_admonition(node, 'warning')

    def depart_warning(self, node):
        self.depart_admonition()

    def unimplemented_visit(self, node):
        raise NotImplementedError('visiting unimplemented node type: %s'
                                  % node.__class__.__name__)


class SimpleListChecker(nodes.GenericNodeVisitor):

    """
    Raise `nodes.SkipNode` if non-simple list item is encountered.

    Here "simple" means a list item containing nothing other than a single
    paragraph, a simple list, or a paragraph followed by a simple list.
    """

    def default_visit(self, node):
        raise nodes.NodeFound

    def visit_bullet_list(self, node):
        pass

    def visit_enumerated_list(self, node):
        pass

    def visit_list_item(self, node):
        children = []
        for child in node.get_children():
            if not isinstance(child, nodes.Invisible):
                children.append(child)
        if (children and isinstance(children[0], nodes.paragraph)
            and (isinstance(children[-1], nodes.bullet_list)
                 or isinstance(children[-1], nodes.enumerated_list))):
            children.pop()
        if len(children) <= 1:
            return
        else:
            raise nodes.NodeFound

    def visit_paragraph(self, node):
        raise nodes.SkipNode

    def invisible_visit(self, node):
        """Invisible nodes should be ignored."""
        pass

    visit_comment = invisible_visit
    visit_substitution_definition = invisible_visit
    visit_target = invisible_visit
    visit_pending = invisible_visit
