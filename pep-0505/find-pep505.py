'''
Find code patterns that PEP-505 attempts to make more concise.

Example usage:

    $ find /usr/lib/python3.4 -name '*.py' | xargs python3 find-pep505.py

'''

import ast
import sys


class NoneCoalesceIfBlockVisitor(ast.NodeVisitor):
    '''
    Look for if blocks of the form:

        >>> if a is None:
        ...     a = b

        >>> if a is not None:
        ...     b
        ... else:
        ...     a = c

        >>> def foo(self, a=None):
        ...     if a is None:
        ...         self.b = c
        ...     else:
        ...         self.b = a

        >>> def foo(self, a=None):
        ...     if a is not None:
        ...         self.b = a
        ...     else:
        ...         self.b = c

    ...where `a` is a name and other characters represent any abitrary
    expression.

    In the two latter forms, the search criterion is an assignment of `a`
    to any identifier in the `a is not None` block.
    '''

    def __init__(self, file_, callback):
        self.__file = file_
        self.__callback = callback

    def visit_If(self, if_):

        if not isinstance(if_.test, ast.Compare):
            return

        op = if_.test.ops[0]

        # Match `if a is None:` or `if a is not None:`, where `a` is a name.
        if isinstance(op, (ast.Is, ast.IsNot)) and \
           isinstance(if_.test.left, ast.Name) and \
           isinstance(if_.test.comparators[0], ast.NameConstant) and \
           if_.test.comparators[0].value is None:

            test_name = if_.test.left.id
        else:
            return

        # Keep track of which block handles the `a is None` condition and which
        # handles the `a is not None` condition.
        if isinstance(op, ast.Is):
            none_block = if_.body
            value_block = if_.orelse
        elif isinstance(op, ast.IsNot):
            none_block = if_.orelse
            value_block = if_.body

        if len(none_block) != 1:
            return

        none_stmt = none_block[0]

        # If there is no `a is not None` block, handle gracefully.
        if len(value_block) == 1:
            value_stmt = value_block[0]
        else:
            value_stmt = None

        # Assigning a value to `a` when it is `None`?
        if isinstance(none_stmt, ast.Assign) and \
           len(none_stmt.targets) == 1:

            target = none_stmt.targets[0]

            if isinstance(target, ast.Name):
                if test_name == target.id:
                    self.__callback(self.__file, if_.test.lineno,
                                    target.lineno)
                    return

        # Assigning value of `a` to another identifier when a is not `None`?
        if isinstance(value_stmt, ast.Assign) and \
             isinstance(value_stmt.value, ast.Name) and \
             test_name == value_stmt.value.id:

            end_line = max(value_stmt.lineno, none_stmt.lineno)
            self.__callback(self.__file, if_.test.lineno, end_line)


class NoneCoalesceOrVisitor(ast.NodeVisitor):
    '''
    Look for expressions of the form:

        >>> a or '1'
        >>> a or []
        >>> a or {}

    ...where `a` is any name. More formally, match a plain name on the left side
    of `or` and something that looks like a default on the right, e.g. a
    constant or a constructor invocation.
    '''

    def __init__(self, file_, callback):
        self.__file = file_
        self.__callback = callback

    def visit_BoolOp(self, bool_op):
        if not isinstance(bool_op.op, ast.Or) or \
           not isinstance(bool_op.values[0], ast.Name):
            return

        defaults = ast.Call, ast.Dict, ast.List, ast.Num, ast.Set, ast.Str

        if isinstance(bool_op.values[1], defaults):
            start_line = bool_op.values[0].lineno
            end_line = bool_op.values[-1].lineno
            self.__callback(self.__file, start_line, end_line)


