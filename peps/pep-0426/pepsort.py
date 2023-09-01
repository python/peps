#!/usr/bin/env python3

# Distribution sorting comparisons
#   between pkg_resources, PEP 386 and PEP 426
#
# Requires distlib, original script written by Vinay Sajip

import logging
import re
import sys
import json
import errno
import time

from distlib.compat import xmlrpclib
from distlib.version import suggest_normalized_version, legacy_key, normalized_key

logger = logging.getLogger(__name__)

PEP426_VERSION_RE = re.compile(r'^(\d+(\.\d+)*)((a|b|c|rc)(\d+))?'
                               r'(\.(post)(\d+))?(\.(dev)(\d+))?$')

PEP426_PRERELEASE_RE = re.compile(r'(a|b|c|rc|dev)\d+')

def pep426_key(s):
    s = s.strip()
    m = PEP426_VERSION_RE.match(s)
    if not m:
        raise ValueError('Not a valid version: %s' % s)
    groups = m.groups()
    nums = tuple(int(v) for v in groups[0].split('.'))
    while len(nums) > 1 and nums[-1] == 0:
        nums = nums[:-1]

    pre = groups[3:5]
    post = groups[6:8]
    dev = groups[9:11]
    if pre == (None, None):
        pre = ()
    else:
        pre = pre[0], int(pre[1])
    if post == (None, None):
        post = ()
    else:
        post = post[0], int(post[1])
    if dev == (None, None):
        dev = ()
    else:
        dev = dev[0], int(dev[1])
    if not pre:
        # either before pre-release, or final release and after
        if not post and dev:
            # before pre-release
            pre = ('a', -1) # to sort before a0
        else:
            pre = ('z',)    # to sort after all pre-releases
    # now look at the state of post and dev.
    if not post:
        post = ('a',)
    if not dev:
        dev = ('final',)

    return nums, pre, post, dev

def is_release_version(s):
    return not bool(PEP426_PRERELEASE_RE.search(s))

def cache_projects(cache_name):
    logger.info("Retrieving package data from PyPI")
    client = xmlrpclib.ServerProxy('http://python.org/pypi')
    projects = dict.fromkeys(client.list_packages())
    public = projects.copy()
    failed = []
    for pname in projects:
        time.sleep(0.01)
        logger.debug("Retrieving versions for %s", pname)
        try:
            projects[pname] = list(client.package_releases(pname, True))
            public[pname] = list(client.package_releases(pname))
        except:
            failed.append(pname)
    logger.warn("Error retrieving versions for %s", failed)
    with open(cache_name, 'w') as f:
        json.dump([projects, public], f, sort_keys=True,
                  indent=2, separators=(',', ': '))
    return projects, public

def get_projects(cache_name):
    try:
        f = open(cache_name)
    except IOError as exc:
        if exc.errno != errno.ENOENT:
            raise
        projects, public = cache_projects(cache_name);
    else:
        with f:
            projects, public = json.load(f)
    return projects, public


VERSION_CACHE = "pepsort_cache.json"

class Category(set):

    def __init__(self, title, num_projects):
        super().__init__()
        self.title = title
        self.num_projects = num_projects

    def __str__(self):
        num_projects = self.num_projects
        num_in_category = len(self)
        pct = (100.0 * num_in_category) / num_projects
        return "{}: {:d} / {:d} ({:.2f} %)".format(
                    self.title, num_in_category, num_projects, pct)

SORT_KEYS = {
    "386": normalized_key,
    "426": pep426_key,
}

