PEP: 561 
Title: Distributing and Packaging Type Information
Author: Ethan Smith <ethan@ethanhs.me>
Status: Accepted
Type: Standards Track
Content-Type: text/x-rst
Created: 09-Sep-2017
Python-Version: 3.7
Post-History: 10-Sep-2017, 12-Sep-2017, 06-Oct-2017, 26-Oct-2017, 12-Apr-2018


Abstract
========

PEP 484 introduced type hinting to Python, with goals of making typing
gradual and easy to adopt. Currently, typing information must be distributed
manually. This PEP provides a standardized means to leverage existing tooling
to package and distribute type information with minimal work and an ordering
for type checkers to resolve modules and collect this information for type
checking.

PEP 484は、入力のヒントをPythonに導入しました。ゴールは型を緩やかで簡単に導入できるものでした。
今の所、型情報は手動で配布する必要があります。
本PEPは、既存のツールを活用して最小限の作業でタイプ情報をパッケージ化して配布するための標準化された手段と、タイプチェッカーが型チェックのための型情報を収集するモジュール探索順を提供します。


Rationale
=========

Currently, package authors wish to distribute code that has inline type
information. Additionally, maintainers would like to distribute stub files
to keep Python 2 compatibility while using newer annotation syntax. However,
there is no standard method to distribute packages with type information.
Also, if one wished to ship stub files privately the only method available
would be via setting ``MYPYPATH`` or the equivalent to manually point to
stubs. If the package can be released publicly, it can be added to 
typeshed [1]_. However, this does not scale and becomes a burden on the
maintainers of typeshed. In addition, it ties bug fixes in stubs to releases
of the tool using typeshed.

現在、パッケージ作成者は、インラインタイプの情報を持つコードを配布したいと考えています。 
さらにメンテナーは、新しいアノテーション構文を使用しながらPython 2との互換性を保つためにスタブファイルを配布したいと考えています。 
しかし、型情報を持つパッケージを配布するための標準的な方法はありません。
また、スタブファイルを個人的に配布したい場合は、 MYPYPATH環境変数または同等のものを手動でスタブにポイントする方法があります。 
パッケージを公開することができれば、それをtypeshed [1]_ に追加することができます。 
しかしこれはスケールしませんし、typeshed管理者にとって負担になります。
さらに、スタブ内のバグ修正をtypeshedを使ったツールのリリースに結びついてしまいます。

PEP 484 has a brief section on distributing typing information. In this
section [2]_ the PEP recommends using ``shared/typehints/pythonX.Y/`` for
shipping stub files. However, manually adding a path to stub files for each
third party library does not scale. The simplest approach people have taken
is to add ``site-packages`` to their ``MYPYPATH``, but this causes type
checkers to fail on packages that are highly dynamic (e.g. sqlalchemy 
and Django).

PEP 484には、タイピング情報の配布に関する簡単なセクションがあります。
このセクション [2]_ では、PEPは、配送スタブファイルのためにshared / typehints / pythonX.Y /を使うことを推奨しています。 
ただし、各サードパーティ製ライブラリのスタブファイルへのパスを手動での追加はスケールしません。 
人々が取った最も簡単なアプローチは、自分のMYPYPATH環境変数に site-packages を追加することですが、これは動的なパッケージ（例えば、sqlalchemyやDjangoなど）で型チェックが失敗します。

Definition of Terms
===================

The definition of "MAY", "MUST", and "SHOULD", and "SHOULD NOT" are
to be interpreted as described in RFC 2119.

"MAY"、 "MUST"、 "SHOULD"、 "SHOULD NOT"の定義はRFC 2119に記述されているように解釈されます 。

"inline" - the types are part of the runtime code using PEP 526 and
PEP 3107 syntax (the filename ends in ``.py``).

"インライン" - 型はPEP 526とPEP 3107の構文（ファイル名は.pyで終わる）を使ってランタイムコードの一部です。

