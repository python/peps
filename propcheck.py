"""Perform an integrity check upon all PEPs to make sure the needed svn
properties are set."""

import glob
import pdb
import subprocess
from xml.etree import ElementTree

PROPS = {'svn:eol-style': "native", 'svn:keywords': "Author Date Id Revision"}


def get_props():
    """Return the properties set on pep-*.txt files as an ElementTree instance.

    Files with no properties set will not be contained in the returned data.

    """
    cmd = 'svn proplist --xml pep-*.txt'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    xml_results = proc.communicate()[0]
    if proc.returncode:
        raise subprocess.CalledProcessError("%s returned %d" %
                                            (cmd, proc.returncode))
    return ElementTree.fromstring(xml_results)


def missing_props(props):
    """Figure out what properties are missing on what PEPs, returning a sequence
    of (path, [missing_props]) pairs.

    For the set properties (as calculated by get_props()), see which PEPs are
    lacking any properties. For the PEPs that are not even listed in the set
    properties, assume they are missing all needed properties.

    """
    problems = []
    missing_files = set(glob.glob('pep-*.txt'))
    missing_files.remove('pep-0000.txt')
    for target in props:
        assert target.tag == 'target'
        needs = PROPS.keys()
        path = target.attrib['path']
        missing_files.remove(path)
        for property in target.getchildren():
            assert property.tag == 'property'
            try:
                needs.remove(property.attrib['name'])
            except ValueError:
                pass
        if needs:
            problems.append([path, needs])
    for path in missing_files:
        problems.append([path, PROPS.keys()])
    return problems


def fix_props(missing_props):
    """Fix the missing properties."""
    for path, missing in missing_props:
        print "For %s, setting %s" % (path, missing)
        for problem in missing:
            cmd = 'svn propset %s "%s" %s' % (problem, PROPS[problem], path)
            subprocess.check_call(cmd, shell=True)


def main():
    props = get_props()
    need_fixing = missing_props(props)
    fix_props(need_fixing)



if __name__ == '__main__':
    main()
