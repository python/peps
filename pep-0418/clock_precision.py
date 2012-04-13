import time

def compute_precision(func):
    previous = func()
    precision = None
    points = 0
    min_points = 100
    while points < min_points:
        value = func()
        if value == previous:
            continue
        dt = value - previous
        previous = value
        if precision is not None:
            precision = min(precision, dt)
        else:
            precision = dt
        if precision < 10e-6:
            min_points = 5000
        elif precision < 1e-3:
            min_points = 1000
        points += 1
    return dt

def format_duration(dt):
    if dt >= 1e-3:
        return "%.1f ms" % (dt * 1e3)
    if dt >= 1e-6:
        return "%.1f µs" % (dt * 1e6)
    else:
        return "%.1f ns" % (dt * 1e9)

def test_clock(name, func):
    precision = compute_precision(func)
    print("%s:" % name)
    print("- precision in Python: %s" % format_duration(precision))


for name in ('clock', 'perf_counter', 'process_time', 'monotonic', 'time'):
    func = getattr(time, name)
    test_clock("%s()" % name, func)
    info = time.get_clock_info(name)
    if 'precision' in info:
        print("- announced precision: %s" % format_duration(info['precision']))
    print("- function: %s" % info['function'])
    print("- resolution: %s" % format_duration(info['resolution']))

clock_ids = [name for name in dir(time) if name.startswith("CLOCK_")]
for clock_id_text in clock_ids:
    clock_id = getattr(time, clock_id_text)
    name = 'clock_gettime(%s)' % clock_id_text
    def gettime():
        return time.clock_gettime(clock_id)
    test_clock(name, gettime)

