import time

try:
    from time import timeout_time
except ImportError:
    from time import time as timeout_time

def compute_resolution(func):
    resolution = None
    points = 0
    timeout = timeout_time() + 1.0
    previous = func()
    while timeout_time() < timeout or points < 3:
        for loop in range(10):
            t1 = func()
            t2 = func()
            dt = t2 - t1
            if 0 < dt:
                break
        else:
            dt = t2 - previous
            if dt <= 0.0:
                continue
        if resolution is not None:
            resolution = min(resolution, dt)
        else:
            resolution = dt
        points += 1
        previous = func()
    return resolution

def format_duration(dt):
    if dt >= 1e-3:
        return "%.0f ms" % (dt * 1e3)
    if dt >= 1e-6:
        return "%.0f us" % (dt * 1e6)
    else:
        return "%.0f ns" % (dt * 1e9)

def test_clock(name, func):
    print("%s:" % name)
    resolution = compute_resolution(func)
    print("- resolution in Python: %s" % format_duration(resolution))


clocks = ['clock', 'perf_counter', 'process_time']
if hasattr(time, 'monotonic'):
    clocks.append('monotonic')
clocks.append('time')
for name in clocks:
    func = getattr(time, name)
    test_clock("%s()" % name, func)
    info = time.get_clock_info(name)
    print("- implementation: %s" % info.implementation)
    print("- resolution: %s" % format_duration(info.resolution))

clock_ids = [name for name in dir(time) if name.startswith("CLOCK_")]
clock_ids.sort()
for clock_id_text in clock_ids:
    clock_id = getattr(time, clock_id_text)
    name = 'clock_gettime(%s)' % clock_id_text
    def gettime():
        return time.clock_gettime(clock_id)
    try:
        gettime()
    except OSError as err:
        print("%s failed: %s" % (name, err))
        continue
    test_clock(name, gettime)
    resolution = time.clock_getres(clock_id)
    print("- announced resolution: %s" % format_duration(resolution))

