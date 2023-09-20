"""
Linux 3.6, O_CLOEXEC:

open(cloexec=False) + close(): 7.76 us per call
open(cloexec=True) + close(): 7.87 us per call

=> 1% slower

Linux 3.6, ioctl(FIOCLEX):

open(cloexec=False) + close(): 7.77 us per call
open(cloexec=True) + close(): 8.02 us per call

=> 3% slower

Linux 3.6, fnctl(F_GETFD) + fnctl(F_SETFD):

open(cloexec=False) + close(): 7.77 us per call
open(cloexec=True) + close(): 8.01 us per call

=> 3% slower
"""
import os, time

name = __file__
LOOPS = 10**5
RUNS = 5

for cloexec in (False, True):
    best = None
    for run in range(RUNS):
        print("cloexec", cloexec, "run", run)
        time.sleep(1)
        start = time.perf_counter()
        for loops in range(LOOPS):
            fd = os.open(name, os.O_RDONLY, cloexec=cloexec)
            os.close(fd)
        dt = time.perf_counter() - start
        if best is not None:
            best = min(best, dt)
        else:
            best = dt

    seconds = best / LOOPS
    print("open(cloexec=%s) + close(): %.2f us per call" % (cloexec, seconds * 1e6))
