#!/usr/bin/env python
"""
convert PEP's to (X)HTML - courtesy of /F

Syntax: pep2html [sf_username]

The user name 'sf_username' is used to upload the converted files
to the web pages at source forge.
"""

import cgi, glob, os, re, sys

# this doesn't validate -- you cannot use <hr> and <h3> inside <pre>
# tags.  but if I change that, the result doesn't look very nice...

DTD = ('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" '
       '"http://www.w3.org/TR/REC-html40/loose.dtd">')

fixpat = re.compile("((http|ftp):[-_a-zA-Z0-9/.+~:?#$=&]+)|(pep-\d+(.txt)?)|.")

def fixanchor(match):
    text = match.group(0)
    link = None
    if text[:5] == "http:" or text[:4] == "ftp:":
        link = text
    elif text[:3] == "pep":
        link = os.path.splitext(text)[0] + ".html"
    if link:
        return "<a href='%s'>%s</a>" % (link, cgi.escape(link))
    return cgi.escape(match.group(0)) # really slow, but it works...

def fixfile(infile, outfile):
    # convert plain text pep to minimal XHTML markup
    fi = open(infile)
    fo = open(outfile, "w")
    fo.write("%s\n<html>\n" % DTD)
    # head
    header = []
    fo.write("<head>\n")
    pep = ""
    title = ""
    while 1:
        line = fi.readline()
        if not line or ":" not in line:
            break
        key, value = line.split(":", 1)
        value = value.strip()
        header.append((key, value))
        if key.lower() == "title":
            title = value
        if key.lower() == "pep":
            pep = value
    if pep:
        title = "PEP " + pep + " -- " + title
    if title:
        fo.write("<title>%s</title>\n" % cgi.escape(title))
    fo.write("</head>\n")
    # body
    fo.write("<body bgcolor='white'>\n")
    fo.write("<pre>\n")
    fo.write("[<a href='..'>home</a>]")
    if os.path.basename(file) != "pep-0000.txt":
        fo.write(" [<a href='.'>index</a>]")
    fo.write("\n<hr />\n")
    # fo.write("\n</pre><hr /><pre>\n")
    for k, v in header:
        fo.write("<b>%s:</b> %s\n" % (cgi.escape(k), cgi.escape(v)))
    title = 0
    while 1:
        line = fi.readline()
        if not line:
            break
        if line[:1] == "\f":
            fo.write("\n<hr />\n")
            # fo.write("\n</pre><hr /><pre>\n")
            title = 1
        elif title >= 0:
            line = fixpat.sub(fixanchor, line)
            if title:
                if line.strip() == "Local Variables:":
                    title = -1
                else:
                    fo.write("<h3><tt>%s</tt></h3>\n" % line)
                    # fo.write("</pre><h3><tt>%s</tt></h3><pre>\n" % line)
                    title = 0
            else:
                fo.write(line)
    fo.write("</pre>\n")
    fo.write("</body>\n")
    fo.write("</html>\n")

for file in glob.glob("pep-*.txt"):
    print file, "..."
    fixfile(file, os.path.splitext(file)[0] + ".html")

if len(sys.argv) == 1:
    username = ""
elif len(sys.argv) == 2:
    username = sys.argv[1]+"@"
else:
    raise "Syntax: "+sys.argv[0]+" [sf_username]"
    
os.system("scp pep-*.html "+username+"shell.sourceforge.net:/home/groups/python/htdocs/peps")
