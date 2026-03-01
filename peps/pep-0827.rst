PEP: 827
Title: Type Manipulation
Author: Michael J. Sullivan <sully@vercel.com>,
        Daniel W. Park <daniel.park@vercel.com>,
        Yury Selivanov <yury@vercel.com>
Discussions-To: Pending
Status: Draft
Type: Standards Track
Topic: Typing
Created: 27-Feb-2026
Python-Version: 3.15
Post-History: Pending


Abstract
========

We propose to add powerful type-level introspection and construction
facilities to the type system, inspired in large part by
TypeScript's conditional and mapped types, but adapted to the quite
different conditions of Python typing.

Motivation
==========

Python has a gradual type system, but at the heart of it is a *fairly*
conventional static type system.

In Python as a language, on the other hand, it is not unusual to
perform complex metaprogramming, especially in libraries and
frameworks. The type system typically cannot model metaprogramming.

To bridge the gap between metaprogramming and the type
system, some libraries come with custom mypy plugins.
The case of dataclass-like transformations
was considered common enough that a special-case
``@dataclass_transform`` decorator was added specifically to cover
that case (:pep:`681`). The problem with this approach is that many
typecheckers do not (and will not) have a plugin API, so having
consistent typechecking across IDEs, CI, and tooling is not
achievable.

Given the significant mismatch between the expressiveness of
the Python language and its type system, we propose to bridge
this gap by adding type manipulation facilities that
are better able to keep up with dynamic Python code.

There is demand for this. In the analysis of the
responses to Meta's `2025 Typed Python Survey <#survey_>`__, the first
entry on the list of "Most Requested Features" was:

  **Missing Features From TypeScript and Other Languages**: Many respondents
  requested features inspired by TypeScript, such as **Intersection types**
  (like the & operator), **Mapped and Conditional types**, **Utility types**
  (like Pick, Omit, keyof, and typeof), and better **Structural typing** for
  dictionaries/dicts (e.g., more flexible TypedDict or anonymous types).

We will present a few examples of problems that could be solved with
more powerful type manipulation, but the proposal is generic and will
unlock many more use cases.

Prisma-style ORMs
-----------------

`Prisma <#prisma_>`_, a popular ORM for TypeScript, allows writing
database queries in TypeScript like
(adapted from `this example <#prisma-example_>`_):

.. code-block:: typescript

  const user = await prisma.user.findMany({
    select: {
      name: true,
      email: true,
      posts: true,
    },
  });

for which the inferred type of ``user`` will be something like:

.. code-block:: typescript

    {
        email: string;
        name: string | null;
        posts: {
            id: number;
            title: string;
            content: string | null;
            authorId: number | null;
        }[];
    }[]

Here, the output type is an intersection of the existing information
about the type of ``prisma.user`` (a TypeScript type reflected from
the database ``user`` table) and the type of the argument to
the ``findMany()`` method. It returns an array of objects containing
the properties of ``user`` that were explicitly requested;
where ``posts`` is a "relation" referencing another type.

We would like to be able to do something similar in Python. Suppose
our database schema is defined in Python (or code-generated from
the database) like::

    class Comment:
        id: Property[int]
        name: Property[str]
        poster: Link[User]


    class Post:
        id: Property[int]

        title: Property[str]
        content: Property[str]

        comments: MultiLink[Comment]
        author: Link[User]


    class User:
        id: Property[int]

        name: Property[str]
        email: Property[str]
        posts: Link[Post]

So, in Python code, a call like::

    db.select(
        User,
        name=True,
        email=True,
        posts=True,
    )

would have a dynamically computed return type ``list[<User>]`` where::

    class <User>:
        name: str
        email: str
        posts: list[<Post>]

    class <Post>:
        id: int
        title: str
        content: str

Even further, an IDE could offer code completion for
all arguments of the ``db.select()`` call (matching the
actual database column names), recursively.

(Example code for implementing this :ref:`below <pep827-qb-impl>`.)


Automatically deriving FastAPI CRUD models
------------------------------------------

The `FastAPI tutorial <#fastapi-tutorial_>`_, shows how to
build CRUD endpoints for a simple ``Hero`` type.  At its heart is a
series of class definitions used both to define the database interface
and to perform validation and filtering of the data in the endpoint::

    class HeroBase(SQLModel):
        name: str = Field(index=True)
        age: int | None = Field(default=None, index=True)


    class Hero(HeroBase, table=True):
        id: int | None = Field(default=None, primary_key=True)
        secret_name: str


    class HeroPublic(HeroBase):
        id: int


    class HeroCreate(HeroBase):
        secret_name: str


    class HeroUpdate(HeroBase):
        name: str | None = None
        age: int | None = None
        secret_name: str | None = None


The ``HeroPublic`` type is used as the return type of the read
endpoint (and is validated while being output, including having extra
fields stripped), while ``HeroCreate`` and ``HeroUpdate`` serve as
input types (automatically converted from JSON and validated based on
the types, using `Pydantic <#pydantic_>`_).

Despite the multiple types and duplication here, mechanical rules
could be written for deriving these types:

* The "Public" version should include all non-"hidden" fields, and the primary key
  should be made non-optional
* "Create" should include all fields except the primary key
* "Update" should include all fields except the primary key, but they
  should all be made optional and given a default value

With the definition of appropriate helpers inside FastAPI framework,
this proposal would allow its users to write::

    class Hero(NewSQLModel, table=True):
        id: int | None = Field(default=None, primary_key=True)

        name: str = Field(index=True)
        age: int | None = Field(default=None, index=True)

        secret_name: str = Field(hidden=True)

    type HeroPublic = Public[Hero]
    type HeroCreate = Create[Hero]
    type HeroUpdate = Update[Hero]

Those types, evaluated, would look something like::

    class HeroPublic:
        id: int
        name: str
        age: int | None


    class HeroCreate:
        name: str
        age: int | None = None
        secret_name: str


    class HeroUpdate:
        name: str | None = None
        age: int | None = None
        secret_name: str | None = None


While the implementation of ``Public[]``, ``Create[]``, and ``Update[]``
computed types is relatively complex, they perform quite mechanical
operations and if included in the framework library they would significantly
reduce the boilerplate the users of FastAPI have to maintain.

A notable feature of this use case is that it **requires performing
runtime evaluation of the type annotations**. FastAPI uses the
Pydantic models to validate and convert to/from JSON for both input
and output from endpoints.

Currently it is possible to do the runtime half of this: we could write
functions that generate Pydantic models at runtime based on whatever
rules we wished. But this is unsatisfying, because we would not be
able to properly statically typecheck the functions.

(Example code for implementing this :ref:`below <pep827-fastapi-impl>`.)


dataclasses-style method generation
-----------------------------------

We would additionally like to be able to generate method signatures
based on the attributes of an object. The most well-known example of
this is generating ``__init__`` methods for dataclasses,
which we present a simplified example of.

This kind of pattern is widespread enough that :pep:`681`
was created to represent a lowest-common denominator subset of what
existing libraries do.

Making it possible for libraries to implement more of these patterns
directly in the type system will give better typing without needing
further special casing, typechecker plugins, hardcoded support, etc.

(Example code for implementing this :ref:`below <pep827-init-impl>`.)