class Analysis:

    def __init__(self, title, projects, releases_only=False):
        self.title = title
        self.projects = projects

        num_projects = len(projects)

        compatible_projects = Category("Compatible", num_projects)
        translated_projects = Category("Compatible with translation", num_projects)
        filtered_projects = Category("Compatible with filtering", num_projects)
        incompatible_projects = Category("No compatible versions", num_projects)
        sort_error_translated_projects = Category("Sorts differently (after translations)", num_projects)
        sort_error_compatible_projects = Category("Sorts differently (no translations)", num_projects)
        null_projects = Category("No applicable versions", num_projects)

        self.categories = [
            compatible_projects,
            translated_projects,
            filtered_projects,
            incompatible_projects,
            sort_error_translated_projects,
            sort_error_compatible_projects,
            null_projects,
        ]

        sort_key = SORT_KEYS[pepno]
        sort_failures = 0
        for i, (pname, versions) in enumerate(projects.items()):
            if i % 100 == 0:
                sys.stderr.write('%s / %s\r' % (i, num_projects))
                sys.stderr.flush()
            if not versions:
                logger.debug('%-15.15s has no versions', pname)
                null_projects.add(pname)
                continue
            # list_legacy and list_pep will contain 2-tuples
            # comprising a sortable representation according to either
            # the setuptools (legacy) algorithm or the PEP algorithm.
            # followed by the original version string
            # Go through the PEP 386/426 stuff one by one, since
            # we might get failures
            list_pep = []
            release_versions = set()
            prerelease_versions = set()
            excluded_versions = set()
            translated_versions = set()
            for v in versions:
                s = v
                try:
                    k = sort_key(v)
                except Exception:
                    s = suggest_normalized_version(v)
                    if not s:
                        good = False
                        logger.debug('%-15.15s failed for %r, no suggestions', pname, v)
                        excluded_versions.add(v)
                        continue
                    else:
                        try:
                            k = sort_key(s)
                        except ValueError:
                            logger.error('%-15.15s failed for %r, with suggestion %r',
                                         pname, v, s)
                            excluded_versions.add(v)
                            continue
                    logger.debug('%-15.15s translated %r to %r', pname, v, s)
                    translated_versions.add(v)
                if is_release_version(s):
                    release_versions.add(v)
                else:
                    prerelease_versions.add(v)
                    if releases_only:
                        logger.debug('%-15.15s ignoring pre-release %r', pname, s)
                        continue
                list_pep.append((k, v))
            if releases_only and prerelease_versions and not release_versions:
                logger.debug('%-15.15s has no release versions', pname)
                null_projects.add(pname)
                continue
            if not list_pep:
                logger.debug('%-15.15s has no compatible versions', pname)
                incompatible_projects.add(pname)
                continue
            # The legacy approach doesn't refuse the temptation to guess,
            # so it *always* gives some kind of answer
            if releases_only:
                excluded_versions |= prerelease_versions
            accepted_versions = set(versions) - excluded_versions
            list_legacy = [(legacy_key(v), v) for v in accepted_versions]
            assert len(list_legacy) == len(list_pep)
            sorted_legacy = sorted(list_legacy)
            sorted_pep = sorted(list_pep)
            sv_legacy = [t[1] for t in sorted_legacy]
            sv_pep = [t[1] for t in sorted_pep]
            if sv_legacy != sv_pep:
                if translated_versions:
                     logger.debug('%-15.15s translation creates sort differences', pname)
                     sort_error_translated_projects.add(pname)
                else:
                     logger.debug('%-15.15s incompatible due to sort errors', pname)
                     sort_error_compatible_projects.add(pname)
                logger.debug('%-15.15s unequal: legacy: %s', pname, sv_legacy)
                logger.debug('%-15.15s unequal: pep%s: %s', pname, pepno, sv_pep)
                continue
            # The project is compatible to some degree,
            if excluded_versions:
                logger.debug('%-15.15s has some compatible versions', pname)
                filtered_projects.add(pname)
                continue
            if translated_versions:
                logger.debug('%-15.15s is compatible after translation', pname)
                translated_projects.add(pname)
                continue
            logger.debug('%-15.15s is fully compatible', pname)
            compatible_projects.add(pname)

    def print_report(self):
        print("Analysing {}".format(self.title))
        for category in self.categories:
            print(" ", category)


def main(pepno = '426'):
    print('Comparing PEP %s version sort to setuptools.' % pepno)

    projects, public = get_projects(VERSION_CACHE)
    print()
    Analysis("release versions", public, releases_only=True).print_report()
    print()
    Analysis("public versions", public).print_report()
    print()
    Analysis("all versions", projects).print_report()
    # Uncomment the line below to explore differences in details
    # import pdb; pdb.set_trace()
    # Grepping the log files is also informative
    # e.g. "grep unequal pep426sort.log" for the PEP 426 sort differences

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '386':
        pepno = '386'
    else:
        pepno = '426'
    logname = 'pep{}sort.log'.format(pepno)
    logging.basicConfig(level=logging.DEBUG, filename=logname,
                        filemode='w', format='%(message)s')
    logger.setLevel(logging.DEBUG)
    main(pepno)