"stubs" - files containing only type information, empty of runtime code
(the filename ends in ``.pyi``).

"スタブ" - タイプ情報のみを含むファイル、ランタイムコードが空です（ファイル名は.pyiで終わります）。

"Distributions" are the packaged files which are used to publish and distribute
a release. [3]_

「ディストリビューション」は、リリースを公開および配布するために使用されるパッケージファイルです。 [3]_

"Module" a file containing Python runtime code or stubbed type information.

"モジュール"は、Pythonランタイムコードまたはスタブ型情報を含むファイルです。

"Package" a directory or directories that namespace Python modules.
(Note the distinction between packages and distributions.  While most
distributions are named after the one package they install, some
distributions install multiple packages.)

Pythonモジュールの名前空間を持つディレクトリを「パッケージ」します。 （パッケージとディストリビューションの区別に注意してください。ほとんどのディストリビューションは、それらがインストールするパッケージの名前になっていますが、いくつかのディストリビューションでは複数のパッケージがインストールされます）。

Specification
=============

There are several motivations and methods of supporting typing in a package.
This PEP recognizes three types of packages that users of typing wish to
create

パッケージにはタイピングをサポートするモチベーションと方法がいくつかあります。 このPEPは、入力のユーザが作成したい3種類のパッケージを認識します:

1. The package maintainer would like to add type information inline.

1. パッケージ管理者は、タイプ情報をインラインで追加したいと考えています。

2. The package maintainer would like to add type information via stubs.

2. パッケージメンテナーは、スタブで型情報を追加したいと考えています。

3. A third party or package maintainer would like to share stub files for
   a package, but the maintainer does not want to include them in the source
   of the package.

3. サードパーティまたはパッケージメンテナは、パッケージのスタブファイルを共有したいが、メンテナはパッケージのソースにそれらを含めることは望まない。
   
This PEP aims to support all three scenarios and make them simple to add to
packaging and deployment.

このPEPは、3つのシナリオをすべてサポートし、パッケージングおよび展開に簡単に追加できるようにすることを目的としています。

The two major parts of this specification are the packaging specifications
and the resolution order for resolving module type information. The type
checking spec is meant to replace the ``shared/typehints/pythonX.Y/`` spec
of PEP 484 [2]_.

この仕様の2つの主要な部分は、モジュールのタイプ情報を解決するためのパッケージ仕様と解決のためのモジュール探索順です。
型チェック仕様は、 PEP 484 [2]_ の仕様 ``shared/typehints/pythonX.Y/`` を置き換えることを意図しています。

New third party stub libraries SHOULD distribute stubs via the third party
packaging methods proposed in this PEP in place of being added to typeshed.
Typeshed will remain in use, but if maintainers are found, third party stubs
in typeshed MAY be split into their own package.

新しいサードパーティのスタブライブラリは、typeshedに追加するのではなく、このPEPで提案されているサードパーティのパッケージメソッドを介してスタブを配布するべきです。
Typeshedは引き続き使用されますが、メンテナーが見つかったらtypeshedから独自のパッケージに分割されるでしょう。

Packaging Type Information
--------------------------

In order to make packaging and distributing type information as simple and
easy as possible, packaging and distribution is done through existing
frameworks.

パッケージングを行い、型情報をできるだけ簡単かつ簡単に配布するために、パッケージングと配布は既存のフレームワークを通じて行われます。

Package maintainers who wish to support type checking of their code MUST add
a marker file named ``py.typed`` to their package supporting typing. This marker applies
recursively: if a top-level package includes it, all its sub-packages MUST support
type checking as well. To have this file installed with the package,
maintainers can use existing packaging options such as ``package_data`` in
distutils, shown below.

