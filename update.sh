#! /bin/sh

# This script is meant to be run by cron regularly on the
# www.python.org server to avoid letting the online PEPs get stale.
# Before using it, the user whose account it is run under needs to use
# the "cvs login" command to log into the Python CVS server as
# anonymous.

TMPDIR="$HOME/tmp"
WORKDIR="peps-$$"

TARGETDIR='/ftp/ftp.python.org/pub/www.python.org/peps'

CVSROOT=':pserver:anonymous@cvs.python.sourceforge.net:/cvsroot/python'
export CVSROOT

cd "$TMPDIR" || exit $?
cvs -Q checkout -d "$WORKDIR" python/nondist/peps || exit $?

cd "$WORKDIR" || exit $?
python ./pep2html.py -q || exit $?

# This loop avoids modifying the files for an unchanged PEP.
# The HTML file is treated a little strangely since it contains the
# (pseudo-)random selection of the corner logo.

for FILE in *.txt ; do
    HTML="${FILE%txt}html"
    if [ -e "$TARGETDIR/$FILE" ] ; then
        if cmp -s "$FILE" "$TARGETDIR/$FILE" ; then
            true
        else
            cp "$FILE" "$TARGETDIR/" || exit $?
            cp "$HTML" "$TARGETDIR/" || exit $?
        fi
    else
        cp "$HTML" "$TARGETDIR/" || exit $?
    fi
done

cd "$TMPDIR" || exit $?
rm -r "$WORKDIR" || exit $?
