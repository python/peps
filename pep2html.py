#!/usr/bin/env python
"""
convert PEP's to (X)HTML - courtesy of /F

Usage: %(PROGRAM)s [options] [peps]

Options:

    -u/--user
        SF username

    -b/--browse
        After generating the HTML, direct your web browser to view it
        (using the Python webbrowser module).  If both -i and -b are
        given, this will browse the on-line HTML; otherwise it will
        browse the local HTML.  If no pep arguments are given, this
        will browse PEP 0.

    -i/--install
        After generating the HTML, install it and the plain text source file
        (.txt) SourceForge.  In that case the user's name is used in the scp
        and ssh commands, unless -u sf_username is given (in which case, it is
        used instead).  Without -i, -u is ignored.

    -q/--quiet
        Turn off verbose messages.

    -h/--help
        Print this help message and exit.

The optional argument `peps' is a list of either pep numbers or .txt files.
"""

import sys
import os
import re
import cgi
import glob
import getopt
import errno
import random
import time

PROGRAM = sys.argv[0]
RFCURL = 'http://www.faqs.org/rfcs/rfc%d.html'
PEPURL = 'pep-%04d.html'
PEPCVSURL = 'http://cvs.sourceforge.net/cgi-bin/viewcvs.cgi/python/python/nondist/peps/pep-%04d.txt'
PEPDIRRUL = 'http://www.python.org/peps/'


HOST = "www.python.org"                    # host for update
HDIR = "/ftp/ftp.python.org/pub/www.python.org/peps" # target host directory
LOCALVARS = "Local Variables:"

# The generated HTML doesn't validate -- you cannot use <hr> and <h3> inside
# <pre> tags.  But if I change that, the result doesn't look very nice...
DTD = ('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN"\n'
       '                      "http://www.w3.org/TR/REC-html40/loose.dtd">')

fixpat = re.compile("((http|ftp):[-_a-zA-Z0-9/.+~:?#$=&,]+)|(pep-\d+(.txt)?)|"
                    "(RFC[- ]?(?P<rfcnum>\d+))|"
                    "(PEP\s+(?P<pepnum>\d+))|"
                    ".")

EMPTYSTRING = ''
SPACE = ' '



def usage(code, msg=''):
    print >> sys.stderr, __doc__ % globals()
    if msg:
        print >> sys.stderr, msg
    sys.exit(code)



def fixanchor(current, match):
    text = match.group(0)
    link = None
    if text.startswith('http:') or text.startswith('ftp:'):
        # Strip off trailing punctuation.  Pattern taken from faqwiz.
        ltext = list(text)
        while ltext:
            c = ltext.pop()
            if c not in '();:,.?\'"<>':
                ltext.append(c)
                break
        link = EMPTYSTRING.join(ltext)
    elif text.startswith('pep-') and text <> current:
        link = os.path.splitext(text)[0] + ".html"
    elif text.startswith('PEP'):
        pepnum = int(match.group('pepnum'))
        link = PEPURL % pepnum
    elif text.startswith('RFC'):
        rfcnum = int(match.group('rfcnum'))
        link = RFCURL % rfcnum
    if link:
        return '<a href="%s">%s</a>' % (link, cgi.escape(text))
    return cgi.escape(match.group(0)) # really slow, but it works...



NON_MASKED_EMAILS = [
    'peps@python.org',
    'python-list@python.org',
    'python-dev@python.org',
    ]

def fixemail(address, pepno):
    if address.lower() in NON_MASKED_EMAILS:
        # return hyperlinked version of email address
        return linkemail(address, pepno)
    else:
        # return masked version of email address
        parts = address.split('@', 1)
        return '%s&#32;&#97;t&#32;%s' % (parts[0], parts[1])


def linkemail(address, pepno):
    parts = address.split('@', 1)
    return ('<a href="mailto:%s&#64;%s?subject=PEP%%20%s">'
            '%s&#32;&#97;t&#32;%s</a>'
            % (parts[0], parts[1], pepno, parts[0], parts[1]))


