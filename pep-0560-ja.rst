PEP: 560
Title: Core support for typing module and generic types
Author: Ivan Levkivskyi <levkivskyi@gmail.com>
Status: Accepted
Type: Standards Track
Content-Type: text/x-rst
Created: 03-Sep-2017
Python-Version: 3.7
Post-History: 09-Sep-2017, 14-Nov-2017
Resolution: https://mail.python.org/pipermail/python-dev/2017-December/151038.html


Abstract
========

Initially PEP 484 was designed in such way that it would not introduce
*any* changes to the core CPython interpreter. Now type hints and
the ``typing`` module are extensively used by the community, e.g. PEP 526
and PEP 557 extend the usage of type hints, and the backport of ``typing``
on PyPI has 1M downloads/month. Therefore, this restriction can be removed.
It is proposed to add two special methods ``__class_getitem__`` and
``__mro_entries__`` to the core CPython for better support of
generic types.


当初、 PEP 484はインタプリタに何の変更も及ぼさないように設計されていました。 今は型ヒントと ``typing`` モジュールはコミュニティで広く使用されています。たとえば、PEP 526とPEP 557は型ヒントの使用を拡張しましたし、PyPIの ``typing`` バックポートは月に100万回ダウンロードされています。ですから、この当初の制限は取り除けるものでしょう。ジェネリック型のサポートを強化するために __class_getitem__と__mro_entries__の 2つの特別なメソッドをコアCPythonに追加することを提案します。

Rationale
=========

The restriction to not modify the core CPython interpreter led to some
design decisions that became questionable when the ``typing`` module started
to be widely used. There are three main points of concern:
performance of the ``typing`` module, metaclass conflicts, and the large
number of hacks currently used in ``typing``.

インタプリタを変更しないという制限によって、 ``typing`` モジュールが広く使われるようになった今では疑問をもたれる設計が行われました。 検討しないといけない主なものは、 ``typing`` モジュールのパフォーマンス、メタクラスの競合、および ``typing`` で現在使用されている多くのハッキングです。

Performance
-----------

The ``typing`` module is one of the heaviest and slowest modules in
the standard library even with all the optimizations made. Mainly this is
because subscripted generic types (see PEP 484 for definition of terms used
in this PEP) are class objects (see also [1]_). There are three main ways how
the performance can be improved with the help of the proposed special methods:

``typing`` モジュールは、すべての最適化が行われていても、標準ライブラリの中で最も重く遅いモジュールの1つです。 これは主に、添え字ジェネリック型（このPEPで使用される用語の定義についてはPEP 484を参照）がクラスオブジェクトであるためです（ 　[1]_　も参照）。 提案されている特別な方法の助けを借りてパフォーマンスを向上させる方法には、主に3つの方法があります。

- Creation of generic classes is slow since the ``GenericMeta.__new__`` is
  very slow; we will not need it anymore.

  ``GenericMeta.__new__`` は非常に遅いのでジェネリッククラスの作成は遅いです。もう必要ありません。

- Very long method resolution orders (MROs) for generic classes will be
  half as long; they are present because we duplicate the ``collections.abc``
  inheritance chain in ``typing``.

  非常に長いジェネリッククラスのメソッド解決順（MRO）が半分になります。 ``typing`` の ``collections.abc`` の継承チェーンが複製されるので発生していました。

- Instantiation of generic classes will be faster (this is minor however).

  ジェネリッククラスのインスタンス化は高速になります（これはわずかですが）。

Metaclass conflicts
-------------------

All generic types are instances of ``GenericMeta``, so if a user uses
a custom metaclass, then it is hard to make a corresponding class generic.
This is particularly hard for library classes that a user doesn't control.
A workaround is to always mix-in ``GenericMeta``::