class NoneCoalesceTernaryVisitor(ast.NodeVisitor):
    '''
    Look for ternary expressions of the form:

        >>> a if a is not None else b
        >>> b if a is None else a

    ...where a is an identifier and b is an abitrary expression.
    '''

    def __init__(self, file_, callback):
        self.__file = file_
        self.__callback = callback

    def visit_IfExp(self, ifexp):
        if isinstance(ifexp.test, ast.Compare):
            op = ifexp.test.ops[0]

            # Match `a is None` or `a is not None`, where `a` is a name.
            if isinstance(op, (ast.Is, ast.IsNot)) and \
               isinstance(ifexp.test.left, ast.Name) and \
               isinstance(ifexp.test.comparators[0], ast.NameConstant) and \
               ifexp.test.comparators[0].value is None:

                test_name = ifexp.test.left.id
            else:
                return

            if isinstance(op, ast.IsNot) and isinstance(ifexp.body, ast.Name):
                # Match `a if a is not None else ...`.
                result_name = ifexp.body.id
            elif isinstance(op, ast.Is) and isinstance(ifexp.orelse, ast.Name):
                # Match `... if a is None else a`.
               result_name = ifexp.orelse.id
            else:
                return

            if test_name == result_name:
                self.__callback(self.__file, ifexp.test.lineno, None)


class SafeNavAndVisitor(ast.NodeVisitor):
    '''
    Look for expressions where `and` is used to avoid attribute/index access on
    ``None``:

        >>> a and a.foo
        >>> a and a[foo]
        >>> a and a.foo()
        >>> a and a.foo.bar

    ...where `a` is any name and `foo`, `bar` are any attribute or keys.
    '''

    def __init__(self, file_, callback):
        self.__file = file_
        self.__callback = callback

    def visit_BoolOp(self, bool_op):
        if not isinstance(bool_op.op, ast.And) or \
           not isinstance(bool_op.values[0], ast.Name):
            return

        left_name = bool_op.values[0].id
        right = bool_op.values[1]

        if isinstance(right, (ast.Attribute, ast.Call, ast.Subscript)):
            right_name = get_name_from_node(right)
        else:
            return

        if left_name == right_name:
            start_line = bool_op.values[0].lineno
            end_line = bool_op.values[-1].lineno
            self.__callback(self.__file, start_line, end_line)


class SafeNavIfBlockVisitor(ast.NodeVisitor):
    '''
    Look for blocks where `if` is used to avoid attribute/index access on
    ``None``:

        >>> if a is not None:
        ...     a.foo

        >>> if a is None:
        ...     pass
        ... else:
        ...     a.foo

    ...where `a` is any name. Index access and function calls are also matched.
    '''

    def __init__(self, file_, callback):
        self.__file = file_
        self.__callback = callback

    def visit_If(self, if_):

        if not isinstance(if_.test, ast.Compare):
            return

        op = if_.test.ops[0]

        # Match `if a is None:` or `if a is not None:`, where `a` is a name.
        if isinstance(op, (ast.Is, ast.IsNot)) and \
           isinstance(if_.test.left, ast.Name) and \
           isinstance(if_.test.comparators[0], ast.NameConstant) and \
           if_.test.comparators[0].value is None:

            test_name = if_.test.left.id
        else:
            return

        # Keep track of which block handles the `a is None` condition and which
        # handles the `a is not None` condition.
        if isinstance(op, ast.Is):
            none_block = if_.body
            value_block = if_.orelse
        elif isinstance(op, ast.IsNot):
            none_block = if_.orelse
            value_block = if_.body

        if len(none_block) > 0:
            none_lineno = none_block[0].lineno
        else:
            none_lineno = 0

        # If there is no `a is not None` block, then it's definitely not a
        # match.
        if len(value_block) == 1:
            value_stmt = value_block[0]
        else:
            return

        # Assigning the value of `a.foo` or `a[foo]` or calling `a.foo()` in the
        # `a is not None` block. (But don't match bare `a` -- that's already
        # covered by the None coalesce visitors.)
        if isinstance(value_stmt, (ast.Assign, ast.Expr)) and \
           not isinstance(value_stmt.value, ast.Name):
            expr_name = get_name_from_node(value_stmt.value)
        else:
            return

        # Assigning value of `a` to another identifier when a is not `None`?
        if test_name == expr_name:
            end_line = max(value_stmt.lineno, none_lineno)
            self.__callback(self.__file, if_.test.lineno, end_line)


