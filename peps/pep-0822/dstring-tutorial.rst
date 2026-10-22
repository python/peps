.. _pep822-dstring-tutorial:

A Gentle Introduction to d-strings
==================================

This document introduces d-strings for readers who already know ordinary
triple-quoted strings, like this:

.. code-block:: python

   message = """Hello
   World!
   """

A triple-quoted string is useful when you want to write text across several
lines. The difficulty appears when that text lives inside indented Python code.

.. code-block:: python

   def make_message():
       return """Hello
   World!
   """

This produces the text you probably want, but the Python code looks awkward:
the string body is pushed all the way to the left even though it belongs inside
the function.

d-strings are designed for this situation.

The Basic Idea
--------------

A d-string is a triple-quoted string with a ``d`` prefix:

.. code-block:: python

   def make_message():
       return d"""
         Hello
         World!
         """

The ``d`` stands for "dedent". Python removes the shared indentation from the
lines in the string, so the result is:

.. code-block:: python

   "Hello\nWorld!\n"

This lets the text line up naturally with the surrounding Python code without
putting those Python indentation spaces into the final string.

The Opening Line
----------------

With an ordinary ``"""`` string, you can put text immediately after the opening
quotes:

.. code-block:: python

   s = """Hello
   World!
   """

A d-string is different. The opening quotes must be followed immediately by a
newline:

.. code-block:: python

   s = d"""
      Hello
      World!
      """

The newline right after ``d"""`` is only there to start the block. Unlike an
ordinary triple-quoted string, that first newline is not included in the final
string. The string content starts on the next line.

No Trailing Newline
-------------------

Aside from dedenting, d-strings follow the same trailing-newline behavior as
ordinary triple-quoted strings.

If you want the final string to end without a trailing newline, put the
closing quotes immediately after the last content line:

.. code-block:: python

   def label():
       return d"""
           Ready"""

Result:

.. code-block:: python

   "Ready"

If the closing quotes are on their own line, the final newline is part of the
string:

.. code-block:: python

   def label_with_newline():
       return d"""
           Ready
           """

.. code-block:: python

   "Ready\n"

How Indentation Is Removed
--------------------------

Think of a d-string as looking at the actual lines in your source file.
It finds the indentation that all non-blank lines have in common,
then removes that shared indentation.

.. code-block:: python

   def page_title():
       return d"""
           <h1>
             Welcome
           </h1>
           """

.. code-block:: python

   "<h1>\n  Welcome\n</h1>\n"

The two extra spaces before ``Welcome`` remain because they are part of the
document, not just part of the Python indentation.

Keeping Some Indentation
^^^^^^^^^^^^^^^^^^^^^^^^

The closing quote line is important. Its indentation is included when
Python decides how much indentation to remove.

You can use this behavior to preserve indentation by placing the closing quotes
farther to the left than the body.

.. code-block:: python

   def indented_list():
       return d"""
             items:
               - apples
               - bananas
           """

Here the body lines are indented more than the closing quotes. The indentation
shared with the closing quote line is removed, and the extra indentation is
preserved:

.. code-block:: python

   "  items:\n    - apples\n    - bananas\n"

This is useful when the text format itself needs indentation, such as
HTML, YAML-like examples, or generated code.

Blank Lines Become Empty Lines
------------------------------

A blank line is a line that contains only spaces, tabs, and a newline. In a
d-string, blank lines are normalized to empty lines.

.. code-block:: python

   def paragraph():
       return d"""
           First paragraph.

           Second paragraph.
           """

Even if the blank-looking line contains spaces, the result treats it as a plain
empty line:

.. code-block:: python

   "First paragraph.\n\nSecond paragraph.\n"

Blank lines do not decide how much indentation gets removed. They are simply
turned into empty lines.

Although closing quotes are considered when deciding how much indentation to
remove, the line with the closing quotes can also be normalized to an empty
string if it only has spaces before the quotes.

Escapes Are Handled After Dedent
--------------------------------

d-strings remove indentation before escape sequences are processed.

That means dedent works on the physical lines as they appear in your source
file. For example, ``\t`` in the indentation area is not treated as a tab for
dedent purposes; it is just a backslash followed by ``t`` until escapes are
processed later.

.. code-block:: python

   s = d"""
       \tName
       \tAge
       """

The four real spaces before each line are indentation and can be removed. The
``\t`` text remains in the string until escape processing turns it into tab
characters.

This rule matters most when you use a backslash at the end of a line.

Indenting Continued Lines
-------------------------

In Python strings, a backslash at the end of a line can continue the string
onto the next line:

.. code-block:: python

   def long_sentence():
       return """\
   This is a long sentence that continues \
   on the next physical line.
   """

D-string removes indentation before Python processes the line-continuation.
So you can indent continued lines in d-strings.

.. code-block:: python

   def long_sentence():
       return d"""
           This is a long sentence that continues \
           on the next physical line.
           """

There is one special rule to remember: you cannot put that continuation
backslash immediately after the opening quotes. A d-string must start with a
real newline after ``d"""``.

Combining with f/t-strings
--------------------------

d-strings can be combined with f-strings and t-strings. In those combinations,
dedent still happens first, and then f/t-string processing happens as usual.

.. code-block:: python

   def build_validation_message(user, missing_fields):
       return df"""
           Validation failed for {user}.
           Missing required fields: {", ".join(missing_fields)}.
           Please update the input and try again.
           """

.. code-block:: python

   >>> build_validation_message("Alice", ["email", "role"])
   "Validation failed for Alice.\nMissing required fields: email, role.\nPlease update the input and try again.\n"


What To Remember
----------------

- A d-string is written with ``d"""`` or ``d'''``.
- The opening quotes must be followed by a newline, and that newline is not
  included in the string.
- Blank lines are normalized to empty lines.
- The closing quote line, even if it is blank, helps decide how much
  indentation is removed.
- Put the closing quotes right after the last content line when you do not want
  a trailing newline.
- Moving the closing quotes lets you preserve some indentation in the final
  text.
- Dedent works on the physical source lines before escape sequences are
  processed.
- Continued lines ending in ``\`` can be indented naturally inside a d-string.