More powerful decorator typing
------------------------------

The typing of decorator functions has long been a pain point in Python
typing. The situation was substantially improved by the introduction of
``ParamSpec`` in :pep:`612`, but a number of patterns remain
unsupported:

* Adding/removing/modifying a keyword parameter.
* Adding/removing/modifying a variable number of parameters. (Though
  ``TypeVarTuple`` is close to being able to support adding and
  removing, if multiple unpackings were to be allowed, and Pyre
  implemented a ``Map`` operator that allowed modifying multiple.)

This proposal will cover those cases.

Specification of Some Prerequisites
===================================

We have two subproposals that are necessary to get mileage out of the
main part of this proposal.


.. _pep827-unpack-kwargs:

Unpack of typevars for ``**kwargs``
-----------------------------------

A minor proposal that can probably be split off into a typing proposal
without a PEP:

Supporting ``Unpack`` of typevars for ``**kwargs``::

    def f[K: BaseTypedDict](**kwargs: Unpack[K]) -> K:
        return kwargs

Here ``BaseTypedDict`` is defined as::

    class BaseTypedDict(typing.TypedDict):
        pass

But any :class:`~typing.TypedDict` would be allowed there.

Then, if we had a call like::

    x: int
    y: list[str]
    f(x=x, y=y)

the type inferred for ``K`` would be something like::

    TypedDict({'x': int, 'y': list[str]})

This is basically a combination of
:pep:`692` "Using TypedDict for more precise ``**kwargs`` typing"
and the behavior of ``Unpack`` for ``*args``
from :pep:`646` "Variadic Generics".

When inferring types here, the type checker should **infer literal
types when possible**.  This means inferring literal types for
arguments that **do not** appear in the bound, as well as
for arguments that **do** appear in the bound as read-only.

For each non-required item in the bound that does **not** have a
matching argument provided, then if the item is read-only, it will
have its type inferred as ``Never``, to indicate that it was not
provided.  (This can only be done for read-only items, since non
read-only items are invariant.)

This is potentially moderately useful on its own but is being done to
support processing ``**kwargs`` with type level computation.


.. _pep827-extended-callables-prereq:

Extended Callables
------------------