すべてのジェネリック型は ``GenericMeta`` のインスタンスなので、ユーザーがカスタムメタクラスを使用する場合にクラスをジェネリックにすることは難しいです。 これは、ユーザが制御しないライブラリクラスで特に難しいことです。 回避策は、 ``GenericMeta`` を常にミックスインすることです 。

  class AdHocMeta(GenericMeta, LibraryMeta):
      pass

  class UserClass(LibraryBase, Generic[T], metaclass=AdHocMeta):
      ...

but this is not always practical or even possible. With the help of the
proposed special attributes the ``GenericMeta`` metaclass will not be needed.

これは必ずしも実用的ではありません。 提案の特別な属性のおかげで、 ``GenericMeta`` メタクラスは必要なくなるでしょう。

Hacks and bugs that will be removed by this proposal
----------------------------------------------------

- ``_generic_new`` hack that exists because ``__init__`` is not called on
  instances with a type differing form the type whose ``__new__`` was called,
  ``C[int]().__class__ is C``.

  呼び出された型と異なる型のインスタンスで ``__new__`` が呼ばれた際に ``__init__`` が呼び出されないために存在する ``_generic_new__`` ハック。C [int]（）.__ class__はCです

- ``_next_in_mro`` speed hack will be not necessary since subscription will
  not create new classes.

  サブスクリプションは新しいクラスを作成しなくなるので、スピードのための ``_next_in_mro`` ハックは不要になります

- Ugly ``sys._getframe`` hack. This one is particularly nasty since it looks
  like we can't remove it without changes outside ``typing``.

  ひどい ``sys._getframe`` ハック。 `typing` モジュール以外を変更するほかでは無くせそうになかったので特に特に厄介でした

- Currently generics do dangerous things with private ABC caches
  to fix large memory consumption that grows at least as O(N\ :sup:`2`),
  see [2]_. This point is also important because it was recently proposed to
  re-implement ``ABCMeta`` in C.

  現在、ジェネリックスは少なくとも O(N\ :sup:`2`)　のように大きくなる大きなメモリ消費量を修正するためにプライベートABCキャッシュで危険なことをしています。 [2]_ を参照してください。 最近、C 言語でABCMetaを再実装することが提案されたのも、この点において重要です

- Problems with sharing attributes between subscripted generics,
  see [3]_. The current solution already uses ``__getattr__`` and ``__setattr__``,
  but it is still incomplete, and solving this without the current proposal
  will be hard and will need ``__getattribute__``.

  添字付きジェネリック間で属性を共有する際の問題については、 [3]_ を参照してください。 現在のソリューションは既に ``__getattr__`` と ``__setattr__`` を使用していますが、それでもまだ不完全で、この提案なしで解決するのは難しく 、 ``__ getattribute__`` が必要です

- ``_no_slots_copy`` hack, where we clean up the class dictionary on every
  subscription thus allowing generics with ``__slots__``.

  __slots__でジェネリックを許可するたっめにすべてのサブスクリプションでクラス辞書をクリーンアップする ``_no_slots_copy`` ハック

- General complexity of the ``typing`` module. The new proposal will not
  only allow to remove the above mentioned hacks/bugs, but also simplify
  the implementation, so that it will be easier to maintain.

  ``typing`` モジュールの複雑さ。この提案で上記のハックやバグを取り除くことができるだけでなく、実装がシンプルになり、保守が容易になります


Specification
=============

``__class_getitem__``
---------------------

The idea of ``__class_getitem__`` is simple: it is an exact analog of
``__getitem__`` with an exception that it is called on a class that
defines it, not on its instances. This allows us to avoid
``GenericMeta.__getitem__`` for things like ``Iterable[int]``.
The ``__class_getitem__`` is automatically a class method and
does not require ``@classmethod`` decorator (similar to
``__init_subclass__``) and is inherited like normal attributes.
For example