コードの型チェックをサポートしたいパッケージメンテナーは、py.typedという名前のマーカファイルを、パッケージをサポートするパッケージに追加しなければならない（MUST）。 このマーカーは再帰的に適用されます。最上位のパッケージにそれが含まれている場合、そのすべてのサブパッケージも型チェックをサポートしなければなりません。 このファイルをパッケージにインストールするには、以下に示すdistutilsのpackage_dataなどの既存のパッケージオプションを使用します。

Distutils option example::

    setup(
        ...,
        package_data = {
            'foopkg': ['py.typed'],
        },
        ...,
        )

For namespace packages (see PEP 420), the ``py.typed`` file should be in the
submodules of the namespace, to avoid conflicts and for clarity.

namespaceパッケージの場合（ PEP 420を参照）、py.typedファイルは名前空間のサブモジュール内にある必要があります。これは、衝突避けるためと明瞭さのためです。

This PEP does not support distributing typing information as part of
module-only distributions. The code should be refactored into a package-based
distribution and indicate that the package supports typing as described
above.

このPEPは、モジュールのみの配布の一部として型情報の配布をサポートしていません。 コードはパッケージベースの配布にリファクタリングして、上記のようにパッケージが入力をサポートすることを示す必要があります。

Stub-only Packages
''''''''''''''''''

For package maintainers wishing to ship stub files containing all of their
type information, it is preferred that the ``*.pyi`` stubs are alongside the
corresponding ``*.py`` files. However, the stubs can also be put in a separate
package and distributed separately. Third parties can also find this method
useful if they wish to distribute stub files. The name of the stub package
MUST follow the scheme ``foopkg-stubs`` for type stubs for the package named
``foopkg``. Note that for stub-only packages adding a ``py.typed`` marker is not
needed since the name ``*-stubs`` is enough to indicate it is a source of typing
information.

パッケージのメンテナーがすべての型情報を含むスタブファイルを配布したい場合は、.pyiスタブは対応する.pyファイルの隣にあることが望ましいです。
ただし、スタブは別のパッケージに入れて別々に配布することもできます。 
サードパーティは、スタブファイルを配布したい場合にもこの手法が便利であることがわかるでしょう。
スタブパッケージの名前は、foopkgという名前のパッケージのスタブタイプのfoopkg-stubsスキームに従わなければなりません。
スタブのみのパッケージの場合、py.typedマーカーを追加する必要はないことに注意してください。
名前-stubsは型情報のソースであることを示すのに十分です。

Third parties seeking to distribute stub files are encouraged to contact the
maintainer of the package about distribution alongside the package. If the
maintainer does not wish to maintain or package stub files or type information
inline, then a third party stub-only package can be created.

スタブファイルを配布しようとしている第三者は、パッケージのメンテナーに連絡してパッケージと一緒に配布することをお勧めします。
メンテナーがスタブファイルを維持したりパッケージ化したりインラインで情報を入力したりしたくない場合は、サードパーティのスタブ専用パッケージを作成することができます。

In addition, stub-only distributions SHOULD indicate which version(s)
of the runtime package are supported by indicating the runtime distribution's
version(s) through normal dependency data. For example, the
stub package ``flyingcircus-stubs`` can indicate the versions of the
runtime ``flyingcircus`` distribution it supports through ``install_requires``
in distutils-based tools, or the equivalent in other packaging tools. Note that
in pip 9.0, if you update ``flyingcircus-stubs``, it will update
``flyingcircus``. In pip 9.0, you can use the
``--upgrade-strategy=only-if-needed`` flag. In pip 10.0 this is the default
behavior.

加えて、スタブ専用ディストリビューションは、通常の依存関係の表し方で対象パッケージのどのバージョンがサポートされているかを示すべきです（SHOULD）。
たとえば、スタブパッケージのflyingcircus-stubsは、distutilsベースのツールのinstall_requiresやその他のパッケージツールでの同等のものでflyingcircusのバージョンを示せます。
pip 9.0では、 flyingcircus-stubsを更新すると、 flyingcircusが更新されることに注意してください。 pip 9.0では、 --upgrade-strategy = only-if-neededフラグを使用できます。 pip 10.0ではこれがデフォルト動作です。