def fixfile(infile, outfile):
    basename = os.path.basename(infile)
    # convert plain text pep to minimal XHTML markup
    try:
        fi = open(infile)
    except IOError, e:
        if e.errno <> errno.ENOENT: raise
        print >> sys.stderr, 'Error: Skipping missing PEP file:', e.filename
        return
    fo = open(outfile, "w")
    print >> fo, DTD
    print >> fo, '<html>'
    print >> fo, '<head>'
    # head
    header = []
    pep = ""
    title = ""
    while 1:
        line = fi.readline()
        if not line.strip():
            break
        if line[0].strip():
            if ":" not in line:
                break
            key, value = line.split(":", 1)
            value = value.strip()
            header.append((key, value))
        else:
            # continuation line
            key, value = header[-1]
            value = value + line
            header[-1] = key, value
        if key.lower() == "title":
            title = value
        elif key.lower() == "pep":
            pep = value
    if pep:
        title = "PEP " + pep + " -- " + title
    if title:
        print >> fo, '  <title>%s</title>' % cgi.escape(title)
    print >> fo, '  <link rel="STYLESHEET" href="style.css" type="text/css">'
    print >> fo, '</head>'
    # body
    print >> fo, '<body bgcolor="white" marginwidth="0" marginheight="0">'
    print >> fo, '<table class="navigation" cellpadding="0" cellspacing="0"'
    print >> fo, '       width="100%" border="0">'
    print >> fo, '<tr><td class="navicon" width="150" height="35">'
    r = random.choice(range(64))
    print >> fo, '<a href="../" title="Python Home Page">'
    print >> fo, '<img src="../pics/PyBanner%03d.gif" alt="[Python]"' % r
    print >> fo, ' border="0" width="150" height="35" /></a></td>'
    print >> fo, '<td class="textlinks" align="left">'
    print >> fo, '[<b><a href="../">Python Home</a></b>]'
    if basename <> 'pep-0000.txt':
        print >> fo, '[<b><a href=".">PEP Index</a></b>]'
    if pep:
        print >> fo, '[<b><a href="pep-%04d.txt">PEP Source</a></b>]' \
              % int(pep)
    print >> fo, '</td></tr></table>'
    print >> fo, '<div class="header">\n<table border="0">'
    for k, v in header:
        if k.lower() in ('author', 'discussions-to'):
            mailtos = []
            for addr in v.split():
                if '@' in addr:
                    if k.lower() == 'discussions-to':
                        m = linkemail(addr, pep)
                    else:
                        m = fixemail(addr, pep)
                    mailtos.append(m)
                elif addr.startswith('http:'):
                    mailtos.append(
                        '<a href="%s">%s</a>' % (addr, addr))
                else:
                    mailtos.append(addr)
            v = SPACE.join(mailtos)
        elif k.lower() in ('replaces', 'replaced-by'):
            otherpeps = ''
            for otherpep in v.split():
                otherpep = int(otherpep)
                otherpeps += '<a href="pep-%04d.html">%i</a> ' % (otherpep, 
                                                                  otherpep)
            v = otherpeps
        elif k.lower() in ('last-modified',):
            url = PEPCVSURL % int(pep)
            date = v or time.strftime('%d-%b-%Y',
                                      time.localtime(os.stat(infile)[8]))
            v = '<a href="%s">%s</a> ' % (url, cgi.escape(date))
        else:
            v = cgi.escape(v)
        print >> fo, '  <tr><th>%s:&nbsp;</th><td>%s</td></tr>' \
              % (cgi.escape(k), v)
    print >> fo, '</table>'
    print >> fo, '</div>'
    print >> fo, '<hr />'
    print >> fo, '<div class="content">'
    need_pre = 1
    while 1:
        line = fi.readline()
        if not line:
            break
        if line[0] == '\f':
            continue
        if line.strip() == LOCALVARS:
            break
        if line[0].strip():
            if line.strip() == LOCALVARS:
                break
            if not need_pre:
                print >> fo, '</pre>'
            print >> fo, '<h3>%s</h3>' % line.strip()
            need_pre = 1
        elif not line.strip() and need_pre:
            continue
        else:
            # PEP 0 has some special treatment
            if basename == 'pep-0000.txt':
                parts = line.split()
                if len(parts) > 1 and re.match(r'\s*\d{1,4}', parts[1]):
                    # This is a PEP summary line, which we need to hyperlink
                    url = PEPURL % int(parts[1])
                    if need_pre:
                        print >> fo, '<pre>'
                        need_pre = 0
                    print >> fo, re.sub(
                        parts[1],
                        '<a href="%s">%s</a>' % (url, parts[1]),
                        line, 1),
                    continue
                elif parts and '@' in parts[-1]:
                    # This is a pep email address line, so filter it.
                    url = fixemail(parts[-1], pep)
                    if need_pre:
                        print >> fo, '<pre>'
                        need_pre = 0
                    print >> fo, re.sub(
                        parts[-1], url, line, 1),
                    continue
            line = fixpat.sub(lambda x, c=infile: fixanchor(c, x), line)
            if need_pre:
                print >> fo, '<pre>'
                need_pre = 0
            fo.write(line)
    if not need_pre:
        print >> fo, '</pre>'
    print >> fo, '</div>'
    print >> fo, '</body>'
    print >> fo, '</html>'
    fo.close()
    os.chmod(outfile, 0664)



