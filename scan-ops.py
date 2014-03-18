#!/usr/bin/env python3
# http://legacy.python.org/dev/peps/pep-0465/
# https://gist.github.com/njsmith/9157645

# usage:
#   python3 scan-ops.py stdlib_path sklearn_path nipy_path

import sys
import os
import os.path
import tokenize
from collections import OrderedDict

NON_SOURCE_TOKENS = [
    tokenize.COMMENT, tokenize.NL, tokenize.ENCODING, tokenize.NEWLINE,
    tokenize.INDENT, tokenize.DEDENT,
    ]

SKIP_OPS = list("(),.:[]{}@;") + ["->", "..."]

class TokenCounts(object):
    def __init__(self, dot_names=[]):
        self.counts = {}
        self.sloc = 0
        self.dot_names = dot_names

    def count(self, path):
        sloc_idxes = set()
        for token in tokenize.tokenize(open(path, "rb").readline):
            if token.type == tokenize.OP:
                self.counts.setdefault(token.string, 0)
                self.counts[token.string] += 1
            if token.string in self.dot_names:
                self.counts.setdefault("dot", 0)
                self.counts["dot"] += 1
            if token.type not in NON_SOURCE_TOKENS:
                sloc_idxes.add(token.start[0])
        self.sloc += len(sloc_idxes)

    @classmethod
    def combine(cls, objs):
        combined = cls()
        for obj in objs:
            for op, count in obj.counts.items():
                combined.counts.setdefault(op, 0)
                combined.counts[op] += count
            combined.sloc += obj.sloc
        return combined

def count_tree(root, **kwargs):
    c = TokenCounts(**kwargs)
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            if filename.endswith(".py"):
                path = os.path.join(dirpath, filename)
                try:
                    c.count(path)
                    sys.stderr.write(".")
                    sys.stderr.flush()
                except Exception as e:
                    sys.stderr.write("\nFailed to read %s: %s\n" % (path, e))
    return c

# count_objs is OrderedDict (name -> TokenCounts)
def summarize(count_objs, out):
    ops = {}
    for count_obj in count_objs.values():
        for op in count_obj.counts:
            ops[op] = []
    for count_obj in count_objs.values():
        for op, row in ops.items():
            count = count_obj.counts.get(op, 0)
            row.append(count / count_obj.sloc)
    titles = ["Op"] + list(count_objs)
    # 4 chars is enough for ops and all numbers.
    column_widths = [max(len(title), 4) for title in titles]

    rows = []
    for op, row in ops.items():
        #rows.append(["``" + op + "``"] + row)
        rows.append([op] + row)

    rows.sort(key=lambda row: row[-1])
    rows.reverse()

    def write_row(entries):
        out.write("  ".join(entries))
        out.write("\n")

    def lines():
        write_row("=" * w for w in column_widths)

    lines()
    write_row(t.rjust(w) for w, t in zip(column_widths, titles))
    lines()
    for row in rows:
        op = row[0]
        if op in SKIP_OPS:
            continue
        # numbers here are avg number of uses per sloc, which is
        # inconveniently small. convert to uses/1e4 sloc
        numbers = row[1:]
        number_strs = [str(int(round(x * 10000))) for x in numbers]
        formatted_row = [op] + number_strs
        write_row(str(e).rjust(w)
                  for w, e in zip(column_widths, formatted_row))
    lines()

def run_projects(names, dot_names, dirs, out):
    assert len(names) == len(dot_names) == len(dirs)
    count_objs = OrderedDict()
    for name, dot_name, dir in zip(names, dot_names, dirs):
        counts = count_tree(dir, dot_names=dot_name)
        count_objs[name] = counts
        out.write("%s: %s sloc\n" % (name, counts.sloc))
    count_objs["combined"] = TokenCounts.combine(count_objs.values())
    summarize(count_objs, out)

if __name__ == "__main__":
    run_projects(["stdlib", "scikit-learn", "nipy"],
                 [[],
                  # https://github.com/numpy/numpy/pull/4351#discussion_r9977913
                  # sklearn fast_dot is used to fix up some optimizations that
                  # are missing from older numpy's, but in modern days is
                  # exactly the same, so it's fair to count. safe_sparse_dot
                  # has hacks to workaround some quirks in scipy.sparse
                  # matrices, but these quirks are also already fixed, so
                  # counting this calls is also fair.
                  ["dot", "fast_dot", "safe_sparse_dot"],
                  ["dot"]],
                 sys.argv[1:],
                 sys.stdout)