class SafeNavTernaryVisitor(ast.NodeVisitor):
    '''
    Look for ternary expressions of the form:

        >>> a.foo if a is not None else b
        >>> b if a is None else a.foo

    ...where `a` is an identifier, `b` is an abitrary expression, and `foo` is
    an attribute, index, or function invocation.
    '''

    def __init__(self, file_, callback):
        self.__file = file_
        self.__callback = callback

    def visit_IfExp(self, ifexp):
        if isinstance(ifexp.test, ast.Compare):
            op = ifexp.test.ops[0]

            # Match `a is None` or `a is not None`, where `a` is a name.
            if isinstance(op, (ast.Is, ast.IsNot)) and \
               isinstance(ifexp.test.left, ast.Name) and \
               isinstance(ifexp.test.comparators[0], ast.NameConstant) and \
               ifexp.test.comparators[0].value is None:

                test_name = ifexp.test.left.id
            else:
                return

            exprs = ast.Attribute, ast.Call, ast.Subscript

            if isinstance(op, ast.IsNot) and isinstance(ifexp.body, exprs):
                # Match `a.foo if a is not None else ...`.
                result_name = get_name_from_node(ifexp.body)
            elif isinstance(op, ast.Is) and isinstance(ifexp.orelse, exprs):
                # Match `... if a is None else a.foo`.
                result_name = get_name_from_node(ifexp.orelse)
            else:
                return

            if test_name == result_name:
                self.__callback(self.__file, ifexp.test.lineno, None)


def count_calls_decorator(callback):
    '''
    Decorator for a callback that counts how many time that callback
    was invoked.
    '''

    def invoke(*args):
        callback(*args)
        invoke.count += 1

    invoke.count = 0

    return invoke


def get_call_count(invoke):
    '''
    In tandem with `count_calls_decorator`, return the number of times that
    a callback was invoked.
    '''

    return invoke.count


def get_name_from_node(node):
    '''
    Return the left-most name from an Attribute or Subscript node.
    '''

    while isinstance(node, (ast.Attribute, ast.Call, ast.Subscript)):
        if isinstance(node, ast.Call):
            node = node.func
        else:
            node = node.value

    if isinstance(node, ast.Name):
        return node.id
    else:
        return None


def log(text, file_, start_line, stop_line=None):
    '''
    Display a match, including file name, line number, and code excerpt.
    '''

    print('{}: {}:{}'.format(text, file_, start_line))

    if stop_line is None:
        stop_line = start_line

    with open(file_) as source:
        print(''.join(source.readlines()[start_line-1:stop_line]))


def main():
    if len(sys.argv) < 2:
        sys.stderr.write('Usage: python3 parse.py <files>\n')
        sys.exit(1)

    def make_callback(text):
        return count_calls_decorator(
            lambda file_, start, stop: log(text, file_, start, stop)
        )

    nci_callback = make_callback('None-coalescing `if` block')
    nco_callback = make_callback('[Possible] None-coalescing `or`')
    nct_callback = make_callback('None-coalescing ternary')
    sna_callback = make_callback('Safe navigation `and`')
    sni_callback = make_callback('Safe navigation `if` block')
    snt_callback = make_callback('Safe navigation ternary')

    for file_ in sys.argv[1:]:
        with open(file_) as source:
            tree = ast.parse(source.read(), filename=file_)

            NoneCoalesceIfBlockVisitor(file_, nci_callback).visit(tree)
            NoneCoalesceOrVisitor(file_, nco_callback).visit(tree)
            NoneCoalesceTernaryVisitor(file_, nct_callback).visit(tree)
            SafeNavAndVisitor(file_, sna_callback).visit(tree)
            SafeNavIfBlockVisitor(file_, sni_callback).visit(tree)
            SafeNavTernaryVisitor(file_, snt_callback).visit(tree)

    print('Total None-coalescing `if` blocks: {}'
          .format(get_call_count(nci_callback)))

    print('Total [possible] None-coalescing `or`: {}'
          .format(get_call_count(nco_callback)))

    print('Total None-coalescing ternaries: {}'
          .format(get_call_count(nct_callback)))

    print('Total Safe navigation `and`: {}'
          .format(get_call_count(sna_callback)))

    print('Total Safe navigation `if` blocks: {}'
          .format(get_call_count(sni_callback)))

    print('Total Safe navigation ternaries: {}'
          .format(get_call_count(snt_callback)))


if __name__ == '__main__':
    main()