``__class_getitem__`` のアイデアはシンプルです。 __getitem__とまったく同じですが、インスタンスではなく定義したクラスで呼び出されるという例外があります。 これにより、 ``Iterable[int]`` のようなものに対して ``GenericMeta.__ getitem__`` を避けることができます。 ``__class_getitem__`` は ``@classmethod`` デコレータを書かずとも自動的にクラスメソッドになり（ ``__init_subclass__`` に似ています ）、通常の属性のように継承されます。 例えば::

  class MyList:
      def __getitem__(self, index):
          return index + 1
      def __class_getitem__(cls, item):
          return f"{cls.__name__}[{item.__name__}]"

  class MyOtherList(MyList):
      pass

  assert MyList()[0] == 1
  assert MyList[int] == "MyList[int]"

  assert MyOtherList()[0] == 1
  assert MyOtherList[int] == "MyOtherList[int]"

Note that this method is used as a fallback, so if a metaclass defines
``__getitem__``, then that will have the priority.

このメソッドはフォールバックとして使用されることに注意してください。メタクラスで ``__getitem__`` を定義すると優先されます。

``__mro_entries__``
-------------------

If an object that is not a class object appears in the tuple of bases of
a class definition, then method ``__mro_entries__`` is searched on it.
If found, it is called with the original tuple of bases as an argument.
The result of the call must be a tuple, that is unpacked in the base classes
in place of this object. (If the tuple is empty, this means that the original
bases is simply discarded.) If there are more than one object with
``__mro_entries__``, then all of them are called with the same original tuple
of bases. This step happens first in the process of creation of a class,
all other steps, including checks for duplicate bases and MRO calculation,
happen normally with the updated bases.

クラスオブジェクトではないオブジェクトがクラス定義のベースのタプルに現れた場合、メソッド ``__mro_entries__`` が検索されます。 見つかった場合、ベースの元タプルを引数として呼び出されます。 呼び出しの結果は、このオブジェクトの代わりに基底クラスで解凍されたタプルでなければなりません。 （タプルが空の場合、これは元の基底が単に破棄されることを意味します） 。 ``__mro_entries__`` を持つオブジェクトが複数ある場合、それらのオブジェクトはすべて同じ元の元のタプルで呼び出されます。 このステップは、クラスの作成過程で最初に行われ、複製ベースとMRO計算のチェックを含む他のすべてのステップは、通常、更新されたベースで行われます。

Using the method API instead of just an attribute is necessary to avoid
inconsistent MRO errors, and perform other manipulations that are currently
done by ``GenericMeta.__new__``. The original bases are stored as
``__orig_bases__`` in the class namespace (currently this is also done by
the metaclass). For example

矛盾したMROエラーを回避し、現在 ``GenericMeta.__new__`` によって行われている他の操作を実行するには、属性の代わりにメソッドAPIを使用する必要があります。 元の基底はクラスの名前空間に ``__orig_bases__`` として格納されます（現在はメタクラスによっても行われています）。 例えば::

  class GenericAlias:
      def __init__(self, origin, item):
          self.origin = origin
          self.item = item
      def __mro_entries__(self, bases):
          return (self.origin,)

  class NewList:
      def __class_getitem__(cls, item):
          return GenericAlias(cls, item)

  class Tokens(NewList[int]):
      ...

  assert Tokens.__bases__ == (NewList,)
  assert Tokens.__orig_bases__ == (NewList[int],)
  assert Tokens.__mro__ == (Tokens, NewList, object)

Resolution using ``__mro_entries__`` happens *only* in bases of a class
definition statement. In all other situations where a class object is
expected, no such resolution will happen, this includes ``isinstance``
and ``issubclass`` built-in functions.

``__mro_entries__`` を使用した解決は、クラス定義ステートメントのベースでのみ発生します。 クラスオブジェクトが予期される他のすべての状況では、 ``isinstance`` と ``issubclass`` 組み込み関数が含まれます。

NOTE: These two method names are reserved for use by the ``typing`` module
and the generic types machinery, and any other use is discouraged.
The reference implementation (with tests) can be found in [4]_, and
the proposal was originally posted and discussed on the ``typing`` tracker,
see [5]_.

