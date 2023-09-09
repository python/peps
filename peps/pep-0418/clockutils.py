#!/usr/bin/python
#
# Framework to present system clocks by feature, intended to avoid
# the library-as-policy pitfalls of the discussion around PEP 418.
#
# My 2c:
# http://www.gossamer-threads.com/lists/python/dev/977474#977474
# http://www.gossamer-threads.com/lists/python/dev/977495#977495
# or:
# http://www.mail-archive.com/python-dev@python.org/msg66174.html
# http://www.mail-archive.com/python-dev@python.org/msg66179.html
#       - Cameron Simpson <cs@cskk.id.au> 02apr2012
#

from collections import namedtuple
from time import time
import os

# the module exposing OS clock features
_time = os

HIGHRES = 0x01    # high resolution
MONOTONIC = 0x02  # never goes backwards
STEADY = 0x04     # never steps; implies MONOTONIC
ADJUSTED = 0x08   # may be adjusted, for example by NTP
WALLCLOCK = 0x10  # tracks real world time, will usually be ADJUSTED too
RUNTIME = 0x20    # track system run time - stops when system suspended
SYNTHETIC = 0x40  # a synthetic clock, computed from other clocks

def get_clock(flags=0, clocklist=None):
    ''' Return a clock based on the supplied `flags`.
        The returned clock shall have all the requested flags.
        If no clock matches, return None.
    '''
    for clock in get_clocks(flags=flags, clocklist=clocklist):
      return clock
    return None

def get_clocks(flags=0, clocklist=None):
    ''' Yield all clocks matching the supplied `flags`.
        The returned clocks shall have all the requested flags.
    '''
    if clocklist is None:
        clocklist = ALL_CLOCKS
    for clock in clocklist:
        if clock.flags & flags == flags:
            yield clock.factory()

def monotonic_clock(other_flags=0):
    ''' Return a monotonic clock, preferably high resolution.
    '''
    return get_clock(MONOTONIC|HIGHRES|other_flags, MONOTONIC_CLOCKS) \
        or get_clock(MONOTONIC|other_flags, MONOTONIC_CLOCKS)

def steady_clock(other_flags=0):
    ''' Return a steady clock, preferably high resolution.
    '''
    return get_clock(STEADY|HIGHRES|other_flags, STEADY_CLOCKS) \
        or get_clock(STEADY|other_flags, STEADY_CLOCKS)

def highres_clock(other_flags=0):
    ''' Return a high resolution clock, preferably steady.
    '''
    return get_clock(HIGHRES|STEADY|other_flags, HIGHRES_CLOCKS) \
        or get_clock(HIGHRES|other_flags, HIGHRES_CLOCKS)

_global_monotonic = None

def monotonic():
    ''' Return the current time according to the default monotonic clock.
    '''
    global _global_monotonic
    if _global_monotonic is None:
        _global_monotonic = monotonic_clock()
        if _global_monotonic is None:
            raise RunTimeError("no monotonic clock available")
    return _global_monotonic.now()

_global_hires = None

def highres():
    ''' Return the current time according to the default high resolution clock.
    '''
    global _global_hires
    if _global_hires is None:
        _global_hires = highres()
        if _global_hires is None:
            raise RunTimeError("no highres clock available")
    return _global_hires.now()

_global_steady = None

def steady():
    ''' Return the current time according to the default steady clock.
    '''
    global _global_steady
    if _global_steady is None:
        _global_steady = steady()
        if _global_steady is None:
            raise RunTimeError("no steady clock available")
    return _global_steady.now()

class _Clock_Flags(int):
    ''' An int with human friendly str() and repr() for clock flags.
    '''

    _flag_names = (
        'HIGHRES',
        'MONOTONIC',
        'STEADY',
        'ADJUSTED',
        'WALLCLOCK',
        'RUNTIME',
        'SYNTHETIC',
    )

    def __str__(self):
        f = self
        G = globals()
        names = []
        for name in _Clock_Flags._flag_names:
            n = G[name]
            if f & n:
                names.append(name)
                f &= ~n
        if f:
            names.append('0x%02x' % f)
        return '|'.join(names) if names else '0'

    def __repr__(self):
        return '<%s %02x %s>' % (self.__class__.__name__, self, self)

# now assemble the list of platform clocks