Type Checker Module Resolution Order
------------------------------------

The following is the order in which type checkers supporting this PEP SHOULD
resolve modules containing type information

このPEPをサポートしている型チェックツールが型情報を含むモジュールを解決するモジュール探索順序は次のとおりです:

1. User code - the files the type checker is running on.

1. ユーザーコード - 型チェッカーが実行されているファイル。

2. Stubs or Python source manually put in the beginning of the path. Type
   checkers SHOULD provide this to allow the user complete control of which
   stubs to use, and to patch broken stubs/inline types from packages.
   In mypy the ``$MYPYPATH`` environment variable can be used for this.

2. スタブまたはPythonソースで手動でパスの先頭に挿入された場所。
   型チェッカーはこれを提供して、どのスタブを使用するかを完全に制御し、バグっているスタブ/インライン型をパッケージからパッチすることを許可すべきです（SHOULD）。
   mypyでは、これに$MYPYPATH環境変数を使用できます。

3. Stub packages - these packages SHOULD supersede any installed inline
   package. They can be found at ``foopkg-stubs`` for package ``foopkg``.

3. スタブパッケージ - これらのパッケージは、インストールされているインラインパッケージに取って代わるべきである（SHOULD）。
   foopkgパッケージの場合はfoopkg-stubsです。

4. Inline packages - if there is nothing overriding the installed
   package, *and* it opts into type checking, inline types SHOULD be used.

4. インラインパッケージ - インストールされたパッケージをオーバーライドするものがなく、型チェックを選択する場合は、インライン型を使うべきです（SHOULD）。

5. Typeshed (if used) - Provides the stdlib types and several third party
   libraries.

5. Typeshed（使用されている場合） - stdlib型といくつかのサードパーティライブラリを提供します。

Type checkers that check a different Python version than the version they run
on MUST find the type information in the ``site-packages``/``dist-packages``
of that Python version. This can be queried e.g.
``pythonX.Y -c 'import site; print(site.getsitepackages())'``. It is also recommended
that the type checker allow for the user to point to a particular Python
binary, in case it is not in the path.

実行するバージョンとは異なるPythonバージョンをチェックするタイプチェッカーは、そのPythonバージョンのsite-packages / dist-packagesにタイプ情報を見つけなければなりません。 これは例えばpythonX.Y -c 'import site; print（site.getsiteパッケージ（）） ' また、パスにない場合は、タイプチェッカーを使用して特定のPythonバイナリを指すこともできます。

Partial Stub Packages
---------------------

Many stub packages will only have part of the type interface for libraries
completed, especially initially. For the benefit of type checking and code
editors, packages can be "partial". This means modules not found in the stub
package SHOULD be searched for in parts four and five of the module resolution
order above, namely inline packages and typeshed.

多くのスタブパッケージは、特に初めに、完成したライブラリ用のタイプインタフェースの一部しか持たないでしょう。
型チェックとコードエディタのために、パッケージは「部分的」にすることができます。
つまり、スタブパッケージに見つからないモジュールは、上記のモジュール解決順序のうちの4番目と5番目の部分、つまりインラインパッケージとtypeshedで検索されるべきである（SHOULD）。

Type checkers should merge the stub package and runtime package or typeshed
directories. This can be thought of as the functional equivalent of copying the
stub package into the same directory as the corresponding runtime package or
typeshed folder and type checking the combined directory structure. Thus type
checkers MUST maintain the normal resolution order of checking ``*.pyi`` before
``*.py`` files.

型チェッカーは、スタブパッケージとランタイムパッケージまたはtypeshedディレクトリをマージする必要があります。 これは、スタブパッケージを対応するランタイムパッケージまたはtypeshedフォルダと同じディレクトリにコピーし、結合されたディレクトリ構造をチェックするという機能的な同等物と考えることができます。 したがって、型チェッカーは、 * .pyファイルの前に* .pyiをチェックする通常の解決順序を維持しなければならない（MUST）。