def find_pep(pep_str):
    """Find the .txt file indicated by a cmd line argument"""
    if os.path.exists(pep_str):
        return pep_str
    num = int(pep_str)
    return "pep-%04d.txt" % num

def make_html(file, verbose=0):
    newfile = os.path.splitext(file)[0] + ".html"
    if verbose:
        print file, "->", newfile
    fixfile(file, newfile)
    return newfile

def push_pep(htmlfiles, txtfiles, username, verbose):
    if verbose:
        quiet = ""
    else:
        quiet = "-q"
    if username:
        username = username + "@"
    target = username + HOST + ":" + HDIR
    files = htmlfiles[:]
    files.extend(txtfiles)
    files.append("style.css")
    filelist = SPACE.join(files)
    rc = os.system("scp %s %s %s" % (quiet, filelist, target))
    if rc:
        sys.exit(rc)
    rc = os.system("ssh %s%s chmod 664 %s/*" % (username, HOST, HDIR))
    if rc:
        sys.exit(rc)


def browse_file(pep):
    import webbrowser
    file = find_pep(pep)
    if file.endswith(".txt"):
        file = file[:-3] + "html"
    file = os.path.abspath(file)
    url = "file:" + file
    webbrowser.open(url)

def browse_remote(pep):
    import webbrowser
    file = find_pep(pep)
    if file.endswith(".txt"):
        file = file[:-3] + "html"
    url = PEPDIRRUL + file
    webbrowser.open(url)


def main():
    # defaults
    update = 0
    username = ''
    verbose = 1
    browse = 0

    try:
        opts, args = getopt.getopt(
            sys.argv[1:], 'bihqu:',
            ['browse', 'install', 'help', 'quiet', 'user='])
    except getopt.error, msg:
        usage(1, msg)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(0)
        elif opt in ('-i', '--install'):
            update = 1
        elif opt in ('-u', '--user'):
            username = arg
        elif opt in ('-q', '--quiet'):
            verbose = 0
        elif opt in ('-b', '--browse'):
            browse = 1

    if args:
        peptxt = []
        html = []
        for pep in args:
            file = find_pep(pep)
            peptxt.append(file)
            newfile = make_html(file, verbose=verbose)
            html.append(newfile)
            if browse and not update:
                browse_file(pep)
    else:
        # do them all
        peptxt = []
        files = glob.glob("pep-*.txt")
        files.sort()
        for file in files:
            peptxt.append(file)
            make_html(file, verbose=verbose)
        html = ["pep-*.html"]
        if browse and not update:
            browse_file("0")

    if update:
        push_pep(html, peptxt, username, verbose)
        if browse:
            if args:
                for pep in args:
                    browse_remote(pep)
            else:
                browse_remote("0")



if __name__ == "__main__":
    main()