class _Clock(object):
    ''' A _Clock is the private base class of clock objects.
        A clock has the following mandatory attributes:
            .flags  Feature flags describing the clock.
        A clock may have the following optional attributes:
            .epoch  If present, the offset from time.time()'s epoch
                    of this clock's epoch(). Not all clocks have epochs; some
                    measure elapsed time from an unknown point and only the
                    difference in two measurements is useful.
            .resolution
                    The resolution of the underlying clock facility's
                    reporting units. The clock can never be more precise than
                    this value. The actual accuracy of the reported time may
                    vary with adjustments and the real accuracy of the
                    underlying OS clock facility (which in turn may be
                    dependent on the precision of some hardware clock).
        A clock must also supply the following methods:
            .now()  Report the current time in seconds, a float.
    '''
    def __init__(self):
        ''' Set instance attributes from class attributes, suitable to
            singleton clocks.
        '''
        klass = self.__class__
        self.flags = _Clock_Flags(klass.flags)
        for attr in 'epoch', 'resolution':
            try:
                attrval = getattr(klass, attr)
            except AttributeError:
                pass
            else:
                setattr(self, attr, attrval)

    def __repr__(self):
        props = [self.__class__.__name__]
        for attr in sorted( [ attr for attr in dir(self)
                              if attr
                                 and attr[0].isalpha()
                                 and attr not in ('now',)] ):
            props.append("%s=%s" % (attr, getattr(self, attr)))
        return "<" + " ".join(props) + ">"

ClockEntry = namedtuple('ClockEntry', 'flags factory')

ALL_CLOCKS = []

def _SingletonClockEntry( klass ):
    ''' Construct a ClockEntry for a Singleton class, typical for system clocks.
    '''
    klock = klass()
    return ClockEntry( klass.flags, lambda: klock )

# always provide good old time.time()
# provide no flags - this is a fallback - totally implementation agnostic
class _TimeDotTimeClock(_Clock):
    ''' A clock made from time.time().
    '''
    flags = 0
    epoch = 0
    def now(self):
        return time()
ALL_CLOCKS.append( _SingletonClockEntry(_TimeDotTimeClock) )

# load system specific clocks here
# in notional order of preference

if os.name == "nt":

    class _NT_GetSystemTimeAsFileTimeClock(_Clock):
        ''' A clock made from GetSystemTimeAsFileTime().
        '''
        flags = WALLCLOCK
        epoch = EPOCH_16010101T000000   # 01jan1601
                                        # a negative value wrt 01jan1970
        resolution = 0.0000001          # 100 nanosecond units
                                        # accuracy HW dependent?
        def now(self):
            # convert 100-nanosecond intervals since 1601 to UNIX style seconds
            return ( _time._GetSystemTimeAsFileTime() / 10000000
                   + NT_GetSystemTimeAsFileTimeClock.epoch
                   )
    ALL_CLOCKS.append( _SingletonClockEntry(_NT_GetSystemTimeAsFileTimeClock) )

    class _NT_GetTickCount64(_Clock):
        ''' Based on
                http://msdn.microsoft.com/en-us/library/windows/desktop/ms724411%28v=vs.85%29.aspx
            Note that this specifically disavows high resolution.
        '''
        flags = RUNTIME|MONOTONIC
        resolution = 0.001
        def now(self):
            msecs = _time.GetTickCount64()
            return msecs / 1000
    ALL_CLOCKS.append( _SingletonClockEntry(_NT_GetTickCount64) )

