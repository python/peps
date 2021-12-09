PEP: 9999
Title: Callable Type Syntax
Author: Steven Troxler <steven.troxler@gmail.com>,
        Pradeep Kumar Srinivasan <gohanpra@gmail.com>
Sponsor: TODO
Status: Draft
Type: Standards Track
Content-Type: text/x-rst
Created: xxx
Python-Version: 3.11
Post-History:

Abstract
========

This PEP introduces a concise and friendly syntax for callable types, supporting the same functionality as ``typing.Callable`` but with an arrow syntax inspired by the syntax for typed function signatures. This allows types like ``Callable[[int, str], bool]`` to be written ``(int, str) -> bool``.

The proposed syntax supports all the functionality provided by ``typing.Callable`` and ``typing.Concatenate`` and could eventually replace them entirely.


Motivation
==========


The ``Callable`` type, defined as part of PEP 484, is one of the most commonly used complex types in ``typing`` alongside ``Union`` and collection types like ``Dict`` and ``List``.


There are four major problems with the existing ``Callable`` type:
- it is verbose, particularly for more complex function signatures.
- it requires an explicit import, something we no longer require for most of the other
  very common types after PEP 604 (``|`` for ``Union`` types) and PEP 585 (generic collections)
- it does not visually represent the way function headers are written.
- it relies on two levels of nested square brackets. This can be quite hard to read,
  especially when the function arguments themselves have square brackets.

