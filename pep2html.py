#!/usr/bin/env python
"""
convert PEP's to (X)HTML - courtesy of /F

Syntax: pep2html [-n] [sf_username]

The user name 'sf_username' is used to upload the converted files
to the web pages at source forge.

If -n is given, the script doesn't actually try to install the
generated HTML at SourceForge.

"""

import cgi, glob, os, re, sys

# this doesn't validate -- you cannot use <hr> and <h3> inside <pre>
# tags.  but if I change that, the result doesn't look very nice...

DTD = ('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN"\n'
       '                      "http://www.w3.org/TR/REC-html40/loose.dtd">')

fixpat = re.compile("((http|ftp):[-_a-zA-Z0-9/.+~:?#$=&]+)|(pep-\d+(.txt)?)|.")

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
    fo.write("[<a href='../'>home</a>]\n")
    if os.path.basename(infile) != "pep-0000.txt":
        fo.write("[<a href='.'>index</a>]\n")
    fo.write("<hr />\n<table border='0'>\n")
    for k, v in header:
        fo.write("  <tr><th align='right'>%s:</th><td>%s</td></tr>\n"
                 % (cgi.escape(k), cgi.escape(v)))
    title = 0
    fo.write("</table>\n<pre>")
    while 1:
        line = fi.readline()
        if not line:
            break
        if line[:1] == "\f":
            fo.write("<hr />")
            # fo.write("\n</pre><hr /><pre>\n")
            title = 1
        else:
            line = fixpat.sub(lambda x, c=infile: fixanchor(c, x), line)
            if title:
                if line.strip() == "Local Variables:":
                    break
                fo.write("</pre>\n<h3>%s</h3>\n<pre>" % line.strip())
                # fo.write("</pre><h3><tt>%s</tt></h3><pre>\n" % line)
                title = 0
            else:
                fo.write(line)
    fo.write("</pre>\n")
    fo.write("</body>\n")
    fo.write("</html>\n")


def main():
    update = 1
    for file in glob.glob("pep-*.txt"):
        print file, "..."
        fixfile(file, os.path.splitext(file)[0] + ".html")

    if len(sys.argv) > 1 and sys.argv[1] == "-n":
        update = 0
        del sys.argv[1]

    if len(sys.argv) == 1:
        username = ""
    elif len(sys.argv) == 2:
        username = sys.argv[1]+"@"
    else:
        raise "Syntax: "+sys.argv[0]+" [-n] [sf_username]"

    if update:
        os.system("scp pep-*.html " + username
                  + "shell.sourceforge.net:/home/groups/python/htdocs/peps")


if __name__ == "__main__":
    main()