We introduce a new extended callable proposal for expressing
arbitrarily complex callable types. The goal here is **not** to have a
new syntax to write in annotations (it's quite verbose for that), but
to provide a way of constructing the types that is amenable to
creating and introspecting callable types using the other features of
this PEP.

We introduce a ``Param`` type that contains all the information about a function param::

    class Param[N: str | None, T, Q: ParamQuals = typing.Never]:
        pass

    ParamQuals = typing.Literal["*", "**", "default", "keyword"]

    type PosParam[N: str | None, T] = Param[N, T, Literal["positional"]]
    type PosDefaultParam[N: str | None, T] = Param[N, T, Literal["positional", "default"]]
    type DefaultParam[N: str, T] = Param[N, T, Literal["default"]]
    type NamedParam[N: str, T] = Param[N, T, Literal["keyword"]]
    type NamedDefaultParam[N: str, T] = Param[N, T, Literal["keyword", "default"]]
    type ArgsParam[T] = Param[Literal[None], T, Literal["*"]]
    type KwargsParam[T] = Param[Literal[None], T, Literal["**"]]

And then, we can represent the type of a function like::

    def func(
        a: int,
        /,
        b: int,
        c: int = 0,
        *args: int,
        d: int,
        e: int = 0,
        **kwargs: int
    ) -> int:
        ...

as::

    Callable[
        [
            Param[Literal["a"], int, Literal["positional"]],
            Param[Literal["b"], int],
            Param[Literal["c"], int, Literal["default"]],
            Param[None, int, Literal["*"]],
            Param[Literal["d"], int, Literal["keyword"]],
            Param[Literal["e"], int, Literal["default", "keyword"]],
            Param[None, int, Literal["**"]],
        ],
        int,
    ]


or, using the type abbreviations we provide::

    Callable[
        [
            PosParam[Literal["a"], int],
            Param[Literal["b"], int],
            DefaultParam[Literal["c"], int],
            ArgsParam[int],
            NamedParam[Literal["d"], int],
            NamedDefaultParam[Literal["e"], int],
            KwargsParam[int],
        ],
        int,
    ]

(Rationale discussed :ref:`below <pep827-callable-rationale>`.)

Specification
=============

As was visible in the examples above, we introduce a few new syntactic
forms of valid types, but much of the power comes from type level
**operators** that will be defined in the ``typing`` module.


Grammar specification of the extensions to the type language
------------------------------------------------------------

No changes to the **Python** grammar are being proposed, only
to the grammar of what Python expressions are considered as valid types.


::

   <type> = ...
        # Type booleans are all valid types too
        | <type-bool>

        # Conditional types
        | <type> if <type-bool> else <type>

        # Types with variadic arguments can have
        # *[... for t in ...] arguments
        | <ident>[<variadic-type-arg> +]

        # Type member access
        | <type>.<name>

        | GenericCallable[<type>, lambda <args>: <type>]

   # Type conditional checks are boolean compositions of
   # boolean type operators
   <type-bool> =
         <bool-operator>[<type> +]
       | not <type-bool>
       | <type-bool> and <type-bool>
       | <type-bool> or <type-bool>
       | any(<type-bool-for>)
       | all(<type-bool-for>)

   <variadic-type-arg> =
         <type> ,
       | * [ <type-for-iter> ] ,


   <type-for> = <type> <type-for-iter>+ <type-for-if>*
   <type-for-iter> =
         # Iterate over a tuple type
         for <var> in Iter[<type>]
   <type-for-if> =
         if <type-bool>

Where:

* ``<bool-operator>`` refers to any of the names defined in the
  :ref:`Boolean Operators <pep827-boolean-ops>` section, whether used directly,
  qualified, or under another name.

* ``<type-bool-for>`` is identical to ``<type-for>`` except that the
  result type is a ``<type-bool>`` instead of a ``<type>``.

There are three and a half core syntactic features introduced: type booleans,
conditional types, unpacked comprehension types, and type member access.

:ref:`"Generic callables" <pep827-generic-callable>` are also technically a
syntactic feature, but are discussed as an operator.

Type booleans
'''''''''''''

Type booleans are a special subset of the type language that can be
used in the body of conditionals.  They consist of the :ref:`Boolean
Operators <pep827-boolean-ops>`, defined below, potentially combined with
``and``, ``or``, ``not``, ``all``, and ``any``. For ``all`` and
``any``, the argument is a comprehension of type booleans, evaluated
in the same way as the :ref:`unpacked comprehensions <pep827-unpacked>`.

When evaluated in type annotation context, they will evaluate to
``Literal[True]`` or ``Literal[False]``.

We restrict what operators may be used in a conditional
so that at runtime, we can have those operators produce "type" values
with appropriate behavior, without needing to change the behavior of
existing ``Literal[False]`` values and the like.


Conditional types
'''''''''''''''''

The type ``true_typ if bool_typ else false_typ`` is a conditional
type, which resolves to ``true_typ`` if ``bool_typ`` is equivalent to
``Literal[True]`` and to ``false_typ`` otherwise.

``bool_typ`` is a type, but it needs to syntactically be a type boolean,
defined above.

.. _pep827-unpacked:

Unpacked comprehension
''''''''''''''''''''''

An unpacked comprehension, ``*[ty for t in Iter[iter_ty]]`` may appear
anywhere in a type that ``Unpack[...]`` is currently allowed, and it
evaluates essentially to an ``Unpack`` of a tuple produced by a list
comprehension iterating over the arguments of tuple type ``iter_ty``.

The comprehension may also have ``if`` clauses, which filter in the
usual way.

Type member access
''''''''''''''''''

The ``Member`` and ``Param`` types introduced to represent class
members and function params have "associated" type members, which can
be accessed by dot notation: ``m.name``, ``m.type``, etc.

This operation is not lifted over union types. Using it on the wrong
sort of type will be an error. It must be that way at runtime,
and we want typechecking to match.


Type operators
--------------

Many of the operators specified have type bounds listed for some of
their operands. These should be interpreted more as documentation than
as exact type bounds. Trying to evaluate operators with invalid
arguments will produce ``Never`` as the return. (There is some
discussion of potential alternatives :ref:`below <pep827-strict-kinds>`.)

Note that in some of these bounds below we write things like
``Literal[int]`` to mean "a literal that is of type ``int``".
We don't propose to add that as actual syntax yet.

.. _pep827-boolean-ops:

Boolean operators
'''''''''''''''''

* ``IsAssignable[T, S]``: Returns a boolean literal type indicating whether
  ``T`` is assignable to ``S``.

  That is, it is a "consistent subtype". This is subtyping extended
  to gradual types.

* ``IsEquivalent[T, S]``:
  Equivalent to ``IsAssignable[T, S] and IsAssignable[S, T]``.
  Technically this relation is "consistency" in the typing spec, not
  equivalence.

* ``Bool[T]``: Returns ``Literal[True]`` if ``T`` is also
  ``Literal[True]`` or a union containing it.
  Equivalent to ``IsAssignable[T, Literal[True]] and not IsAssignable[T, Never]``.

  This is useful for invoking "helper aliases" that return a boolean
  literal type.

Basic operators
'''''''''''''''

* ``GetArg[T, Base, Idx: Literal[int]]``: returns the type argument
  number ``Idx`` to ``T`` when interpreted as ``Base``, or ``Never``
  if it cannot be. (That is, if we have ``class A(B[C]): ...``, then
  ``GetArg[A, B, Literal[0]] == C``
  while ``GetArg[A, A, Literal[0]] == Never``).

  Negative indexes work in the usual way.

  Note that runtime evaluation will only be able to support proper classes
  as ``Base``, *not* protocols. So, for example, ``GetArg[Ty,
  Iterable, Literal[0]]`` to get the type of something iterable will
  fail in the runtime evaluator.

  Special forms require special handling: the arguments list of a ``Callable``
  will be packed in a tuple, and a ``...`` will become
  ``SpecialFormEllipsis``.

* ``GetArgs[T, Base]``: returns a tuple containing all of the type
  arguments of ``T`` when interpreted as ``Base``, or ``Never`` if it
  cannot be.

* ``GetMemberType[T, S: Literal[str]]``: Extract the type of the
  member named ``S`` from the class ``T``.

* ``Length[T: tuple]`` - Gets the length of a tuple as an int literal
  (or ``Literal[None]`` if it is unbounded)

* ``Slice[S: tuple, Start: Literal[int | None], End: Literal[int | None]]``:
  Slices a tuple type.

* ``GetSpecialAttr[T, Attr: Literal[str]]``: Extracts the value
  of the special attribute named ``Attr`` from the class ``T``. Valid
  attributes are ``__name__``, ``__module__``, and ``__qualname__``.
  Returns the value as a ``Literal[str]``.

All of the operators in this section are :ref:`lifted over union types
<pep827-lifting>`.

Union processing
''''''''''''''''

* ``FromUnion[T]``: Returns a tuple containing all of the union
  elements, or a 1-ary tuple containing T if it is not a union.

* ``Union[*Ts]``: ``Union`` will become able to take variadic
  arguments, so that it can take unpacked comprehension arguments.


Object inspection
'''''''''''''''''

* ``Members[T]``: produces a ``tuple`` of ``Member`` types describing
  the members (attributes and methods) of class or typed dict ``T``.

  In order to allow typechecking time and runtime evaluation to coincide
  more closely, **only members with explicit type annotations are included**.

* ``Attrs[T]``: like ``Members[T]`` but only returns attributes (not
  methods).

* ``GetMember[T, S: Literal[str]]``: Produces a ``Member`` type for the
  member named ``S`` from the class ``T``.

* ``Member[N: Literal[str], T, Q: MemberQuals, Init, D]``: ``Member``,
  is a simple type, not an operator, that is used to describe members
  of classes.  Its type parameters encode the information about each
  member.

  * ``N`` is the name, as a literal string type. Accessible with ``.name``.
  * ``T`` is the type. Accessible with ``.type``.
  * ``Q`` is a union of qualifiers (see ``MemberQuals`` below). Accessible with ``.quals``.
  * ``Init`` is the literal type of the attribute initializer in the
    class (see :ref:`InitField <pep827-init-field>`). Accessible with ``.init``.
  * ``D`` is the defining class of the member. (That is, which class
    the member is inherited from. Always ``Never``, for a ``TypedDict``).
    Accessible with ``.definer``.

* ``MemberQuals = Literal['ClassVar', 'Final', 'NotRequired', 'ReadOnly']`` -
  ``MemberQuals`` is the type of "qualifiers" that can apply to a
  member; currently ``ClassVar`` and ``Final`` apply to classes, and
  ``NotRequired`` and ``ReadOnly`` apply to typed dicts.


Methods are returned as callables using the new ``Param`` based
extended callables, and carrying the ``ClassVar``
qualifier. ``staticmethod`` and ``classmethod`` will return
``staticmethod`` and ``classmethod`` types, which are subscriptable as
of Python 3.14.

All of the operators in this section are :ref:`lifted over union types
<pep827-lifting>`.

Object creation
'''''''''''''''

* ``NewProtocol[*Ms: Member]``: Create a new structural protocol with members
  specified by ``Member`` arguments

* ``NewTypedDict[*Ps: Member]`` - Creates a new ``TypedDict`` with
  items specified by the ``Member`` arguments.

Note that we are not currently proposing any way to create *nominal* classes
or any way to make new *generic* types.


.. _pep827-init-field:

InitField
'''''''''

We want to be able to support transforming types based on
dataclasses/attrs/Pydantic-style field descriptors.  In order to do
that, we need to be able to consume operations like calls to ``Field``.

Our strategy for this is to introduce a new type
``InitField[KwargDict]`` that collects arguments defined by a
``KwargDict: TypedDict``::

  class InitField[KwargDict: BaseTypedDict]:
      def __init__(self, **kwargs: typing.Unpack[KwargDict]) -> None:
          ...

      def _get_kwargs(self) -> KwargDict:
          ...

When ``InitField`` or (more likely) a subtype of it is instantiated
inside a class body, we infer a *more specific* type for it, based on
``Literal`` types where possible. (Though actually, this is just an
application of the rule that typevar unpacking in ``**kwargs`` should
use ``Literal`` types.)

So if we write::

  class A:
      foo: int = InitField(default=0, kw_only=True)

then we would infer the type ``InitField[TypedDict('...', {'default':
Literal[0], 'kw_only': Literal[True]})]`` for the initializer, and
that would be made available as the ``Init`` field of the ``Member``.


Callable inspection and creation
''''''''''''''''''''''''''''''''

``Callable`` types always have their arguments exposed in the extended
Callable format discussed above.

The names, type, and qualifiers share associated type names with
``Member`` (``.name``, ``.type``, and ``.quals``).

.. _pep827-generic-callable:

Generic Callable
''''''''''''''''

* ``GenericCallable[Vs, lambda <vs>: Ty]``: A generic callable. ``Vs``
  are a tuple type of unbound type variables and ``Ty`` should be a
  ``Callable``, ``staticmethod``, or ``classmethod`` that has access
  to the variables in ``Vs`` via the bound variables in ``<vs>``.

For now, we restrict the use of ``GenericCallable`` to
the type argument of ``Member``, to disallow its use for
locals, parameter types, return types, nested inside other types,
etc.  Rationale discussed :ref:`below <pep827-generic-callable-rationale>`.

Overloaded function types
'''''''''''''''''''''''''

* ``Overloaded[*Callables]`` - An overloaded function type, with the
  underlying types in order.


Raise error
'''''''''''

* ``RaiseError[S: Literal[str], *Ts]``: If this type needs to be evaluated
  to determine some actual type, generate a type error with the
  provided message.

  Any additional type arguments should be included in the message.

.. _pep827-update-class:

Update class
''''''''''''

* ``UpdateClass[*Ps: Member]``: A special form that *updates* an
  existing nominal class with new members (possibly overriding old
  ones, or removing them by making them have type ``Never``).

  This can only be used in the return type of a type decorator
  or as the return type of ``__init_subclass__``.

  When a class is declared, if one or more of its ancestors have an
  ``__init_subclass__`` with an ``UpdateClass`` return type, they are
  applied in reverse MRO order. N.B: If the ``cls`` param is
  parameterized by ``type[T]``, then the class type should be
  substituted in for ``T``.

.. _pep827-lifting:

Lifting over Unions
-------------------

Many of the builtin operations are "lifted" over ``Union``.

For example::

    Concat[Literal['a'] | Literal['b'], Literal['c'] | Literal['d']] = (
        Literal['ac'] | Literal['ad'] | Literal['bc'] | Literal['bd']
    )


When an operation is lifted over union types, we take the cross
product of the union elements for each argument position, evaluate the
operator for each tuple in the cross product, and then union all of
the results together. In Python, the logic looks like::

    args_union_els = [get_union_elems(arg) for arg in args]
    results = [
        eval_operator(*xs)
        for xs in itertools.product(*args_union_els)
    ]
    if results:
        return Union[*results]
    else:
        return Never


.. _pep827-rt-support:

Runtime evaluation support
--------------------------

An important goal is supporting runtime evaluation of these computed
types.  We **do not** propose to add an official evaluator to the standard
library, but intend to release a third-party evaluator library.

While most of the extensions to the type system are "inert" type
operator applications, the syntax also includes list iteration,
conditionals, and attribute access, which will be automatically
evaluated when the ``__annotate__`` method of a class, alias, or
function is called.

In order to allow an evaluator library to trigger type evaluation in
those cases, we add a new hook to ``typing``:

* ``special_form_evaluator``: This is a ``ContextVar`` that holds a
  callable that will be invoked with a ``typing._GenericAlias``
  argument when ``__bool__`` is called on a
  :ref:`Boolean Operator <pep827-boolean-ops>` or ``__iter__`` is called
  on ``typing.Iter``.
  The returned value will then have ``bool`` or ``iter`` called upon
  it before being returned.

  If set to ``None`` (the default), the boolean operators will return
  ``False`` while ``Iter`` will evaluate to ``iter(())``.


There has been some discussion of adding a ``Format.AST`` mode for
fetching annotations (see this `PEP draft <#ast_format_>`_). That
would combine extremely well with this proposal, as it would make it
easy to still fetch fully unevaluated annotations.

Examples / Tutorial
===================

Here we will take something of a tutorial approach in discussing how
to achieve the goals in the examples in the motivation section,
explain the features being used as we use them.

.. _pep827-qb-impl:

Prisma-style ORMs
-----------------

First, to support the annotations we saw above, we have a collection
of dummy classes with generic types.

::

    class Pointer[T]:
        pass

    class Property[T](Pointer[T]):
        pass

    class Link[T](Pointer[T]):
        pass

    class SingleLink[T](Link[T]):
        pass

    class MultiLink[T](Link[T]):
        pass

The ``select`` method is where we start seeing new things.

The ``**kwargs: Unpack[K]`` is part of this proposal, and allows
*inferring* a TypedDict from keyword args.

``Attrs[K]`` extracts ``Member`` types corresponding to every
type-annotated attribute of ``K``, while calling ``NewProtocol`` with
``Member`` arguments constructs a new structural type.

``c.name`` fetches the name of the ``Member`` bound to the variable ``c``
as a literal type--all of these mechanisms lean very heavily on literal types.
``GetMemberType`` gets the type of an attribute from a class.

::

    def select[ModelT, K: typing.BaseTypedDict](
        typ: type[ModelT],
        /,
        **kwargs: Unpack[K],
    ) -> list[
        typing.NewProtocol[
            *[
                typing.Member[
                    c.name,
                    ConvertField[typing.GetMemberType[ModelT, c.name]],
                ]
                for c in typing.Iter[typing.Attrs[K]]
            ]
        ]
    ]:
        raise NotImplementedError

``ConvertField`` is our first type helper, and it is a conditional type
alias, which decides between two types based on a (limited)
subtype-ish check.

In ``ConvertField``, we wish to drop the ``Property`` or ``Link``
annotation and produce the underlying type, as well as, for links,
producing a new target type containing only properties and wrapping
``MultiLink`` in a list.

::

    type ConvertField[T] = (
        AdjustLink[PropsOnly[PointerArg[T]], T]
        if typing.IsAssignable[T, Link]
        else PointerArg[T]
    )

``PointerArg`` gets the type argument to ``Pointer`` or a subclass.

``GetArg[T, Base, I]`` is one of the core primitives; it fetches the
index ``I`` type argument to ``Base`` from a type ``T``, if ``T``
inherits from ``Base``.

(The subtleties of this will be discussed later; in this case, it just
grabs the argument to a ``Pointer``).

::

    type PointerArg[T] = typing.GetArg[T, Pointer, Literal[0]]

``AdjustLink`` sticks a ``list`` around ``MultiLink``, using features
we've discussed already.

::

    type AdjustLink[Tgt, LinkTy] = (
        list[Tgt] if typing.IsAssignable[LinkTy, MultiLink] else Tgt
    )

And the final helper, ``PropsOnly[T]``, generates a new type that
contains all the ``Property`` attributes of ``T``.

::

    type PropsOnly[T] = typing.NewProtocol[
        *[
            typing.Member[p.name, PointerArg[p.type]]
            for p in typing.Iter[typing.Attrs[T]]
            if typing.IsAssignable[p.type, Property]
        ]
    ]

The full test is `in our test suite <#qb-test_>`_.


.. _pep827-fastapi-impl:

Automatically deriving FastAPI CRUD models
------------------------------------------

We have a more `fully-worked example <#fastapi-test_>`_ in our test
suite, but here is a possible implementation of just ``Create``::

    # Extract the default type from an Init field.
    # If it is a Field, then we try pulling out the "default" field,
    # otherwise we return the type itself.
    type GetDefault[Init] = (
        GetFieldItem[Init, Literal["default"]]
        if typing.IsAssignable[Init, Field]
        else Init
    )

    # Create takes everything but the primary key and preserves defaults
    type Create[T] = typing.NewProtocol[
        *[
            typing.Member[
                p.name,
                p.type,
                p.quals,
                GetDefault[p.init],
            ]
            for p in typing.Iter[typing.Attrs[T]]
            if not typing.IsAssignable[
                Literal[True],
                GetFieldItem[p.init, Literal["primary_key"]],
            ]
        ]
    ]

The ``Create`` type alias creates a new type (via ``NewProtocol``) by
iterating over the attributes of the original type.  It has access to
names, types, qualifiers, and the literal types of initializers (in
part through new facilities to handle the extremely common
``= Field(...)``-like pattern used here).

Here, we filter out attributes that have ``primary_key=True`` in their
``Field`` as well as extracting default arguments (which may be either
from a ``default`` argument to a field or specified directly as an
initializer).


.. _pep827-init-impl:

dataclasses-style method generation
-----------------------------------

``InitFnType`` generates a ``Member`` for a new ``__init__`` function
based on iterating over all attributes.

``GetDefault`` here is borrowed from our FastAPI-like example above.

::

    # Generate the Member field for __init__ for a class
    type InitFnType[T] = typing.Member[
        Literal["__init__"],
        Callable[
            [
                typing.Param[Literal["self"], Self],
                *[
                    typing.Param[
                        p.name,
                        p.type,
                        # All arguments are keyword-only
                        # It takes a default if a default is specified in the class
                        Literal["keyword"]
                        if typing.IsAssignable[
                            GetDefault[p.init],
                            Never,
                        ]
                        else Literal["keyword", "default"],
                    ]
                    for p in typing.Iter[typing.Attrs[T]]
                ],
            ],
            None,
        ],
        Literal["ClassVar"],
    ]
    type AddInit[T] = typing.NewProtocol[
        InitFnType[T],
        *[x for x in typing.Iter[typing.Members[T]]],
    ]

``UpdateClass`` can then be used to create a class decorator (a la
``@dataclass``) adds a new ``__init__`` method to a class.

::

    def dataclass_ish[T](
        cls: type[T],
    ) -> typing.UpdateClass[
        # Add the computed __init__ function
        InitFnType[T],
    ]:
        pass

Or to create a base class (a la Pydantic) that does.

::

    class Model:
        def __init_subclass__[T](
            cls: type[T],
        ) -> typing.UpdateClass[
            # Add the computed __init__ function
            InitFnType[T],
        ]:
            super().__init_subclass__()


NumPy-style broadcasting
------------------------

One of the motivations for the introduction of ``TypeVarTuple`` in
:pep:`646` is to represent the shapes of multi-dimensional
arrays, such as::

  x: Array[float, L[480], L[640]] = Array()

The example in that PEP shows how ``TypeVarTuple`` can be used to
make sure that both sides of an arithmetic operation have matching
shapes. Most multi-dimensional array libraries, however, also support
`broadcasting <#broadcasting_>`__, which allows the mixing of differently
shaped data.  With this PEP, we can define a ``Broadcast[A, B]`` type
alias, and then use it as a return type::

    class Array[DType, *Shape]:
        def __add__[*Shape2](
            self,
            other: Array[DType, *Shape2]
        ) -> Array[DType, *Broadcast[tuple[*Shape], tuple[*Shape2]]]:
            raise BaseException

(The somewhat clunky syntax of wrapping the ``TypeVarTuple`` in
another ``tuple`` is because typecheckers currently disallow having
two ``TypeVarTuple`` arguments. A possible improvement would be to
allow writing the bare (non-starred or ``Unpack``-ed) variable name to
mean its interpretation as a tuple.)

We can then do::

    a1: Array[float, L[4], L[1]]
    a2: Array[float, L[3]]
    a1 + a2  # Array[builtins.float, Literal[4], Literal[3]]

    b1: Array[float, int, int]
    b2: Array[float, int]
    b1 + b2  # Array[builtins.float, int, int]

    err1: Array[float, L[4], L[2]]
    err2: Array[float, L[3]]
    # err1 + err2  # E: Broadcast mismatch: Literal[2], Literal[3]


Note that this is meant to be an example of the expressiveness of type
manipulation, and not any kind of final proposal about the typing of
tensor types.

.. _pep827-numpy-impl:

Implementation
''''''''''''''

::

    class Array[DType, *Shape]:
        def __add__[*Shape2](
            self, other: Array[DType, *Shape2]
        ) -> Array[DType, *Broadcast[tuple[*Shape], tuple[*Shape2]]]:
            raise BaseException

``MergeOne`` is the core of the broadcasting operation. If the two types
are equivalent, we take the first, and if either of the types is
``Literal[1]`` then we take the other.

On a mismatch, we use the ``RaiseError`` operator to produce an error
message identifying the two types.

::

    type MergeOne[T, S] = (
        T
        if typing.IsEquivalent[T, S] or typing.IsEquivalent[S, Literal[1]]
        else S
        if typing.IsEquivalent[T, Literal[1]]
        else typing.RaiseError[Literal["Broadcast mismatch"], T, S]
    )

    type DropLast[T] = typing.Slice[T, Literal[0], Literal[-1]]
    type Last[T] = typing.GetArg[T, tuple, Literal[-1]]

    # Matching on Never here is intentional; it prevents infinite
    # recursions when T is not a tuple.
    type Empty[T] = typing.IsAssignable[typing.Length[T], Literal[0]]

Broadcast recursively walks down the input tuples applying ``MergeOne``
until one of them is empty.

::

    type Broadcast[T, S] = (
        S
        if typing.Bool[Empty[T]]
        else T
        if typing.Bool[Empty[S]]
        else tuple[
            *Broadcast[DropLast[T], DropLast[S]],
            MergeOne[Last[T], Last[S]],
        ]
    )


Rationale
=========

.. _pep827-callable-rationale:

Extended Callables
------------------

We need extended callable support, in order to inspect and produce
callables via type-level computation. mypy supports `extended
callables
<https://mypy.readthedocs.io/en/stable/additional_features.html#extended-callable-types>`__
but they are deprecated in favor of callback protocols.

Unfortunately callback protocols don't work well for type level
computation. (They probably could be made to work, but it would
require a separate facility for creating and introspecting *methods*,
which wouldn't be any simpler.)

We are proposing a fully new extended callable syntax because:
 1. The ``mypy_extensions`` functions are full no-ops, and we need
    real runtime objects.
 2. They use parentheses and not brackets, which really goes against
    the philosophy here.
 3. We can make an API that more nicely matches what we are going to
    do for inspecting members (we could introduce extended callables that
    closely mimic the ``mypy_extensions`` version though, if something new
    is a non-starter).

.. _pep827-generic-callable-rationale:

Generic Callable
----------------

Consider a method with the following signature::

    def process[T](self, x: T) -> T if IsAssignable[T, list] else list[T]:
        ...

The type of the method is generic, and the generic is bound at the
**method**, not the class. We need a way to represent such a generic
function as a programmer might write it for a ``NewProtocol``.

One option that is somewhat appealing but doesn't work would be to use
unbound type variables and let them be generalized::

    type Foo = NewProtocol[
        Member[
            Literal["process"],
            Callable[[T], set[T] if IsAssignable[T, int] else T]
        ]
    ]

The problem is that this is basically incompatible with runtime
evaluation support, since evaluating the alias ``Foo`` will need to
evaluate the ``IsAssignable``, and so we will lose one side of the
conditional at least.  Similar problems will happen when evaluating
``Members`` on a class with generic functions.  By wrapping the body
in a lambda, we can delay evaluation in both of these cases.  (The
``Members`` case of delaying evaluation works quite nicely for
functions with explicit generic annotations. For old-style generics,
we'll probably have to try to evaluate it and then raise an error when
we encounter a variable.)

The reason we suggest restricting the use of ``GenericCallable`` to
the type argument of ``Member`` is because impredicative
polymorphism (where you can instantiate type variables with other
generic types) and rank-N types (where generics can be bound in nested
positions deep inside function types) are cans of worms when combined
with type inference [#undecidable]_.  While it would be nice to support,
we don't want to open that can of worms now.

The unbound type variable tuple is so that bounds and defaults and
``TypeVarTuple``-ness can be specified, though maybe we want to come
up with a new approach.


Backwards Compatibility
=======================

In the most strict sense, this PEP only proposes new features, and so
shouldn't have backward compatibility issues.

More loosely speaking, though, the use of ``if`` and ``for`` in type
annotations can cause trouble for tools that want to extract type
annotations.

Tools that want to fully evaluate the annotations will need to either
implement an evaluator or use a library for it (the PEP authors are
planning to produce such a library).

Tools that specifically rely on introspecting annotations at runtime
(tools that parse Python files are obviously unaffected) that want
to extract the annotations unevaluated and process them in some way are
possibly in more trouble. Currently, this is
doable if ``from __future__ import annotations`` is specified, because
the string annotation could be parsed with ``ast.parse`` and then handled
in arbitrary ways.

Absent that, as things currently stand, things get trickier, since
there is currently no way to get useful info out of the
``__annotate__`` functions without running the annotation, and its
tricks for building a string do not work for loops and
conditionals.

This could be mitigated by doing one of:
 1. The :pep:`"Just store the strings" <649#just-store-the-strings>`
    option from :pep:`649`, which would allow always extracting
    unevaluated strings.
 2. Adding a ``Format.AST`` mode for
    fetching annotations (see this `PEP draft <#ast_format_>`_)

If neither of those options is taken, then tools that want to process
unevaluated type manipulation expressions will probably need to
reparse the source code and extract annotations from there. Which we
expect is what most tools do anyway.


Security Implications
=====================

None are expected.


How to Teach This
=================

We think much inspiration can be taken from how TypeScript teaches
their equivalent features, since they have similar complexity.  We
will want high-level example-driven documentation, similar to what
TypeScript does.

It is also important to note that the expected audience that will use
the new syntax and APIs are framework and library maintainers who
will be impementing type manipulation to support the advanced patterns
and APIs they introduce.


Reference Implementation
========================

There is a `demo of a runtime evaluator <#runtime_>`__, which is
also where this PEP draft currently lives.

There is an in-progress `proof-of-concept implementation <#ref-impl_>`__ in mypy.

It can type check the ORM, FastAPI-style model derivation, and
NumPy-style broadcasting examples.

It is missing support for callables, ``UpdateClass``, annotation
processing, and various smaller things.

Alternate syntax ideas
======================

AKA '"Rejected" Ideas That Maybe We Should Actually Do?'

Very interested in feedback about these!

Dictionary comprehension based syntax for creating typed dicts and protocols
----------------------------------------------------------------------------

This is in some ways an extension of the :pep:`764` (still draft)
proposal for inline typed dictionaries.

Combined with the above proposal, using it for ``NewProtocol`` might
look (using something from :ref:`the query builder example <pep827-qb-impl>`)
something like:

::

    type PropsOnly[T] = typing.NewProtocol[
        {
            p.name: PointerArg[p.type]
            for p in typing.Iter[typing.Attrs[T]]
            if typing.IsAssignable[p.type, Property]
        }
    ]

Then we would probably also want to allow specifying a ``Member`` (but
reordered so that ``Name`` is last and has a default), for if we want
to specify qualifiers and/or an initializer type.

We could also potentially allow qualifiers to be written in the type,
though it is a little odd, since that is an annotation expression, not
a type expression, and you probably *wouldn't* be allowed to have an
annotation expression in an arm of a conditional type?

The main downside of this proposal is just complexity: it requires
introducing another kind of weird type form.

We'd also need to figure out the exact interaction between TypedDicts
and new protocols. Would the dictionary syntax always produce a typed
dict, and then ``NewProtocol`` converts it to a protocol, or would
``NewProtocol[<dict type expr>]`` be a special form? Would we try to
allow ``ClassVar`` and ``Final``?

Destructuring?
''''''''''''''

The other potential "downside" (which might really be an upside!) is
that it suggests that we might want to be able to iterate over
``Attrs`` and ``Members`` with an ``items()`` style iterator, and that
raises more complicated questions.

First, the syntax would be something like::

    type PropsOnly[T] = typing.NewProtocol[
        {
            k: PointerArg[ty]
            for k, ty in typing.IterItems[typing.Attrs[T]]
            if typing.IsAssignable[ty, Property]
        }
    ]

This is looking pretty nice, but we only have access to the name and
the type, not the qualifiers or the initializers.

Potential options for dealing with this:

* It is fine, programmers can use this ``.items()`` style
  iterator for common cases and operate on full ``Member`` objects
  when they need to.
* We can put the qualifiers/initializer in the ``key``? Actually using
  the name would then require doing ``key.name`` or similar.

(We'd also need to figure out exactly what the rules are for what can
be iterated over this way.)

Call type operators using parens
--------------------------------

If people are having a bad time in Bracket City, we could also
consider making the built-in type operators use parens instead of
brackets.

Using a mix of ``[]`` and ``()`` would introduce consistency issues and
will force users to remember which APIs use square brackets and which
use parentheses. Given that the current Python typing revolves around
using brackets we feel strongly that continuing on that path will lead
to a better developer experience.

As an example, here is how mixing ``()`` and ``[]`` could look like::

    type PropsOnly[T] = typing.NewProtocol(
        {
            p.name: PointerArg[p.type]
            for p in typing.Iter(typing.Attrs(T))
            if typing.IsAssignable(p.type, Property)
        }
    )

(The user-defined type alias ``PointerArg`` still must be called with
brackets, despite being basically a helper operator.)

Have a general mechanism for dot-notation accessible associated types
---------------------------------------------------------------------

The main proposal is currently silent about exactly *how* ``Member``
and ``Param`` will have associated types for ``.name`` and ``.type``.

We could just make it work for those particular types, or we could
introduce a general mechanism that might look something like::

    @typing.has_associated_types
    class Member[
        N: str,
        T,
        Q: MemberQuals = typing.Never,
        I = typing.Never,
        D = typing.Never
    ]:
        type name = N
        type tp = T
        type quals = Q
        type init = I
        type definer = D


The decorator (or a base class) is needed if we want the dot notation
for the associated types to be able to work at runtime, since we need
to customize the behavior of ``__getattr__`` on the
``typing._GenericAlias`` produced by the class so that it captures
both the type parameters to ``Member`` and the alias.

(Though possibly we could change the behavior of ``_GenericAlias``
itself to avoid the need for that.)

Rejected Ideas
==============

Renounce all cares of runtime evaluation
----------------------------------------

This would give us more flexibility to experiment with syntactic
forms, and would allow us to dispense with some ugliness such as
requiring ``typing.Iter`` in unpacked comprehension types and having a
limited set of ``<type-bool>`` expressions that can appear in
conditional types.

For better or worse, though, runtime use of type annotations is
widespread, e.g. ``pydantic`` depends on it, and one of our motivating
examples (automatically deriving FastAPI CRUD models) depends on it too.

Support TypeScript style pattern matching in subtype checking
-------------------------------------------------------------

In TypeScript, conditional types are formed like::

    SomeType extends OtherType ? TrueType : FalseType

What's more, the right-hand side of the check allows binding type
variables based on pattern matching, using the ``infer`` keyword, like
this example that extracts the element type of an array::

    type ArrayArg<T> = T extends [infer El] ? El : never;

This is a very elegant mechanism, especially in the way that it
eliminates the need for ``typing.GetArg`` and its subtle ``Base``
parameter.

Unfortunately it seems very difficult to shoehorn into Python's
existing syntax in any sort of satisfactory way, especially because of
the subtle binding structure.

Perhaps the most plausible variant would be something like::

    type ArrayArg[T] = El if IsAssignable[T, list[Infer[El]]] else Never

Then, if we wanted to evaluate it at runtime, we'd need to do
something gnarly involving a custom ``globals`` environment that
catches the unbound ``Infer`` arguments.

Additionally, without major syntactic changes (using type operators
instead of ternary), we wouldn't be able to match TypeScript's
behavior of lifting the conditional over unions.


Replace ``IsAssignable`` with something weaker than "assignable to" checking
----------------------------------------------------------------------------

Full Python typing assignability checking is not fully implementable
at runtime (in particular, even if all the typeshed types for the
stdlib were made available, checking against protocols will often not
be possible, because class attributes may be inferred and have no visible
presence at runtime).

As proposed, a runtime evaluator will need to be "best effort",
ideally with the contours of that effort well-documented.

An alternative approach would be to have a weaker predicate as the
core primitive.

One possibility would be a "sub-similarity" check: ``IsAssignableSimilar``
would do *simple* checking of the *head* of types, essentially,
without looking at type parameters. It would not work with protocols.
It would still lift over unions and would check literals.

We decided it probably was not a good idea to introduce a new notion
that is similar to but not the same as subtyping, and that would need
to either have a long and weird name like ``IsAssignableSimilar`` or a
misleading short one like ``IsAssignable``.


Don't use dot notation to access ``Member`` components
------------------------------------------------------

Earlier versions of this PEP draft omitted the ability to write
``m.name`` and similar on ``Member`` and ``Param`` components, and
instead relied on helper operators such as ``typing.GetName`` (that
could be implemented under the hood using ``typing.GetArg`` or
``typing.GetMemberType``).

The potential advantage here is reducing the number of new constructs
being added to the type language, and avoiding needing to either
introduce a new general mechanism for associated types or having a
special-case for ``Member``.

``PropsOnly`` (from :ref:`the query builder example <pep827-qb-impl>`) would
look like::

    type PropsOnly[T] = typing.NewProtocol[
        *[
            typing.Member[typing.GetName[p], PointerArg[typing.GetType[p]]]
            for p in typing.Iter[typing.Attrs[T]]
            if typing.IsAssignable[typing.GetType[p], Property]
        ]
    ]

.. _pep827-less_syntax:


Use type operators for conditional and iteration
------------------------------------------------

Instead of writing:
 * ``tt if tb else tf``
 * ``*[tres for T in Iter[ttuple]]``

we could use type operator forms like:
 * ``Cond[tb, tt, tf]``
 * ``UnpackMap[ttuple, lambda T: tres]``
 * or ``UnpackMap[ttuple, T, tres]`` where ``T`` must be a declared
   ``TypeVar``

Boolean operations would likewise become operators (``Not``, ``And``,
etc).

The advantage of this is that constructing a type annotation never
needs to do non-trivial computation (assuming we also get rid of dot
notation), and thus we don't need :ref:`runtime hooks <pep827-rt-support>` to
support evaluating them.

It would also mean that it would be much easier to extract the raw
type annotation.  (The lambda form would still be somewhat fiddly.
The non-lambda form would be trivial to extract, but requiring the
declaration of a ``TypeVar`` goes against the grain of recent
changes.)

Another advantage is not needing any notion of a special
``<type-bool>`` class of types.

The disadvantage is that the syntax seems a *lot*
worse. Supporting filtering while mapping would make it even more bad
(maybe an extra argument for a filter?)

We can explore other options too if needed.

Perform type manipulations with normal Python functions
-------------------------------------------------------

One suggestion has been, instead of defining a new type language
fragment for type-level manipulations, to support calling (some subset
of) Python functions that serve as kind-of "mini-mypy-plugins".

The main advantage (in our view) here would be leveraging a more
familiar execution model.

One suggested advantage is that it would be a simplification of the
proposal, but we feel that the simplifications promised by the idea
are mostly a mirage, and that calling Python functions to manipulate
types would be quite a bit *more* complicated.

It would require a well-defined and safe-to-run subset of the language
(and standard library) to be defined that could be run from within
typecheckers. Subsets like this have been defined in other systems
(see `Starlark <#starlark_>`_, the configuration language for Bazel),
but it's still a lot of surface area, and programmers would need to
keep in mind its boundaries.

Additionally there would need to be a clear specification of how types
are represented in the "mini-plugin" functions, as well as defining
functions/methods for performing various manipulations. Those
functions would have a pretty big overlap with what this PEP currently
proposes.

If runtime use is desired, then either the type representation would
need to be made compatible with how ``typing`` currently works or we'd
need to have two different runtime type representations.

Whether it would improve the syntax is more up for debate; we think
that adopting some of the syntactic cleanup ideas discussed above (but
not yet integrated into the main proposal) would improve the syntactic
situation at lower cost.


.. _pep827-strict-kinds:

Make the type-level operations more "strictly-typed"
----------------------------------------------------

This proposal is less "strictly-typed" than TypeScript
(strictly-kinded, maybe?).

TypeScript has better typechecking at the alias definition site:
For ``P[K]``, ``K`` needs to have ``keyof P``. The ``extends``
conditional type operator narrows the type to help spuport this.

We could do potentially better but it would require quite a bit more
machinery.

* ``KeyOf[T]`` - literal keys of ``T``
* ``Member[T]``, when statically checking a type alias, could be
  treated as having some type like ``tuple[Member[KeyOf[T], object,
  str, ..., ...], ...]``
* ``GetMemberType[T, S: KeyOf[T]]`` - but this isn't supported yet.
  TypeScript supports it.
* We would also need to do context sensitive type bound inference


Potential Future Extensions
===========================

Support Manipulating Annotated
------------------------------

Libraries like FastAPI use annotations heavily, and we would like to
be able to use annotations to drive type-level computation decision
making.

Note that currently ``Annotated`` may be fully ignored by
typecheckers, and so supporting inspection and manipulation of it
could end up being fraught.

One potential API for this might be:

* ``GetAnnotations[T]`` - Fetch the annotations of a potentially
  Annotated type, as Literals. Examples::

    GetAnnotations[Annotated[int, 'xxx']] = Literal['xxx']
    GetAnnotations[Annotated[int, 'xxx', 5]] = Literal['xxx', 5]
    GetAnnotations[int] = Never


* ``DropAnnotations[T]`` - Drop the annotations of a potentially
  Annotated type. Examples::

    DropAnnotations[Annotated[int, 'xxx']] = int
    DropAnnotations[Annotated[int, 'xxx', 5]] = int
    DropAnnotations[int] = int

String manipulation
'''''''''''''''''''

TypeScript has "template literal" types for strings that allow both
concatenating string literal types and decomposing them. They also
have a suite of capitalization related operations.

Supporting concatenation would allow use-cases such as generating new
method names based on attributes: for every attribute ``foo`` we could
generate a ``get_foo`` method.

Supporting slicing would allow doing more in-depth string traversals,
and supporting capitalization would allow operations like transforming
a name from ``snake_case`` to ``CapitalizedWords``.

We can actually implement the case functions in terms of them and a
bunch of conditionals, but shouldn't (especially if we want it to work
for all unicode!).

It would definitely be possible to take just slicing and
concatenation, also.

* ``Slice[S: Literal[str], Start: Literal[int | None], End: Literal[int | None]]``:
  Also support slicing string types. (Currently tuples are supported.)
* ``Concat[S1: Literal[str], S2: Literal[str]]``: concatenate two strings
* ``Uppercase[S: Literal[str]]``: uppercase a string literal
* ``Lowercase[S: Literal[str]]``: lowercase a string literal
* ``Capitalize[S: Literal[str]]``: capitalize a string literal
* ``Uncapitalize[S: Literal[str]]``: uncapitalize a string literal

All of the operators in this section are :ref:`lifted over union types
<pep827-lifting>`.

NewProtocolWithBases
''''''''''''''''''''

It would sometimes be useful to support something like
``NewProtocolWithBases``, with a specification like:

* ``NewProtocolWithBases[Bases: tuple[type], *Ms: Member]``

The idea is that a type would satisfy this protocol if it extends all
of the given bases and has the specified members.

This would be useful in situations where we want to do something like
creating a new Pydantic model.

We are holding off from fully proposing this at this time because
protocol-with-bases would be an addition to what protocols can be that
we don't want to tangle with yet, and because many use cases can be
simulated in other ways.

.. * Should we support building new nominal types??

Open Issues
===========

* What invalid operations should be errors and what should return ``Never``?

* :ref:`Unpack of typevars for **kwargs <pep827-unpack-kwargs>`: Should
  whether we try to infer literal types for extra arguments be
  configurable in the ``TypedDict`` serving as the bound somehow? If
  ``readonly`` had been added as a parameter to ``TypedDict`` we would
  use that, but it wasn't.

* :ref:`Extended Callables <pep827-extended-callables-prereq>`: Should the extended
  argument list be wrapped in a ``typing.Parameters[*Params]`` type (that
  will also kind of serve as a bound for ``ParamSpec``)?

* :ref:`Extended Callables <pep827-extended-callables-prereq>`: Currently the
  qualifiers are short strings for code brevity, but an alternate approach
  would be to mirror ``inspect.Signature`` more directly, and have an enum
  with names like ``ParamKind.POSITIONAL_OR_KEYWORD``. Would that be better?

  A related potential change would be to fully separate the kind from whether
  there is a default, and have whether there is a default represented in
  an ``init`` field, like we do for class member initializers with ``Member``.

* :ref:`Generic Callable <pep827-generic-callable>`: Should we have any mechanisms
  to inspect/destruct ``GenericCallable``? Maybe can fetch the variable
  information and maybe can apply it to concrete types?

* :ref:`Update class <pep827-update-class>`: ``UpdateClass`` introduces
  type-evaluation-order dependence; if the ``UpdateClass`` return type for
  some ``__init_subclass__`` inspects some unrelated class's ``Members``,
  and that class also has an ``__init_subclass__``, then the results might
  depend on what order they are evaluated. Ideally this kind of case would be
  rejected. This does actually exactly mirror a potential **runtime**
  evaluation-order dependence, though.

* Because of generic functions, there will be plenty of cases where we
  can't evaluate a type operator (because it's applied to an unresolved
  type variable), and exactly what the type evaluation rules should be
  in those cases is somewhat unclear.

  Currently, in the proof of concept implementation in mypy, stuck type
  evaluations implement subtype checking fully invariantly: we check
  that the operators match and that every operand matches in both
  arguments invariantly.


Acknowledgements
================

We'd like to thank Jukka Lehtosalo, for many discussions about the design.

We'd also like to thank the TypeScript team for their language's
substantial influence on this proposal!

Footnotes
=========

.. _#broadcasting: https://numpy.org/doc/stable/user/basics.broadcasting.html
.. _#fastapi: https://fastapi.tiangolo.com/
.. _#pydantic: https://docs.pydantic.dev/latest/
.. _#fastapi-tutorial: https://fastapi.tiangolo.com/tutorial/sql-databases/#heroupdate-the-data-model-to-update-a-hero
.. _#fastapi-test: https://github.com/vercel/python-typemap/blob/main/tests/test_fastapilike_2.py
.. _#prisma: https://www.prisma.io/
.. _#prisma-example: https://github.com/prisma/prisma-examples/tree/latest/orm/express
.. _#qb-test: https://github.com/vercel/python-typemap/blob/main/tests/test_qblike_2.py
.. _#ref-impl: https://github.com/msullivan/mypy/tree/typemap
.. _#runtime: https://github.com/vercel/python-typemap
.. _#starlark: https://starlark-lang.org/
.. _#survey: https://engineering.fb.com/2025/12/22/developer-tools/python-typing-survey-2025-code-quality-flexibility-typing-adoption/
.. _#ast_format: https://imogenbits-peps.readthedocs.io/en/ast_format/pep-9999/

.. [#undecidable]

* "Partial polymorphic type inference is undecidable" by Hans Boehm: https://dl.acm.org/doi/10.1109/SFCS.1985.44
* "On the Undecidability of Partial Polymorphic Type Reconstruction" by Frank Pfenning: https://www.cs.cmu.edu/~fp/papers/CMU-CS-92-105.pdf

  Our setting does not try to infer generic types for functions,
  though, which might dodge some of the problems. On the other hand,
  we have subtyping. (Honestly we are already pretty deep into some
  of these cans of worms.)


Copyright
=========

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.