If a stub package is partial it MUST include ``partial\n`` in a top level
``py.typed`` file.

スタブパッケージが部分的な場合は、最上位のpy.typedファイルに ``partial\n`` を含める必要があります。

Implementation
==============

The proposed scheme of indicating support for typing is completely backwards
compatible, and requires no modification to package tooling. A sample package
with inline types is available [typed_package]_, as well as a [stub_package]_. A
sample package checker [pkg_checker]_ which reads the metadata of installed
packages and reports on their status as either not typed, inline typed, or a
stub package.

タイピングのサポートを示す提案されたスキームは、完全に下位互換性があり、パッケージツーリングの変更を必要としません。
インラインタイプのサンプルパッケージ（ [typed_pa​​ckage]_ ）と [stub_package]_ が利用できます。
インストールされているパッケージのメタデータを読み込み、型付けされていない、インライン型またはスタブパッケージとしてステータスを報告するサンプルパッケージチェッカー [pkg_checker]_ もあります。

The mypy type checker has an implementation of PEP 561 searching which can be
read about in the mypy docs [4]_.

mypy型チェッカーには、 PEP 561の実装があり、これはmypy docs [4]_ で読み取ることができます。

[numpy-stubs]_ is an example of a real stub-only package for the numpy
distribution.

[numpy-stubs]_ は、numpyのスタブ専用パッケージの例です。

Acknowledgements
================

This PEP would not have been possible without the ideas, feedback, and support
of Ivan Levkivskyi, Jelle Zijlstra, Nick Coghlan, Daniel F Moisset, Andrey
Vlasovskikh, Nathaniel Smith, and Guido van Rossum.


Version History
===============

* 2018-07-09

    * Add links to sample stub-only packages

* 2018-06-19

    * Partial stub packages can look at typeshed as well as runtime packages

* 2018-05-15

    * Add partial stub package spec.

* 2018-04-09

    * Add reference to mypy implementation
    * Clarify stub package priority.

* 2018-02-02

    * Change stub-only package suffix to be -stubs not _stubs.
    * Note that py.typed is not needed for stub-only packages.
    * Add note about pip and upgrading stub packages.

* 2017-11-12

    * Rewritten to use existing tooling only
    * No need to indicate kind of type information in metadata
    * Name of marker file changed from ``.typeinfo`` to ``py.typed``

* 2017-11-10
    
    * Specification re-written to use package metadata instead of distribution
      metadata.
    * Removed stub-only packages and merged into third party packages spec.
    * Removed suggestion for typecheckers to consider checking runtime versions
    * Implementations updated to reflect PEP changes.

* 2017-10-26
    
    * Added implementation references.
    * Added acknowledgements and version history.

* 2017-10-06

    * Rewritten to use .distinfo/METADATA over a distutils specific command.
    * Clarify versioning of third party stub packages.

* 2017-09-11

    * Added information about current solutions and typeshed.
    * Clarify rationale.


References
==========
.. [1] Typeshed (https://github.com/python/typeshed)

.. [2] PEP 484, Storing and Distributing Stub Files
   (https://www.python.org/dev/peps/pep-0484/#storing-and-distributing-stub-files)
 
.. [3] PEP 426 definitions
   (https://www.python.org/dev/peps/pep-0426/)

.. [4] Example implementation in a type checker
   (https://mypy.readthedocs.io/en/latest/installed_packages.html)

.. [stub_package] A stub-only package
   (https://github.com/ethanhs/stub-package)

.. [typed_package] Sample typed package
   (https://github.com/ethanhs/sample-typed-package)

.. [numpy-stubs] Stubs for numpy
   (https://github.com/numpy/numpy-stubs)

.. [pkg_checker] Sample package checker
   (https://github.com/ethanhs/check_typedpkg)

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
