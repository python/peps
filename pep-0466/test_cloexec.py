import os, fcntl, sys, errno

def get_cloexec(fd):
    try:
        flags = fcntl.fcntl(fd, fcntl.F_GETFD)
        return bool(flags & fcntl.FD_CLOEXEC)
    except IOError as err:
        if err.errno == errno.EBADF:
            return '<invalid file descriptor>'
        else:
            return str(err)

def set_cloexec(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFD)
    flags |= fcntl.FD_CLOEXEC
    fcntl.fcntl(fd, fcntl.F_SETFD, flags)

def main():
    f = open(__file__, "rb")
    fd = f.fileno()
    print("initial state: fd=%s, cloexec=%s" % (fd, get_cloexec(fd)))


    pid = os.fork()
    if not pid:
        set_cloexec(fd)
        print("child process after fork, set cloexec: cloexec=%s" % get_cloexec(fd))
        child_argv = [sys.executable, __file__, str(fd),
                      'child process after exec']
        os.execv(child_argv[0], child_argv)

    os.waitpid(pid, 0)
    print("parent process after fork: cloexec=%s" % get_cloexec(fd))
    child_argv = [sys.executable, __file__, str(fd),
                  'parent process after exec']
    os.execv(child_argv[0], child_argv)

def after_exec():
    fd = int(sys.argv[1])
    name = sys.argv[2]
    print("%s: fd=%s, cloexec=%s"
          % (name, fd, get_cloexec(fd)))
    sys.exit()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        main()
    else:
        after_exec()

