#!/usr/bin/env python
"""
convert PEP's to (X)HTML - courtesy of /F

Usage: %(PROGRAM)s [options] [peps]

Notes:

    The optional argument peps can be either pep numbers or .txt files.

Options:

    -u/--user
        SF username

    -i/--install
        After generating the HTML, install it SourceForge.  In that case the
        user's name is used in the scp and ssh commands, unless sf_username is
        given (in which case, it is used instead).  Without -i, sf_username is
        ignored.

    -h/--help
        Print this help message and exit.
"""

import sys
import os
import re
import cgi
import glob
import getopt

PROGRAM = sys.argv[0]



HOST = "shell.sourceforge.net"                    # host for update
HDIR = "/home/groups/python/htdocs/peps"          # target host directory
LOCALVARS = "Local Variables:"

# The generated HTML doesn't validate -- you cannot use <hr> and <h3> inside
# <pre> tags.  But if I change that, the result doesn't look very nice...
DTD = ('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN"\n'
       '                      "http://www.w3.org/TR/REC-html40/loose.dtd">')

fixpat = re.compile("((http|ftp):[-_a-zA-Z0-9/.+~:?#$=&]+)|(pep-\d+(.txt)?)|.")



def usage(code, msg=''):
    sys.stderr.write(__doc__ % globals() + '\n')
    if msg:
        msg = str(msg)
        if msg[-1] <> '\n':
            msg = msg + '\n'
        sys.stderr.write(msg)
    sys.exit(code)



def fixanchor(current, match):
    text = match.group(0)
    link = None
    if text[:5] == "http:" or text[:4] == "ftp:":
        link = text
    elif text[:4] == "pep-" and text != current:
        link = os.path.splitext(text)[0] + ".html"
    if link:
        return "<a href='%s'>%s</a>" % (link, cgi.escape(text))
    return cgi.escape(match.group(0)) # really slow, but it works...



def fixfile(infile, outfile):
    # convert plain text pep to minimal XHTML markup
    fi = open(infile)
    fo = open(outfile, "w")
    fo.write(DTD + "\n<html>\n<head>\n")
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
        fo.write("  <title>%s</title>\n"
                 '  <link rel="STYLESHEET" href="style.css">\n'
                 % cgi.escape(title))
    fo.write("</head>\n")
    # body
    fo.write('<body bgcolor="white">\n'
             '<div class="navigation">\n')
    fo.write('[<b><a href="../">home</a></b>]\n')
    if os.path.basename(infile) != "pep-0000.txt":
        fo.write('[<b><a href=".">index</a></b>]\n')
    fo.write('</div>\n'
             '<div class="header">\n<table border="0">\n')
    for k, v in header:
        if k.lower() == 'author':
            mailtos = []
            for addr in v.split():
                if '@' in addr:
                    mailtos.append(
                        '<a href="mailto:%s?subject=PEP%%20%s">%s</a>' %
                        (addr, pep, addr))
                else:
                    mailtos.append(addr)
            v = ' '.join(mailtos)
        else:
            v = cgi.escape(v)
        fo.write("  <tr><th align='right'>%s:</th><td>%s</td></tr>\n"
                 % (cgi.escape(k), v))
    title = 0
    fo.write("</table>\n</div>\n<hr />\n"
             "<pre>")
    while 1:
        line = fi.readline()
        if not line:
            break
        if line[0] != "\f":
            if line[0].strip():
                if line.strip() == LOCALVARS:
                    break
                fo.write("</pre>\n<h3>%s</h3>\n<pre>" % line.strip())
                title = 0
            else:
                line = fixpat.sub(lambda x, c=infile: fixanchor(c, x), line)
                fo.write(line)
    fo.write("</pre>\n"
             "</body>\n"
             "</html>\n")
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

def push_html(files, username, verbose):
    if verbose:
        quiet = ""
    else:
        quiet = "-q"
    if username:
        username = username + "@"
    target = username + HOST + ":" + HDIR
    files.append("style.css")
    filelist = " ".join(files)
    rc = os.system("scp %s %s %s" % (quiet, filelist, target))
    if rc:
        sys.exit(rc)
    rc = os.system("ssh %s%s chmod 664 %s/*" % (username, HOST, HDIR))
    if rc:
        sys.exit(rc)


def main():
    # defaults
    update = 0
    username = ''
    verbose = 1

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'ihq',
                                   ['install', 'help', 'quiet'])
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

    if args:
        html = []
        for pep in args:
            file = find_pep(pep)
            newfile = make_html(file, verbose=verbose)
            html.append(newfile)
    else:
        # do them all
        for file in glob.glob("pep-*.txt"):
            make_html(file, verbose=verbose)
        html = ["pep-*.html"]
    if update:
        push_html(html, username, verbose)


if __name__ == "__main__":
    main()