else:

    # presuming clock_gettime() and clock_getres() exposed in the os
    # module, along with the clock id names
    if hasattr(_time, "clock_gettime"):

        try:
            clk_id = _time.CLOCK_REALTIME
        except AttributeError:
            pass
        else:
            try:
                timespec = _time.clock_getres(clk_id)
            except OSError:
                pass
            else:
                class _UNIX_CLOCK_REALTIME(_Clock):
                    ''' A clock made from clock_gettime(CLOCK_REALTIME).
                    '''
                    epoch = 0
                    flags = WALLCLOCK
                    resolution = timespec.tv_sec + timespec.tv_nsec / 1000000000
                    @staticmethod
                    def now():
                        timespec = _time.clock_gettime(_time.CLOCK_REALTIME)
                        return timespec.tv_sec + timespec.tv_nsec / 1000000000
                ALL_CLOCKS.append( _SingletonClockEntry(_UNIX_CLOCK_REALTIME) )

        try:
            clk_id = _time.CLOCK_MONOTONIC
        except AttributeError:
            pass
        else:
            try:
                timespec = _time.clock_getres(clk_id)
            except OSError:
                pass
            else:
                class _UNIX_CLOCK_MONOTONIC(_Clock):
                    ''' A clock made from clock_gettime(CLOCK_MONOTONIC).
                    '''
                    flags = MONOTONIC|STEADY|ADJUSTED
                    resolution = timespec.tv_sec + timespec.tv_nsec / 1000000000
                    @staticmethod
                    def now():
                        timespec = _time.clock_gettime(_time.CLOCK_MONOTONIC)
                        return timespec.tv_sec + timespec.tv_nsec / 1000000000
                ALL_CLOCKS.append( _SingletonClockEntry(_UNIX_CLOCK_MONOTONIC) )

        try:
            clk_id = _time.CLOCK_MONOTONIC_RAW
        except AttributeError:
            pass
        else:
            try:
                timespec = _time.clock_getres(clk_id)
            except OSError:
                pass
            else:
                class _UNIX_CLOCK_MONOTONIC_RAW(_Clock):
                    ''' A clock made from clock_gettime(CLOCK_MONOTONIC_RAW).
                    '''
                    flags = MONOTONIC|STEADY
                    resolution = timespec.tv_sec + timespec.tv_nsec / 1000000000
                    @staticmethod
                    def now():
                        timespec = _time.clock_gettime(_time.CLOCK_MONOTONIC_RAW)
                        return timespec.tv_sec + timespec.tv_nsec / 1000000000
                ALL_CLOCKS.append( _SingletonClockEntry(_UNIX_CLOCK_MONOTONIC_RAW) )

        try:
            clk_id = _time.CLOCK_PROCESS_CPUTIME_ID
        except AttributeError:
            pass
        else:
            try:
                timespec = _time.clock_getres(clk_id)
            except OSError:
                pass
            else:
                class _UNIX_CLOCK_PROCESS_CPUTIME_ID(_Clock):
                    ''' A clock made from clock_gettime(CLOCK_PROCESS_CPUTIME_ID).
                    '''
                    flags = MONOTONIC
                    resolution = timespec.tv_sec + timespec.tv_nsec / 1000000000
                    @staticmethod
                    def now():
                        timespec = _time.clock_gettime(_time.CLOCK_PROCESS_CPUTIME_ID)
                        return timespec.tv_sec + timespec.tv_nsec / 1000000000
                ALL_CLOCKS.append( _SingletonClockEntry(_CLOCK_PROCESS_CPUTIME_ID) )

        try:
            clk_id = _time.CLOCK_THREAD_CPUTIME_ID
        except AttributeError:
            pass
        else:
            try:
                timespec = _time.clock_getres(clk_id)
            except OSError:
                pass
            else:
                class _UNIX_CLOCK_THREAD_CPUTIME_ID(_Clock):
                    ''' A clock made from clock_gettime(CLOCK_THREAD_CPUTIME_ID).
                    '''
                    flags = MONOTONIC
                    resolution = timespec.tv_sec + timespec.tv_nsec / 1000000000
                    @staticmethod
                    def now():
                        timespec = _time.clock_gettime(_time.CLOCK_THREAD_CPUTIME_ID)
                        return timespec.tv_sec + timespec.tv_nsec / 1000000000
                ALL_CLOCKS.append( _SingletonClockEntry(_CLOCK_CLOCK_THREAD_CPUTIME_ID) )

    if hasattr(_time, "gettimeofday"):
        class _UNIX_gettimeofday(_Clock):
            ''' A clock made from gettimeofday().
            '''
            epoch = 0
            flags = WALLCLOCK
            resolution = 0.000001
            def now(self):
                timeval = _time.gettimeofday()
                return timeval.tv_sec + timeval.tv_usec / 1000000
        ALL_CLOCKS.append( _SingletonClockEntry(_UNIX_gettimeofday) )

    if hasattr(_time, "ftime"):
        class _UNIX_ftime(_Clock):
            ''' A clock made from ftime().
            '''
            epoch = 0
            flags = WALLCLOCK|ADJUSTED
            resolution = 0.001
            def now(self):
                timeb = _time.ftime()
                return timeb.time + timeb.millitm / 1000
        ALL_CLOCKS.append( _SingletonClockEntry(_UNIX_ftime) )

# an example synthetic clock, coming after time.time()
# because I think synthetic clocks should be less desired
# - they tend to have side effects; but perhaps offered anyway because
# they can offer flag combinations not always presented by the system
# clocks

# a simple synthetic monotonic clock
# may skew with respect to other instances
# Steven D'Aprano wrote a better one
class SyntheticMonotonic(_Clock):
    flags = SYNTHETIC|MONOTONIC
    def __init__(self, base_clock=None):
        _Clock.__init__(self)
        if base_clock is None:
            base_clock = _TimeDotTimeClock()
        self.base_clock = base_clock
        for attr in 'epoch', 'resolution':
            try:
                attrval = getattr(base_clock, attr)
            except AttributeError:
                pass
            else:
                setattr(self, attr, attrval)
        self.__last = None
        self.__base = base_clock
    def now(self):
        last = self.__last
        t = self.__base.now()
        if last is None or last < t:
            self.__last = t
        else:
            t = last
        return t

ALL_CLOCKS.append( ClockEntry(SyntheticMonotonic.flags, SyntheticMonotonic) )

# With more clocks, these will be ALL_CLOCKS listed in order of preference
# for these types i.e. MONOTONIC_CLOCKS will list only monotonic clocks
# in order of quality (an arbitrary measure, perhaps).
MONOTONIC_CLOCKS = ALL_CLOCKS
HIGHRES_CLOCKS = ALL_CLOCKS
STEADY_CLOCKS = ALL_CLOCKS

if __name__ == '__main__':
    print("ALL_CLOCKS =", repr(ALL_CLOCKS))
    for clock in get_clocks():
        print("clock = %r" % (clock,))
        print(clock.__class__.__doc__)
