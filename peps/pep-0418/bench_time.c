/*
 * Benchmark program written for the PEP 418.
 *
 * gcc bench_time.c -O3 -lrt -o bench_time && ./bench_time
 */

#include <time.h>
#include <stdio.h>
#include <sys/time.h>

#ifdef CLOCK_REALTIME
#  define HAVE_CLOCK_GETTIME
#else
typedef int clockid_t;
#endif

#define NRUN 5
#define NLOOP 100000
#define UNROLL(expr) \
    expr; expr; expr; expr; expr; expr; expr; expr; expr; expr
#define NUNROLL 10

#ifdef HAVE_CLOCK_GETTIME

typedef struct {
    const char *name;
    clockid_t identifier;
} CLOCK;

CLOCK clocks[] = {
#ifdef CLOCK_REALTIME_COARSE
    {"CLOCK_REALTIME_COARSE", CLOCK_REALTIME_COARSE},
#endif
#ifdef CLOCK_MONOTONIC_COARSE
    {"CLOCK_MONOTONIC_COARSE", CLOCK_MONOTONIC_COARSE},
#endif
#ifdef CLOCK_THREAD_CPUTIME_ID
    {"CLOCK_THREAD_CPUTIME_ID", CLOCK_THREAD_CPUTIME_ID},
#endif
#ifdef CLOCK_PROCESS_CPUTIME_ID
    {"CLOCK_PROCESS_CPUTIME_ID", CLOCK_PROCESS_CPUTIME_ID},
#endif
#ifdef CLOCK_MONOTONIC_RAW
    {"CLOCK_MONOTONIC_RAW", CLOCK_MONOTONIC_RAW},
#endif
#ifdef CLOCK_VIRTUAL
    {"CLOCK_VIRTUAL", CLOCK_VIRTUAL},
#endif
#ifdef CLOCK_UPTIME_FAST
    {"CLOCK_UPTIME_FAST", CLOCK_UPTIME_FAST},
#endif
#ifdef CLOCK_UPTIME_PRECISE
    {"CLOCK_UPTIME_PRECISE", CLOCK_UPTIME_PRECISE},
#endif
#ifdef CLOCK_UPTIME
    {"CLOCK_UPTIME", CLOCK_UPTIME},
#endif
#ifdef CLOCK_MONOTONIC_FAST
    {"CLOCK_MONOTONIC_FAST", CLOCK_MONOTONIC_FAST},
#endif
#ifdef CLOCK_MONOTONIC_PRECISE
    {"CLOCK_MONOTONIC_PRECISE", CLOCK_MONOTONIC_PRECISE},
#endif
#ifdef CLOCK_REALTIME_FAST
    {"CLOCK_REALTIME_FAST", CLOCK_REALTIME_FAST},
#endif
#ifdef CLOCK_REALTIME_PRECISE
    {"CLOCK_REALTIME_PRECISE", CLOCK_REALTIME_PRECISE},
#endif
#ifdef CLOCK_SECOND
    {"CLOCK_SECOND", CLOCK_SECOND},
#endif
#ifdef CLOCK_PROF
    {"CLOCK_PROF", CLOCK_PROF},
#endif
    {"CLOCK_MONOTONIC", CLOCK_MONOTONIC},
    {"CLOCK_REALTIME", CLOCK_REALTIME}
};
#define NCLOCKS (sizeof(clocks) / sizeof(clocks[0]))

void bench_clock_gettime(clockid_t clkid)
{
    unsigned long loop;
    struct timespec tmpspec;

    for (loop=0; loop<NLOOP; loop++) {
        UNROLL( (void)clock_gettime(clkid, &tmpspec) );
    }
}

#endif   /* HAVE_CLOCK_GETTIME */

void bench_time(clockid_t clkid)
{
    unsigned long loop;
    for (loop=0; loop<NLOOP; loop++) {
        UNROLL( (void)time(NULL) );
    }
}

void bench_usleep(clockid_t clkid)
{
    unsigned long loop;
    for (loop=0; loop<NLOOP; loop++) {
        UNROLL( (void)usleep(1000) );
    }
}

void bench_gettimeofday(clockid_t clkid)
{
    unsigned long loop;
    struct timeval tmpval;
    for (loop=0; loop<NLOOP; loop++) {
        UNROLL( (void)gettimeofday(&tmpval, NULL) );
    }
}

void bench_clock(clockid_t clkid)
{
    unsigned long loop;
    for (loop=0; loop<NLOOP; loop++) {
        UNROLL( (void)clock() );
    }
}

void benchmark(const char *name, void (*func) (clockid_t clkid), clockid_t clkid)
{
    unsigned int run;
    double dt, best;
#ifdef HAVE_CLOCK_GETTIME
    struct timespec before, after;
#else
    struct timeval before, after;
#endif
    struct timeval tmpval;

    best = -1.0;
    for (run=0; run<NRUN; run++) {
#ifdef HAVE_CLOCK_GETTIME
        clock_gettime(CLOCK_MONOTONIC, &before);
        (*func) (clkid);
        clock_gettime(CLOCK_MONOTONIC, &after);

        dt = (after.tv_sec - before.tv_sec) * 1e9;
        if (after.tv_nsec >= before.tv_nsec)
            dt += (after.tv_nsec - before.tv_nsec);
        else
            dt -= (before.tv_nsec - after.tv_nsec);
#else
        gettimeofday(&before, NULL);
        (*func) (clkid);
        gettimeofday(&after, NULL);

        dt = (after.tv_sec - before.tv_sec) * 1e9;
        if (after.tv_usec >= before.tv_usec)
            dt += (after.tv_usec - before.tv_usec) * 1e3;
        else
            dt -= (before.tv_usec - after.tv_usec) * 1e3;
#endif
        dt /= NLOOP;
        dt /= NUNROLL;

        if (best != -1.0) {
            if (dt < best)
                best = dt;
        }
        else
            best = dt;
    }
    printf("%s: %.0f ns\n", name, best, NLOOP);
}

int main()
{
#ifdef HAVE_CLOCK_GETTIME
    clockid_t clkid;
    int i;

    for (i=0; i<NCLOCKS; i++) {
        benchmark(clocks[i].name, bench_clock_gettime, clocks[i].identifier);
    }
#endif
    benchmark("clock()", bench_clock, 0);
    benchmark("gettimeofday()", bench_gettimeofday, 0);
    benchmark("time()", bench_time, 0);
    return 0;
}

