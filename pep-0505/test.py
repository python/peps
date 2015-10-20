'''
This file is used for testing find-pep505.out.

nc_* and Nc* are examples of null coalescing.
sn_* and Sn* are examples of save navigation.
'''

def nc_ifblock1(a=None):
    if a is None:
        a = 'foo'

def nc_ifblock2(a=None):
    if a is not None:
        pass
    else:
        a = 'foo'

class NcIfBlock3:
    def __init__(self, a=None):
        if a is None:
            self.b = {}
        else:
            self.b = a

class NcIfBlock4:
    def __init__(self, a=None):
        if a is not None:
            self.b = a
        else:
            self.b = {}

def nc_or1(a=None):
    return a or 'foo'

def nc_or2(a=None):
    return a or []

def nc_ternary1(a=None):
    return a if a is not None else 'foo'

def nc_ternary2(a=None):
    return 'foo' if a is None else a

def sn_and1(a=None):
    return a and a.foo

def sn_and2(a=None):
    return a and a['foo']

def sn_and3(a=None):
    return a and a.foo()

def sn_and3(a=None):
    return a and a.foo.bar

class SnIfBlock1:
    def __init__(self, a=None):
        if a is not None:
            a.foo()

class SnIfBlock2:
    def __init__(self, a=None):
        if a is None:
            pass
        else:
            a.foo()

class SnIfBlock3:
    def __init__(self, a=None):
        if a is None:
            b = 'foo'
        else:
            b = a.foo

class SnIfBlock4:
    def __init__(self, a=None):
        if a is None:
            b = 'foo'
        else:
            b = a['foo']

def sn_ternary1(a=None):
    return a.foo if a is not None else None

def sn_ternary2(a=None):
    return None if a is None else a.foo

def sn_ternary3(a=None):
    return a['foo'] if a is not None else None

def sn_ternary4(a=None):
    return None if a is None else a.foo()