注：これらの2つのメソッド名は、型指定モジュールとジェネリック型の仕組みで使用するために予約されています 。他の使用方法はお勧めしません。 リファレンス実装（テストあり）は [4]_ にあり、提案はもともと ``typing`` トラッカーに投稿され、議論されています [5]_  。

Dynamic class creation and ``types.resolve_bases``
--------------------------------------------------

``type.__new__`` will not perform any MRO entry resolution. So that a direct
call ``type('Tokens', (List[int],), {})`` will fail. This is done for
performance reasons and to minimize the number of implicit transformations.
Instead, a helper function ``resolve_bases`` will be added to
the ``types`` module to allow an explicit ``__mro_entries__`` resolution in
the context of dynamic class creation. Correspondingly, ``types.new_class``
will be updated to reflect the new class creation steps while maintaining
the backwards compatibility

``type.__new__`` はMROエントリ解決を実行しません。 したがって、直接 ``type('Tokens', (List[int],), {})`` の呼び出しは失敗します。 これは、パフォーマンス上の理由から、暗黙的な変換の回数を最小限に抑えるために行われます。 代わりに、ヘルパー関数 ``resolve_bases`` が ``types`` モジュールに追加され、動的クラス作成のコンテキストで明示的な ``__mro_entries__`` 解決を可能にします。 同様に、 ``types.new_class`` は、後方互換性を維持しながら新しいクラス作成手順を反映するように更新されます::

  def new_class(name, bases=(), kwds=None, exec_body=None):
      resolved_bases = resolve_bases(bases)  # This step is added
      meta, ns, kwds = prepare_class(name, resolved_bases, kwds)
      if exec_body is not None:
          exec_body(ns)
      ns['__orig_bases__'] = bases  # This step is added
      return meta(name, resolved_bases, ns, **kwds)


Using ``__class_getitem__`` in C extensions
-------------------------------------------

As mentioned above, ``__class_getitem__`` is automatically a class method
if defined in Python code. To define this method in a C extension, one
should use flags ``METH_O|METH_CLASS``. For example, a simple way to make
an extension class generic is to use a method that simply returns the
original class objects, thus fully erasing the type information at runtime,
and deferring all check to static type checkers only::

前述のように、Pythonのコードで定義された ``__class_getitem__`` は、自動的にクラスメソッドになります。 このメソッドをC拡張で定義するには、 ``METH_O|METH_CLASS`` フラグを使用する必要があります。 たとえば、拡張クラスを汎用的にする簡単な方法は、元のクラスオブジェクトを単に返すメソッドを使用して、実行時に型情報を完全に消去し、すべてのチェックを静的型チェッカーだけに任せることです。

  typedef struct {
      PyObject_HEAD
      /* ... your code ... */
  } SimpleGeneric;

  static PyObject *
  simple_class_getitem(PyObject *type, PyObject *item)
  {
      Py_INCREF(type);
      return type;
  }

  static PyMethodDef simple_generic_methods[] = {
      {"__class_getitem__", simple_class_getitem, METH_O|METH_CLASS, NULL},
      /* ... other methods ... */
  };

  PyTypeObject SimpleGeneric_Type = {
      PyVarObject_HEAD_INIT(NULL, 0)
      "SimpleGeneric",
      sizeof(SimpleGeneric),
      0,
      .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
      .tp_methods = simple_generic_methods,
  };

Such class can be used as a normal generic in Python type annotations
(a corresponding stub file should be provided for static type checkers,
see PEP 484 for details)

そのようなクラスは、Pythonの型アノテーションの通常のジェネリックとして使用することができます（スタティック型チェッカーの場合は対応するスタブファイルを提供する必要があります（詳細はPEP 484を参照）。::

  from simple_extension import SimpleGeneric
  from typing import TypeVar

  T = TypeVar('T')

  Alias = SimpleGeneric[str, T]
  class SubClass(SimpleGeneric[T, int]):
      ...

  data: Alias[int]  # Works at runtime
  more_data: SubClass[str]  # Also works at runtime