It is common for library authors to make use of untyped or partially-typed callables (e.g. ``Callable[..., Any]`) which we believe is partially a result of the existing types being hard to use. Libraries with less precise types reduce the ability of static analyzers running on downstream projects (including type checkers and security analysis tools) to find problems.

With a succinct, easy-to-use syntax, developers may be less likely to reach for poorly-typed options. Callable types may also be beginner-friendly if we make them look more like function headers, and like the arrow type syntax used by several other popular languages.

A simplified real-world example from a web server illustrates how the types can be verbose and require many levels of nested square brackets::

    from typing import Callable
    from app_logic import Response, UserSetting


    async def customize_response_for_settings(
        response: Response,
        customizer: Callable[[Response, list[UserSetting]], Awaitable[Response]]
    ) -> Response:
       ...

With our proposal, this code can be abbreviated to::

    from app_logic import Response, UserSetting

    def make_endpoint(
        response: Response,
        customizer: async (Response, list[UserSetting]) -> Response,
    ) -> Response:
        ...

This is shorter and requires fewer imports. It also has far less nesting of square brackets - only one level, as opposed to three in the original code.

Rationale
=========

The ``Callable`` type is widely used. For example, in typeshed [#typeshed-stats]_ it is the fifth most common complex type, after ``Optional``, ``Tuple``, ``Union``, and ``List``.

Most of the other commonly used types have gotten improved syntax either via PEP 604 or PEP 525.``Callable`` is used heavily enough to similarly justify a more usable syntax.

Why did we choose to support all the existing semantics of ``typing.Callable``, without adding support for new features? We looked at how frequently each feature would be useful in existing typed and untyped open-source code and determined that the vast majority of use cases are covered.

We considered adding support for named, optional, and variadic arguments but decided against including that because our analysis showed they are infrequently used. And when they are really needed, it is possible to type these using Callback Protocols [#callback-protocols]_.

See the Rejected Alternatives section for more detailed discussion about omitted features.

Specification
=============

Typing Behavior
---------------

Inside of type checkers, the new syntax should be treated with exactly the same semantics as ``typing.Callable``.

So a type checker should treat the following pairs exactly the same::

   from typing import Awaitable, Callable, Concatenate, ParamSpec, TypeVarTuple

    P = ParamSpec("P")
    Ts = = TypeVarTuple('Ts')

    f0: (int, str) -> bool
    f0: Callable[[int, str], bool]
    
    f1: (...) -> bool
    f1: Callable[..., bool]

    f2: async (str) -> str
    f2: Callable[[str], Awaitable[str]]
 
    f3: (**P) -> bool
    f3: Callable[P, bool]

    f4: (int, **P) -> bool
    f4: Callable[Concatenate[int, P], bool]
    
    f5: (*Ts) -> bool
    f5: Callable[[*Ts], bool]

    f6: (int, *Ts, str) -> bool
    f6: Callable[[int, *Ts, str], bool]

Grammar and Ast
---------------

The new syntax we’re proposing can be described by these AST changes ::

    expr = <prexisting_expr_kinds>
         | AsyncCallableType(callable_type_arguments args, expr returns)
         | CallableType(callable_type_arguments args, expr returns)
                                                                                
    callable_type_arguments = AnyArguments
                            | ArgumentsList(expr* posonlyargs)
                            | Concatenation(expr* posonlyargs, expr param_spec)


Here are our proposed changes to the [#python-grammar]_::

    expression:
        | disjunction disjunction 'else' expression
        | callable_type_expression
        | disjunction
        | lambdef

    callable_type_expression:
        | callable_type_arguments '->' expression
        | ASYNC callable_type_arguments '->' expression

    callable_type_arguments:
        | '(' '...' [','] ')'
        | '(' callable_type_positional_argument*  ')'
        | '(' callable_type_positional_argument* callable_type_param_spec ')'

    callable_type_positional_argument:
        | !’...’ expression ','
        | !’...’ expression &')'

    callable_type_param_spec:
        | '**' expression ','
        | '**' expression &')'



If PEP 646 is accepted, we intend to include support for unpacked types by modifying the grammar for ``callable_type_positional_argument`` as follows::

    callable_type_positional_argument:
        | expression ','
        | expression &')'
        | '*' expression ','
        | '*' expression &')'


Implications of the Grammar
---------------------------


Precedence of ->
‘’’’’’’’’’’’’’’’


``->`` binds less tightly than other operators, both inside types and in function signatures::

    (int) -> str | bool
    (int) -> (str | bool)


``->`` associates to the right, both inside types and in function signatures::

    (int) -> (str) -> bool
    (int) -> ((str) -> bool)

    def f() -> (int, str) -> bool: pass
    def f() -> ((int, str) -> bool): pass

    def f() -> (int) -> (str) -> bool: pass
    def f() -> ((int) -> ((str) -> bool)): pass


Because operators bind more tightly than ``->``, parentheses are required whenever an arrow type is intended to be inside an argument to an operator like ``|``::

    (int) -> bool | () -> bool    # syntax error!
    (int) -> bool | (() -> bool)  # okay


We discussed each of these behaviors and believe they are desirable:
- Union types (represented by ``A | B`` according to PEP 604) are valid in function signature returns, so we need to allow operators in the return position for consistency.
- Given that operators bind more tightly than ``->`` it is correct that a type like ```bool | () -> bool`` must be a syntax error. We should be sure the error message is clear because this may be a common mistake.
- Associating ``->`` to the right, rather than requiring explicit parentheses, is consistent with other languages like TypeScript and respects the principle that valid expressions should normally be substitutable when possible.

``async`` Keyword
‘’’’’’’’’’’’’’’’’

All of the binding rules still work for async callable types::

    (int) -> async (float) -> str | bool
    (int) -> (async (float) -> (str | bool))

    def f() -> async (int, str) -> bool: pass
    def f() -> (async (int, str) -> bool): pass

    def f() -> async (int) -> async (str) -> bool: pass
    def f() -> (async (int) -> (async (str) -> bool)): pass


Trailing Commas
‘’’’’’’’’’’’’’’

- Following the precedent of function signatures, putting a comma in an empty arguments list is illegal, ``(,) -> bool`` is a syntax error.
- Again following precedent, trailing commas are otherwise always permitted::


    ((int,) -> bool == (int) -> bool
    ((int, **P,) -> bool == (int, **P) -> bool
    ((...,) -> bool) == ((...) -> bool)
 
Allowing trailing commas also gives autoformatters more flexibility when splitting callable types across lines, which is always legal following standard python whitespace rules.


Disallowing ``...`` as an Argument Type
‘’’’’’’’’’’’’’’‘’’’’’’’’’’’’’’‘’’’’’’’’

Under normal circumstances, any valid expression is permitted where we want a type annotation and ``...`` is a valid expression. This is never semantically valid and all type checkers would reject it, but the grammar would allow it if we didn’t explicitly prevent this.

We decided that there were compelling reasons to prevent it:
- The semantics of ``(...) -> bool`` are different from ``(T) -> bool`` for any valid type T: ``(...)`` is a special form indicating ``AnyArguments`` whereas ``T`` is a type parameter in the arguments list.
- ``...`` is used as a placeholder default value to indicate an optional argument in stubs and Callback Protocols. Allowing it in the position of a type could easily lead to confusion and possibly bugs due to typos.

Since ``...`` is meaningless as a type and there are usability concerns, our grammar rules it out and the following is a syntax error::

    (int, ...) -> bool

Incompatibility with other possible uses of ``*` and ``**``
‘’’’’’’‘’’’’’’‘’’’’’’‘’’’’’’‘‘’’’’’’‘’’’’’’‘’‘’’’’’’‘’’‘’’’’

The use of ``**P`` for supporting PEP 612 ``ParamSpec`` rules out any future proposal using a bare ``**<some_type>`` to type ``kwargs``. This seems acceptable because:
- If we ever do want such a syntax, it would be clearer and to require an argument name anyway so that the type looks more similar to a function signature. In other words, if we ever support typing ``kwargs`` in callable types, we would prefer ``(int, **kwargs: str)`` rather than ``(int, **str)``.
- PEP 646 unpack syntax would rule out using ``*<some_type>`` for ``args``, and the ``kwargs`` case is similar enough that this rules out a bare ``**<some_type>` anyway.

Runtime Behavior
----------------

The precise details of runtime behavior are still under discussion.

We have a separate doc [#runtime-behavior-specification]_ with a very detailed tentative plan, which we can also use for discussion.

In short, the plan is that:
- The `__repr__` will show an arrow syntax literal.
- We will provide a new API where the runtime data structure can be accessed in the same manner as the AST data structure.
- We will ensure that we provide an API that is backward-compatible with ``typing.Callable`` and ``typing.Concatenate``, specifically the behavior of ``__args__`` and ``__parameters__``.


Rejected Alternatives
=====================

Many of the alternatives we considered would have been more expressive than ``typing.Callable``, for example adding support for describing signatures that include named, optional, and variadic arguments.

We decided on a simple proposal focused just on improving syntax for the existing ``Callable`` type based on an extensive analysis of existing projects (see [#callable-type-usage-stats]_, [#callback-usage-stats-typed]_, [#callback-usage-stats]_). We determined that the vast majority of callbacks can be correctly described by the existing ``typing.Callable`` semantics:
- Positional parameters: By far the most important case to handle well is simple callable types with positional parameters, such as ``(int, str) -> bool``
- ParamSpec and Concatenate: The next most important feature is good support for PEP 612 ``ParamSpec`` and ``Concatenate`` types like ``(**P) -> bool`` and ``(int, **P) -> bool``. These are common primarily because of the heavy use of decorator patterns in python code.
- TypeVarTuples: The next most important feature, assuming PEP 646 is accepted, is for unpacked types which are common because of cases where a wrapper passes along `*args` to some other function.

Features that other, more complicated proposals would support account for fewer than 2% of the use cases we found. These are already expressibleusing `Callback Protocols <https://www.python.org/dev/peps/pep-0544/#callback-protocols>`_, and since they aren’t common we decided that it made more sense to move forward with a simpler syntax.

Extended Syntax Supporting Named and Optional Arguments
-------------------------------------------------------

Another alternative was for a compatible but more complex syntax that could express everything in this PEP but also named, optional, and variadic arguments. In this “extended” syntax proposal the following types would have been equivalent::

    class Function(typing.Protocol):
        def f(self, x: int, /, y: float, *, z: bool = ..., **kwargs: str) -> bool:
            ...

    Function = (int, y: float, *, z: bool = ..., **kwargs: str) -> bool

Advantages of this syntax include:
- Most of the advantages of the proposal in this PEP (conciseness, PEP 612 support, etc)
- Furthermore, the ability to handle named, optional, and variadic arguments

We decided against proposing it for the following reasons:
- The implementation would have been more difficult, and usage stats demonstrate that fewer than 3% of use cases would benefit from any of the added features.
- The group that debated these proposals was split down the middle about whether these changes are even desirable:
  - On the one hand they make callable types more expressive, but on the other hand they could easily confuse users who haven’t read the full specification of callable type syntax.
  - We believe the simpler syntax proposed in this PEP, which introduces no new semantics and closely mimics syntax in other popular languages like Kotlin, Scala, and TypesScript, are much less likely to confuse users.
- We intend to implement the current proposal in a way that is forward-compatible with the more complicated extended syntax. So if the community decides after more experience and discussion that we want the additional features they should be straightforward to propose in the future.
- We realized that because of overloads, it is not possible to replace all need for Callback Protocols even with an extended syntax. This makes us prefer proposing a simple solution that handles most use cases well.

We confirmed that the current proposal is forward-compatible with extended syntax by implementing a quick-and-dirty grammar and AST on top of the grammar and AST for the current proposal [#callable-type-syntax--extended]_.


Syntax Closer to Function Signatures
------------------------------------

One alternative we had floated was a syntax much more similar to function signatures.

In this proposal, the following types would have been equivalent::

    class Function(typing.Protocol):
        def f(self, x: int, /, y: float, *, z: bool = ..., **kwargs: str) -> bool:
            ...

    Function = (x: int, /, y: float, *, z: bool = ..., **kwargs: str) -> bool


The benefits of this proposal would have included
- Perfect syntactic consistency between signatures and callable types.
- Support for more features of function signatures (named, optional, variadic args) that this PEP does not support.

Key downsides that led us to reject the idea include the following:
- A large majority of use cases only use positional-only arguments, and this syntax would be more verbose for that use case, both because of requiring argument names and an explicit ``/``, for example ``(int, /) -> bool`` where our proposal allows ``(int) -> bool``
- The requirement for explicit ``/`` for positional-only arguments has a high risk of causing frequent bugs - which often wouldn’t be detected by unit tests - where library authors would accidentally use types with named arguments.
- Our analysis suggests that support for ``ParamSpec`` is key, but the scope rules laid out in PEP 612 would have made this difficult.


Other Proposals Considered
--------------------------

An idea we looked at very early on was to allow using functions as types. This may be a great idea, but we consider less an alternative to better callable types than a major improvement in the usability of Callable Protocols:
- Using functions as types wouldn’t give us a new way of describing function types as first class values. Instead, they would require a function definition statement that effectively defines a type alias (much as a Callable Protocol class statement does).
- Functions-as-types would support almost exactly the same features that Callable Protocols do today: named, optional, and variadic args as well as the ability to define overloads.
So we think that is an idea for a related PEP, but not a direct substitute for improved Callable syntax.

We considered a parentheses-free syntax that would have been even more concise::

    int, str -> bool

We decided against it because this is not visually as similar to existing function header syntax. Moreover, it is visually similar to lambdas, which bind names with no parentheses: ``lambda x, y: x == y``.

Another idea was a new “special string” syntax an puting the type inside of it, for example ``t”(int, str) -> bool”``. We rejected this because it is not as readable, and it doesn’t seem in line with guidance from the Steering Council on ensuring that type expressions do not diverge from the rest of Python syntax. [#python-types-and-runtime-guidance]_



Backwards Compatibility
=======================

This PEP proposes a major syntax improvement over ``typing.Callable``, but the static semantics are the same.

As such, the only thing we need for backward compatibility is to ensure that types specified via the new syntax behave the same as equivalent ``typing.Callable`` and ``typing.Concatenate`` values they intend to replace.

There’s no particular interaction between this proposal and ``from __future__ import annotations`` - just like any other type annotation it will be unparsed to a string at module import, and ``typing.get_type_hints`` should correctly evaluate the resulting strings in cases where that is possible.

This is discussed in more detail in the Runtime Behavior section.


Reference Implementation
========================

We have a working implementation of the AST and Grammar [#callable-type-syntax--shorthand]_ with tests verifying that the grammar proposed here has the desired behaviors.

There is no runtime implementation yet. At a high level we are committed to the following by backward compatibility:
- We will need new object types for both the callable type and concatenation type, tentatively defined in C and exposed as ``types.CallableType`` and ``types.CallableConcatenateType`` in a manner similar to ``types.UnionType``.
- The new types must support existing ``typing.Callable`` and ``typing.Concatenate`` runtime apis almost exactly
  - The ``__repr__`` methods will differ and display the new builtin syntax
  - But the ``__args__`` and ``__parameters__`` fields must behave the same
  - And the indexing operation - which returns a new type object with concrete types substituted for various entries in ``__parameters__``, must also be the same.

We will return to more details of the runtime behavior, which remain open to discussion other than backward compatibility, in the Open Issues section below.


Open Issues
===========

Details of the Runtime API
--------------------------

The new runtime objects to which this syntax evaluates will remain backward-compatible with the ``typing.Callable`` and ``typing.Concatenate`` types they replace, other than details like ``__repr__`` where some behavior change makes sense.

But we also believe that we should have a new runtime API with more structured data access, since:
- Callable types have a more complicated shape than other generics, especially given the behavior when using ``...`` and ``typing.Concatenate``
- In the future we might want to add more features, such as support for named and optional arguments, that would be even more difficult to describe well using only ``__args__`` and ``__parameters___``.

Our tentative plan is to define enough new builtins for the runtime data to mirror the shape of the AST, but other options are also possible. See [#runtime-behavior-specification]_ for a detailed description of the current plan and a place to discuss other ideas.

Once the runtime behavior is fully defined we will add a complete evaluation model and description of behavior to this PEP.

Optimizing ``SyntaxError`` messages
-----------------------------------

The current reference implementation has a fully-functional parser and all edge cases presented here have been tested.

But there are some known cases where the errors are not as informative as we would like. For example, because ``(int, ...) -> bool`` is illegal but ``(int, ...)`` is a valid tuple, we currently produce a syntax error flagging the ``->`` as the problem even though the real cause of the error is using ``...`` as an argument type.

This is not part of the specification per se but is an important detail to add  ress in our implementation. The solution will likely involve adding ``invalid_.*`` rules to ``python.gram`` and customizing error messages.

Resources
=========

Background and History
----------------------

PEP 484 [#pep-484-function-type-hints]_ specifies a very similar syntax for function type hint *comments* for use in code that needs to work on Python 2.7, for example::

    def f(x, y):
        # type: (int, str) -> bool
        ...

At that time we used indexing operations to specify generic types like ``typing.Callable`` because we decided not to add syntax for types, but we have since begun to do so, e.g. with PEP 604

**Maggie** proposed better callable type syntax at the PyCon Typing Summit 2021: [#type-syntax-simplification]_ ([#type-variables-for-all-slides]_).

**Steven** brought up this proposal on typing-sig: [#typing-sig-thread]_.

**Pradeep** brought this proposal to python-dev for feedback: [#python-dev-thread]_.

Other Languages
---------------

Other languages use a similar arrow syntax to express callable types:
Kotlin uses ``->`` [#kotlin]_
Typescript uses ``=>`` [#typescript]_
Flow uses ``=>`` [#flow]_

Acknowledgments
---------------

Thanks to the following people for their feedback on the PEP and help planning the reference implementation:

Guido Van Rossum, Eric Traut, James Hilton-Balfe, Maggie Moss, Shannon Zhu

TODO: MAKE SURE THE THANKS STAYS UP TO DATE


References
==========

.. [#callable-type-syntax--shorthand] Reference implementation of proposed syntax: https://github.com/stroxler/cpython/tree/callable-type-syntax--shorthand

.. [#runtime-behavior-specification] Doc specifying runtime behavior of callable type builtins in detail: https://docs.google.com/document/d/15nmTDA_39Lo-EULQQwdwYx_Q1IYX4dD5WPnHbFG71Lk/edit

.. [#callable-type-syntax--extended] Bare-bones implementation of extended syntax, to demonstrate that shorthand is forward-compatible: https://github.com/stroxler/cpython/tree/callable-type-syntax--extended

.. [#ast-and-runtime-design-discussion] Detailed discussion of our reasoning around the proposed AST and runtime data structures: https://docs.google.com/document/d/1AJ0R7lgcKY0gpZbkBZRxXTvgV-OqxMYDj_JOPYMQFP8/edit

.. [#typeshed-stats] Overall type usage for typeshed: https://github.com/pradeep90/annotation_collector#overall-stats-in-typeshed

.. [#callable-type-usage-stats] Callable type usage stats: https://github.com/pradeep90/annotation_collector#typed-projects---callable-type

.. [#callback-usage-stats] Callback usage stats in open-source projects: https://github.com/pradeep90/annotation_collector#typed-projects---callback-usage

.. [#pep-484-callable] Callable type as specified in PEP 484: https://www.python.org/dev/peps/pep-0484/#callable

.. [#pep-484-function-type-hints] Function type hint comments, as outlined by PEP 484 for Python 2.7 code: https://www.python.org/dev/peps/pep-0484/#suggested-syntax-for-python-2-7-and-straddling-code

.. [#callback-protocols] Callback protocols: https://mypy.readthedocs.io/en/stable/protocols.html#callback-protocols

.. [#typing-sig-thread] Discussion of Callable syntax in the typing-sig mailing list: https://mail.python.org/archives/list/typing-sig@python.org/thread/3JNXLYH5VFPBNIVKT6FFBVVFCZO4GFR2/

.. [#callable-syntax-proposals-slides] Slides discussing potential Callable syntaxes (from 2021-09-20): https://www.dropbox.com/s/sshgtr4p30cs0vc/Python%20Callable%20Syntax%20Proposals.pdf?dl=0

.. [#python-dev-thread] Discussion of new syntax on the python-dev mailing list: https://mail.python.org/archives/list/python-dev@python.org/thread/VBHJOS3LOXGVU6I4FABM6DKHH65GGCUB/

.. [#callback-protocols] Callback protocols, as described in MyPy docs: https://mypy.readthedocs.io/en/stable/protocols.html#callback-protocols


.. [#type-syntax-simplification] Presentation on type syntax simplification from PyCon 2021: https://drive.google.com/file/d/1XhqTKoO6RHtz7zXqW5Wgq9nzaEz9TXjI/view

.. [#python-grammar] Python's PEG grammar: https://docs.python.org/3/reference/grammar.html

.. [#python-types-and-runtime-guidance] Guidance from the Steering Council on ensuring that type expressions remain consistent with the rest of the Python language: https://mail.python.org/archives/list/python-dev@python.org/message/SZLWVYV2HPLU6AH7DOUD7DWFUGBJGQAY/

.. [#callable-syntax-grammar-doc] Google doc with BNF and PEG grammar for callable type syntax: https://docs.google.com/document/d/12201yww1dBIyS6s0FwdljM-EdYr6d1YdKplWjPSt1SE/edit

.. [#kotlin] Lambdas and Callable types in Kotlin: https://kotlinlang.org/docs/lambdas.html

.. [#typescript] Callable types in TypeScript: https://basarat.gitbook.io/typescript/type-system/callable#arrow-syntax

.. [#flow] Callable types in Flow: https://flow.org/en/docs/types/functions/#toc-function-types

Copyright
=========

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.


..
   Local Variables:
   mode: indented-text
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   coding: utf-8
   End:


