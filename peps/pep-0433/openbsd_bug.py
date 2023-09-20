# Script testing an OpenBSD bug
#
# The script fails with "OS BUG!!!" with OpenBSD older than 5.2.
# It works on any version using USE_FORK = False.
USE_FORK = True

import fcntl, os, sys

fd = os.open("/etc/passwd", os.O_RDONLY)
flags = fcntl.fcntl(fd, fcntl.F_GETFD)
flags |= fcntl.FD_CLOEXEC
fcntl.fcntl(fd, fcntl.F_SETFD, flags)

code = """
import os, sys
fd = int(sys.argv[1])
try:
    os.fstat(fd)
except OSError:
    print("fd %s closed by exec (FD_CLOEXEC works)" % fd)
else:
    print("fd %s not closed by exec: FD_CLOEXEC doesn't work, OS BUG!!!" % fd)
"""

args = [sys.executable, '-c', code, str(fd)]
if USE_FORK:
    pid = os.fork()
    if pid:
        os.waitpid(pid, 0)
        sys.exit(0)

os.execv(args[0], args)