Backwards compatibility and impact on users who don't use ``typing``
====================================================================

This proposal may break code that currently uses the names
``__class_getitem__`` and ``__mro_entries__``.  (But the language
reference explicitly reserves *all* undocumented dunder names, and
allows "breakage without warning"; see [6]_.)

この提案は、現在、 ``__class_getitem__`` および ``__mro_entries__`` という名前を使用しているコードを壊す可能性があります 。 （しかし、言語参照は明示的に全ての文書化されていないダンダー（ダブルアンダースコア）の名前を予約し、 "警告なしで破損する"ことを認めている; [6]_ 参照）。

This proposal will support almost complete backwards compatibility with
the current public generic types API; moreover the ``typing`` module is still
provisional. The only two exceptions are that currently
``issubclass(List[int], List)`` returns True, while with this proposal it will
raise ``TypeError``, and ``repr()`` of unsubscripted user-defined generics
cannot be tweaked and will coincide with ``repr()`` of normal (non-generic)
classes.

この提案は、現在のパブリックジェネリック型APIとのほぼ完全な下位互換性をサポートします。 さらに、 ``typing`` モジュールはまだ暫定的です。 ただ2つの例外は、現在のところ ``issubclass(List[int], List)`` はTrueを返します。この提案では ``TypeError`` が発生し 、ユーザ定義されていないジェネリックの ``repr()`` は微調整できず、通常の ``repr()`` （非ジェネリック）クラスと同一になります。

With the reference implementation I measured negligible performance effects
(under 1% on a micro-benchmark) for regular (non-generic) classes. At the same
time performance of generics is significantly improved

リファレンス実装では、通常の（非ジェネリック）クラスのパフォーマンスの影響を無視して測定しました（マイクロベンチマークでは1％以下）。 同時に、ジェネリックのパフォーマンスが大幅に向上します。:

* ``importlib.reload(typing)`` is up to 7x faster

  ``importlib.reload(typing)`` は最大7倍高速になります

* Creation of user defined generic classes is up to 4x faster (on a micro-
  benchmark with an empty body)

  ユーザー定義のジェネリッククラスの作成は、最大4倍高速です（空のボディを持つマイクロベンチマークで）

* Instantiation of generic classes is up to 5x faster (on a micro-benchmark
  with an empty ``__init__``)

  ジェネリッククラスのインスタンス化は最大5倍高速です（空の ``__init__`` を持つマイクロベンチマークで）

* Other operations with generic types and instances (like method lookup and
  ``isinstance()`` checks) are improved by around 10-20%

  メソッドのルックアップや ``isinstance()`` チェックなどのジェネリック型とインスタンスによるその他の操作は、約10〜20％改善します

* The only aspect that gets slower with the current proof of concept
  implementation is the subscripted generics cache look-up. However it was
  already very efficient, so this aspect gives negligible overall impact.

  現在の概念実証実装により遅くなる唯一の側面は、添字付きのジェネリック・キャッシュ・ルックアップです。 しかし、それはすでに非常に効率的でした。したがって、この側面は全体的な影響はごくわずかです。

References
==========

.. [1] Discussion following Mark Shannon's presentation at Language Summit
   (https://github.com/python/typing/issues/432)

.. [2] Pull Request to implement shared generic ABC caches (merged)
   (https://github.com/python/typing/pull/383)

.. [3] An old bug with setting/accessing attributes on generic types
   (https://github.com/python/typing/issues/392)

.. [4] The reference implementation
   (https://github.com/ilevkivskyi/cpython/pull/2/files,
   https://github.com/ilevkivskyi/cpython/tree/new-typing)

.. [5] Original proposal
   (https://github.com/python/typing/issues/468)

.. [6] Reserved classes of identifiers
   (https://docs.python.org/3/reference/lexical_analysis.html#reserved-classes-of-identifiers)

Copyright
=========

This document has been placed in the public domain.



..
   Local Variables:
   mode: indented-text
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   coding: utf-8
   End: