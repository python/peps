PEP: 572
Title: Assignment Expressions
Author: Chris Angelico <rosuav@gmail.com>, Tim Peters <tim.peters@gmail.com>,
    Guido van Rossum <guido@python.org>
Status: Accepted
Type: Standards Track
Content-Type: text/x-rst
Created: 28-Feb-2018
Python-Version: 3.8
Post-History: 28-Feb-2018, 02-Mar-2018, 23-Mar-2018, 04-Apr-2018, 17-Apr-2018,
              25-Apr-2018, 09-Jul-2018
Resolution: https://mail.python.org/pipermail/python-dev/2018-July/154601.html


Abstract
========

This is a proposal for creating a way to assign to variables within an
expression using the notation ``NAME := expr``. A new exception,
``TargetScopeError`` is added, and there is one change to evaluation
order.

式で変数代入を行う記法 ``NAME := expr`` についてのプロポーザルです。
新しく ``TargetScopeError`` 例外が追加になり、評価順の変更が1つあります。

Rationale
=========

Naming the result of an expression is an important part of programming,
allowing a descriptive name to be used in place of a longer expression,
and permitting reuse.  Currently, this feature is available only in
statement form, making it unavailable in list comprehensions and other
expression contexts.

式の結果に名前をつけることはプログラミングにおいて重要な部分です。
長い式の代わりに説明的な名前をつけて再利用できるようになっています。
現在はこの機能は文（statement）でのみ利用可能です。リスト内包表記やその他の式の文妙区では利用できません。

Additionally, naming sub-parts of a large expression can assist an interactive
debugger, providing useful display hooks and partial results. Without a way to
capture sub-expressions inline, this would require refactoring of the original
code; with assignment expressions, this merely requires the insertion of a few
``name :=`` markers. Removing the need to refactor reduces the likelihood that
the code be inadvertently changed as part of debugging (a common cause of
Heisenbugs), and is easier to dictate to another programmer.

加えて、名前づけの効果はインタラクティブデバッガのアシストを得られることでもあります。部分的な結果や便利なディスプレイフックを提供できます。式の結果をインラインでキャプチャできなければ、オリジナルのコードをリファクタリングしなければなりません。代入式であれば ``name :=`` マーカーを追加するだけで済みます。リファクタリングをしないで済めば、デバッグのために謝ってコードの変更をする可能性が減らせます（Heisenbugsを引き起こす原因として一般的）し、他のプログラマに指示するのが容易になります。

The importance of real code
---------------------------

During the development of this PEP many people (supporters and critics
both) have had a tendency to focus on toy examples on the one hand,
and on overly complex examples on the other.

このPEPを決めていくにあたり多くの人たち（支持してくれる人も批評をしてくれる人も）は、おもちゃのような例か妙に複雑な例にフォーカスしがちでした。

The danger of toy examples is twofold: they are often too abstract to
make anyone go "ooh, that's compelling", and they are easily refuted
with "I would never write it that way anyway".

おもちゃのような例の危険性は二つあります。一つが「説得力あるね！」と思わせるには抽象すぎてしまうこと、もう一つは「自分は絶対に書かないわ」と簡単に拒否されてしまうことです。

The danger of overly complex examples is that they provide a
convenient strawman for critics of the proposal to shoot down ("that's
obfuscated").

妙に複雑な例の危険性は、それ自体が批評家にとってプロポーザルを棄却する便利な藁人形になってしまうことです。

Yet there is some use for both extremely simple and extremely complex
examples: they are helpful to clarify the intended semantics.
Therefore there will be some of each below.

ですが、極端に単純な例と、極端に複雑な例はそれぞれ意図を明確にするのに役立ちます。
いかがそれぞれの例となってくれることでしょう。

However, in order to be *compelling*, examples should be rooted in
real code, i.e. code that was written without any thought of this PEP,
as part of a useful application, however large or small.  Tim Peters
has been extremely helpful by going over his own personal code
repository and picking examples of code he had written that (in his
view) would have been *clearer* if rewritten with (sparing) use of
assignment expressions.  His conclusion: the current proposal would
have allowed a modest but clear improvement in quite a few bits of
code.

しかしながら、 *説得力のある** ものにするため、例はリアルなコードに根ざしたものであるべきで、大きくても小さくても役に立つアプリケーションの一部の、このPEPを想定していないコードであるべきです。
Tim Petersは自分のコードリポジトリーから例に使うコードを選び、代入式を（控えめに）利用して書き直していたら *より明確に* なったはずです。彼の結論: 現在のプロポーザルは、ちょっとしたコードをささやかだけれども明らかに改善できるだろう。

Another use of real code is to observe indirectly how much value
programmers place on compactness.  Guido van Rossum searched through a
Dropbox code base and discovered some evidence that programmers value
writing fewer lines over shorter lines.

実際のコードのもう一つの用途はプログラマーがコンパクトなことに対してどれだけ価値を感じているかを間接的に観察できることです。Guido van RossumはDropboxのコードベースを調べて、プログラマーは短い行よりも少ない行に価値を感じるいくばくかの証拠を発見しました。

Case in point: Guido found several examples where a programmer
repeated a subexpression, slowing down the program, in order to save
one line of code, e.g. instead of writing

良い例として: Guidoは、行を短くするためにプログラマーがsubexpressionを繰り返して処理速度を遅くしてしまっている例を見つけました。次のように書く代わりに::

    match = re.match(data)
    group = match.group(1) if match else None

they would write

こう書いていました::

    group = re.match(data).group(1) if re.match(data) else None

Another example illustrates that programmers sometimes do more work to
save an extra level of indentation

別の例ではプログラマーがインデントレベルを浅く保つためにより多くの処理を行わせていることが示されます::

    match1 = pattern1.match(data)
    match2 = pattern2.match(data)
    if match1:
        result = match1.group(1)
    elif match2:
        result = match2.group(2)
    else:
        result = None

This code tries to match ``pattern2`` even if ``pattern1`` has a match
(in which case the match on ``pattern2`` is never used).  The more
efficient rewrite would have been

このコードは ``pattern1`` がマッチしたとしても ``pattern2`` のマッチを確認しています（このケースの場合、 ``pattern2`` のマッチは決して使われません）。
より効率的に書き直すとこうなります::

    match1 = pattern1.match(data)
    if match1:
        result = match1.group(1)
    else:
        match2 = pattern2.match(data)
        if match2:
            result = match2.group(2)
        else:
            result = None


Syntax and semantics
====================

In most contexts where arbitrary Python expressions can be used, a
**named expression** can appear.  This is of the form ``NAME := expr``
where ``expr`` is any valid Python expression other than an
unparenthesized tuple, and ``NAME`` is an identifier.

任意のPython式を使用できるほとんどの文脈では、**名前付き式**が現れることがあります。 これは `` NAME:= expr``という形式です。ここで、 `` expr``は括弧で囲まれていないタプル以外の有効なPython式で、 `` NAME``は識別子です。

The value of such a named expression is the same as the incorporated
expression, with the additional side-effect that the target is assigned
that value

そのような名前付き式の値は組み込まれた式と同じですが、ターゲットにその値が割り当てられるという追加の副作用があります。::

    # Handle a matched regex
    if (match := pattern.search(data)) is not None:
        # Do something with match

    # A loop that can't be trivially rewritten using 2-arg iter()
    while chunk := file.read(8192):
       process(chunk)

    # Reuse a value that's expensive to compute
    [y := f(x), y**2, y**3]

    # Share a subexpression between a comprehension filter clause and its output
    filtered_data = [y for x in data if (y := f(x)) is not None]

Exceptional cases
-----------------

There are a few places where assignment expressions are not allowed,
in order to avoid ambiguities or user confusion

あいまいさやユーザーの混乱を避けるために、代入式を使用できない場所がいくつかあります。:

- Unparenthesized assignment expressions are prohibited at the top
  level of an expression statement.  Example

  式ステートメントのトップレベルでは、引用符で囲まれていない代入式は禁止されています。 例::

    y := f(x)  # INVALID
    (y := f(x))  # Valid, though not recommended

  This rule is included to simplify the choice for the user between an
  assignment statement and an assignment expression -- there is no
  syntactic position where both are valid.

  この規則は、代入文と代入式の間でのユーザの選択を単純化するために含まれています -- 両方が有効な構文上の位置はありません。

- Unparenthesized assignment expressions are prohibited at the top
  level of the right hand side of an assignment statement.  Example

  割り当てられていない代入式は、代入文の右辺の最上位で禁止されています。 例::

    y0 = y1 := f(x)  # INVALID
    y0 = (y1 := f(x))  # Valid, though discouraged

  Again, this rule is included to avoid two visually similar ways of
  saying the same thing.

  繰り返しますが、この規則は視覚的に同じ2つの同じことを言うのを避けるために含まれています。

- Unparenthesized assignment expressions are prohibited for the value
  of a keyword argument in a call.  Example

  呼び出し中のキーワード引数の値に対して、引用符で囲まれていない代入式は禁止されています。 例::

    foo(x = y := f(x))  # INVALID
    foo(x=(y := f(x)))  # Valid, though probably confusing

  This rule is included to disallow excessively confusing code, and
  because parsing keyword arguments is complex enough already.

  この規則は、過度に複雑なコードを許可しないため、およびキーワード引数の解析がすでに十分複雑であるために含まれています。

- Unparenthesized assignment expressions are prohibited at the top
  level of a function default value.  Example

  関数デフォルト値の最上位レベルでは、引用符で囲まれていない代入式は禁止されています。 例::

    def foo(answer = p := 42):  # INVALID
        ...
    def foo(answer=(p := 42)):  # Valid, though not great style
        ...

  This rule is included to discourage side effects in a position whose
  exact semantics are already confusing to many users (cf. the common
  style recommendation against mutable default values), and also to
  echo the similar prohibition in calls (the previous bullet).

  この規則は、正確な意味論がすでに多くのユーザを混乱させる立場にある副作用を抑制し（変更可能なデフォルト値に対する一般的なスタイルの推奨を参照）、呼び出しにおける同様の禁止を反映するためにも含まれます（前の箇条書き）。

- Unparenthesized assignment expressions are prohibited as annotations
  for arguments, return values and assignments.  Example

  引数、戻り値、代入に対する注釈として、括弧で囲まれていない代入式は禁止されています。 例::

    def foo(answer: p := 42 = 5):  # INVALID
        ...
    def foo(answer: (p := 42) = 5):  # Valid, but probably never useful
        ...

  The reasoning here is similar to the two previous cases; this
  ungrouped assortment of symbols and operators composed of ``:`` and
  ``=`` is hard to read correctly.

  ここでの推論は、前の2つの場合と似ています。 ``:=`` と ``=`` からなるシンボルと演算子のこのグループ化されていない品揃えは、正しく読みにくいです。

- Unparenthesized assignment expressions are prohibited in lambda functions.
  Example

  束縛されていない代入式は、ラムダ関数では禁止されています。 例::

    (lambda: x := 1) # INVALID
    lambda: (x := 1) # Valid, but unlikely to be useful
    (x := lambda: 1) # Valid
    lambda line: (m := re.match(pattern, line)) and m.group(1) # Valid

  This allows ``lambda`` to always bind less tightly than ``:=``; having a
  name binding at the top level inside a lambda function is unlikely to be of
  value, as there is no way to make use of it. In cases where the name will be
  used more than once, the expression is likely to need parenthesizing anyway,
  so this prohibition will rarely affect code.

  これにより、 ``lambda`` は常に ``:=`` よりも緊密にバインドすることができます。 それを利用する方法がないので、ラムダ関数内のトップレベルで名前バインディングを持つことは価値があるとは思われません。 名前が複数回使用される場合は、式に括弧を付ける必要がある可能性が高いため、この禁止はコードにほとんど影響を与えません。

- Assignment expressions inside of f-strings require parentheses. Example

  f文字列内の代入式には括弧が必要です。 例::

    >>> f'{(x:=10)}'  # Valid, uses assignment expression
    '10'
    >>> x = 10
    >>> f'{x:=10}'    # Valid, passes '=10' to formatter
    '        10'

  This shows that what looks like an assignment operator in an f-string is
  not always an assignment operator.  The f-string parser uses ``:`` to
  indicate formatting options.  To preserve backwards compatibility,
  assignment operator usage inside of f-strings must be parenthesized.
  As noted above, this usage of the assignment operator is not recommended.

  これは、f文字列の代入演算子のように見えるものが必ずしも代入演算子ではないことを示しています。 f文字列パーサはフォーマットオプションを示すために ``:=`` を使います。 下位互換性を維持するために、f文字列内での代入演算子の使用は括弧で囲む必要があります。 上記のように、代入演算子のこの使用法はお勧めできません。

Scope of the target
-------------------

An assignment expression does not introduce a new scope.  In most
cases the scope in which the target will be bound is self-explanatory:
it is the current scope.  If this scope contains a ``nonlocal`` or
``global`` declaration for the target, the assignment expression
honors that.  A lambda (being an explicit, if anonymous, function
definition) counts as a scope for this purpose.

代入式は新しいスコープを導入しません。 ほとんどの場合、ターゲットがバインドされる範囲は一目瞭然です。それが現在の範囲です。 このスコープがターゲットに対する ``nonlocal`` または ``global`` 宣言を含む場合、代入式はそれを守ります。 ラムダ（匿名の場合は明示的な関数定義）は、この目的の範囲としてカウントされます。

There is one special case: an assignment expression occurring in a
list, set or dict comprehension or in a generator expression (below
collectively referred to as "comprehensions") binds the target in the
containing scope, honoring a ``nonlocal`` or ``global`` declaration
for the target in that scope, if one exists.  For the purpose of this
rule the containing scope of a nested comprehension is the scope that
contains the outermost comprehension.  A lambda counts as a containing
scope.

特別な場合が1つあります。リスト、集合または辞書内包表記またはジェネレータ式（以下まとめて「内包表記」と呼びます）に現れる代入式は、ターゲットを包含スコープ内でバインドし、 ``nonlocal`` または ``global`` を尊重します。 そのスコープ内のターゲットに対するグローバル宣言（存在する場合） この規則の目的のために、入れ子にされた内包の包含範囲は、最も外側の内包を含む範囲です。 ラムダは包含スコープとしてカウントされます。

The motivation for this special case is twofold.  First, it allows us
to conveniently capture a "witness" for an ``any()`` expression, or a
counterexample for ``all()``, for example

この特別な場合の動機は2つあります。 まず、 ``any()`` 式の「目撃者」、または ``all()`` の反例を簡単に捉えることができます。例えば、::

    if any((comment := line).startswith('#') for line in lines):
        print("First comment:", comment)
    else:
        print("There are no comments")

    if all((nonblank := line).strip() == '' for line in lines):
        print("All lines are blank")
    else:
        print("First non-blank line:", nonblank)

Second, it allows a compact way of updating mutable state from a
comprehension, for example

第二に、それは内包から可変状態を更新するコンパクトな方法を可能にします、例えば::

    # Compute partial sums in a list comprehension
    total = 0
    partial_sums = [total := total + v for v in values]
    print("Total:", total)

However, an assignment expression target name cannot be the same as a
``for``-target name appearing in any comprehension containing the
assignment expression.  The latter names are local to the
comprehension in which they appear, so it would be contradictory for a
contained use of the same name to refer to the scope containing the
outermost comprehension instead.

しかし、代入式のターゲット名は、代入式を含む内包表記に現れる ``for``-target 名と同じにすることはできません。 後者の名前はそれらが現れる理解に対して局所的であるので、同じ名前の含まれた使用が代わりに最も外側の理解を含む範囲を参照することは矛盾するでしょう。

For example, ``[i := i+1 for i in range(5)]`` is invalid: the ``for
i`` part establishes that ``i`` is local to the comprehension, but the
``i :=`` part insists that ``i`` is not local to the comprehension.
The same reason makes these examples invalid too

例えば、 ``[i:= i + 1 in range（5）]`` は無効です: ``for i`` 部分は、 ``i`` が内包に対してローカルであることを確立しますが、 ``i:= `` partは、 ``i`` は内包に対してローカルではないと主張します。同じ理由でこれらの例も無効になります::

    [[(j := j) for i in range(5)] for j in range(5)]
    [i := 0 for i, j in stuff]
    [i+1 for i in i := stuff]

A further exception applies when an assignment expression occurs in a
comprehension whose containing scope is a class scope.  If the rules
above were to result in the target being assigned in that class's
scope, the assignment expression is expressly invalid.

代入式が包含範囲がクラスの範囲である内包表記の中に現れる場合には、さらに別の例外が適用されます。 上記の規則によってターゲットがそのクラスのスコープ内に割り当てられることになった場合、代入式は明示的に無効です。

(The reason for the latter exception is the implicit function created
for comprehensions -- there is currently no runtime mechanism for a
function to refer to a variable in the containing class scope, and we
do not want to add such a mechanism.  If this issue ever gets resolved
this special case may be removed from the specification of assignment
expressions.  Note that the problem already exists for *using* a
variable defined in the class scope from a comprehension.)

（後者の例外の理由は、内包のために作成された暗黙の関数です。現在、関数が含んでいるクラススコープ内の変数を参照するための実行時機構はありません。そのような機構を追加したくありません。 この特別な場合は代入式の指定から取り除かれるかもしれません。問題は内包からクラススコープで定義された変数を* using *に使うことで既に存在していることに注意してください。）

See Appendix B for some examples of how the rules for targets in
comprehensions translate to equivalent code.

内包内のターゲットの規則が同等のコードに変換される方法の例については、付録Bを参照してください。

The two invalid cases listed above raise ``TargetScopeError``, a
new subclass of ``SyntaxError`` (with the same signature).

上に挙げた2つの無効なケースは、(``SyntaxError``) の新しいサブクラスである ``TargetScopeError`` （同じシグネチャを持つ）を発生させます。

Relative precedence of ``:=``
-----------------------------

The ``:=`` operator groups more tightly than a comma in all syntactic
positions where it is legal, but less tightly than all other operators,
including ``or``, ``and``, ``not``, and conditional expressions
(``A if C else B``).  As follows from section
"Exceptional cases" above, it is never allowed at the same level as
``=``.  In case a different grouping is desired, parentheses should be
used.

``:= `` 演算子は、それが有効なすべての構文上の位置でコンマよりも厳密にグループ化されますが、 ``or`` 、 ``and`` 、 ``not`` と条件式 (``AならC、それ以外ならB``)を含む他のすべての演算子よりも厳密にグループ化されません。上記の「例外的なケース」からわかるように、それは ``=`` と同じレベルでは許されません。異なるグループ化が必要な場合は、括弧を使用してください。

The ``:=`` operator may be used directly in a positional function call
argument; however it is invalid directly in a keyword argument.

``:= `` 演算子は定位置関数呼び出し引数で直接使用できます。ただし、キーワード引数では直接無効です。

Some examples to clarify what's technically valid or invalid

技術的に有効なものと無効なものを明確にするための例::

    # INVALID
    x := 0

    # Valid alternative
    (x := 0)

    # INVALID
    x = y := 0

    # Valid alternative
    x = (y := 0)

    # Valid
    len(lines := f.readlines())

    # Valid
    foo(x := 3, cat='vector')

    # INVALID
    foo(cat=category := 'vector')

    # Valid alternative
    foo(cat=(category := 'vector'))

Most of the "valid" examples above are not recommended, since human
readers of Python source code who are quickly glancing at some code
may miss the distinction.  But simple cases are not objectionable

上の「有効な」例のほとんどは推奨されていません。なぜなら、あるコードを素早くちらっと見ているPythonソースコードの人間の読者は区別を見逃すかもしれないからです。しかし、単純な場合は不快ではありません::

    # Valid
    if any(len(longline := line) >= 100 for line in lines):
        print("Extremely long line:", longline)

This PEP recommends always putting spaces around ``:=``, similar to
PEP 8's recommendation for ``=`` when used for assignment, whereas the
latter disallows spaces around ``=`` used for keyword arguments.)

このPEPは代入に使われるときのPEP 8の ``=`` の推奨と同様に、常に ``:= ``の周りにスペースを入れることを推奨します。

Change to evaluation order
--------------------------

In order to have precisely defined semantics, the proposal requires
evaluation order to be well-defined.  This is technically not a new
requirement, as function calls may already have side effects.  Python
already has a rule that subexpressions are generally evaluated from
left to right.  However, assignment expressions make these side
effects more visible, and we propose a single change to the current
evaluation order

セマンティクスを正確に定義するために、このプロポーザルは評価順序を明確に定義する必要があります。 関数呼び出しには既に副作用があるため、これは技術的には新しい要件ではありません。 Pythonはすでに部分式は一般に左から右に評価されるという規則をすでに持っています。 しかしながら、代入式はこれらの副作用をより目に見えるようにします、そして我々は現在の評価順序への1つだけ変更を提案します:

- In a dict comprehension ``{X: Y for ...}``, ``Y`` is currently
  evaluated before ``X``.  We propose to change this so that ``X`` is
  evaluated before ``Y``.  (In a dict display like ``{X: Y}`` this is
  already the case, and also in ``dict((X, Y) for ...)`` which should
  clearly be equivalent to the dict comprehension.)

  辞書内包表記 ``{X:Y for ...}`` では、 ``Y`` は現在 ``X`` の前に評価されています。
  これを変更して、 ``X`` が ``Y`` の前に評価されるようにすることを提案します。
  (``{X:Y}`` のような辞書表示では、これはすでに当てはまります。また ``dict((X,Y) for ...)`` でも、これは辞書の解釈と明らかに等価です)

Differences between  assignment expressions and assignment statements
---------------------------------------------------------------------

Most importantly, since ``:=`` is an expression, it can be used in contexts
where statements are illegal, including lambda functions and comprehensions.

最も重要なのは、 ``:=`` は式なので、ラムダ関数や内包表記など、文が不正な文脈で使用できることです。

Conversely, assignment expressions don't support the advanced features
found in assignment statements

逆に、代入式は代入文にある高度な機能をサポートしていません:

- Multiple targets are not directly supported

  複数のターゲットは直接サポートされていません::

    x = y = z = 0  # Equivalent: (z := (y := (x := 0)))

- Single assignment targets other than a single ``NAME`` are
  not supported

  単一の ``NAME`` 以外の単一代入ターゲットはサポートされていません::

    # No equivalent
    a[i] = x
    self.rest = []

- Priority around commas is different

  コンマ周辺の優先順位が違います::

    x = 1, 2  # Sets x to (1, 2)
    (x := 1, 2)  # Sets x to 1

- Iterable packing and unpacking (both regular or extended forms) are
  not supported

  Iterableのパッキングとアンパッキングは、通常形式でも拡張形式でも、はサポートされていません::

    # Equivalent needs extra parentheses
    loc = x, y  # Use (loc := (x, y))
    info = name, phone, *rest  # Use (info := (name, phone, *rest))

    # No equivalent
    px, py, pz = position
    name, phone, email, *other_info = contact

- Inline type annotations are not supported

  インライン型アノテーションはサポートされていません::

    # Closest equivalent is "p: Optional[int]" as a separate declaration
    p: Optional[int] = None

- Augmented assignment is not supported

  拡張割り当てはサポートされていません::

    total += tax  # Equivalent: (total := total + tax)


Examples
========

Examples from the Python standard library
-----------------------------------------

site.py
^^^^^^^

*env_base* is only used on these lines, putting its assignment on the if
moves it as the "header" of the block.

*env_base* はこれらの行でのみ使用され、その代入をifに置くとブロックの「ヘッダ」として移動します。

- Current::

    env_base = os.environ.get("PYTHONUSERBASE", None)
    if env_base:
        return env_base

- Improved::

    if env_base := os.environ.get("PYTHONUSERBASE", None):
        return env_base

_pydecimal.py
^^^^^^^^^^^^^

Avoid nested ``if`` and remove one indentation level.

入れ子になった ``if`` を避けて、インデントレベルを1つ削除します。

- Current::

    if self._is_special:
        ans = self._check_nans(context=context)
        if ans:
            return ans

- Improved::

    if self._is_special and (ans := self._check_nans(context=context)):
        return ans

copy.py
^^^^^^^

Code looks more regular and avoid multiple nested if.
(See Appendix A for the origin of this example.)

コードはより規則的に見え、複数のifをネストせずに済みます。
（この例の由来については付録Aを参照してください。）

- Current::

    reductor = dispatch_table.get(cls)
    if reductor:
        rv = reductor(x)
    else:
        reductor = getattr(x, "__reduce_ex__", None)
        if reductor:
            rv = reductor(4)
        else:
            reductor = getattr(x, "__reduce__", None)
            if reductor:
                rv = reductor()
            else:
                raise Error(
                    "un(deep)copyable object of type %s" % cls)

- Improved::

    if reductor := dispatch_table.get(cls):
        rv = reductor(x)
    elif reductor := getattr(x, "__reduce_ex__", None):
        rv = reductor(4)
    elif reductor := getattr(x, "__reduce__", None):
        rv = reductor()
    else:
        raise Error("un(deep)copyable object of type %s" % cls)

datetime.py
^^^^^^^^^^^

*tz* is only used for ``s += tz``, moving its assignment inside the if
helps to show its scope.

*tz* は ``s + = tz`` 対してのみ使用され、その代入をifの内側に移動するとその範囲を示すのに役立ちます。

- Current::

    s = _format_time(self._hour, self._minute,
                     self._second, self._microsecond,
                     timespec)
    tz = self._tzstr()
    if tz:
        s += tz
    return s

- Improved::

    s = _format_time(self._hour, self._minute,
                     self._second, self._microsecond,
                     timespec)
    if tz := self._tzstr():
        s += tz
    return s

sysconfig.py
^^^^^^^^^^^^

Calling ``fp.readline()`` in the ``while`` condition and calling
``.match()`` on the if lines make the code more compact without making
it harder to understand.

``while`` の文脈で ``fp.readline()`` を呼び出し、if行で ``.match()`` を呼び出すことで、理解を難しくすることなくコードをよりコンパクトにします。

- Current::

    while True:
        line = fp.readline()
        if not line:
            break
        m = define_rx.match(line)
        if m:
            n, v = m.group(1, 2)
            try:
                v = int(v)
            except ValueError:
                pass
            vars[n] = v
        else:
            m = undef_rx.match(line)
            if m:
                vars[m.group(1)] = 0

- Improved::

    while line := fp.readline():
        if m := define_rx.match(line):
            n, v = m.group(1, 2)
            try:
                v = int(v)
            except ValueError:
                pass
            vars[n] = v
        elif m := undef_rx.match(line):
            vars[m.group(1)] = 0


Simplifying list comprehensions
-------------------------------

A list comprehension can map and filter efficiently by capturing
the condition

リスト内包表記は、条件を取り込むことによって効率的にmap/filterできます::

    results = [(x, y, x/y) for x in input_data if (y := f(x)) > 0]

Similarly, a subexpression can be reused within the main expression, by
giving it a name on first use

同様に、最初の使用時にsubexpressionに名前を付けることで、mainexpression内でsubexpressionを再利用できます::

    stuff = [[y := f(x), x/y] for x in range(5)]

Note that in both cases the variable ``y`` is bound in the containing
scope (i.e. at the same level as ``results`` or ``stuff``).

どちらの場合も、変数 ``y`` はそれを含んでいるスコープの中で、つまり ``results`` や ``stuff`` と同じレベルで、バインドされていることに注意してください。

Capturing condition values
--------------------------

Assignment expressions can be used to good effect in the header of
an ``if`` or ``while`` statement

代入式は、 ``if`` または ``while`` ステートメントのヘッダで効果的に使用することができます。::

    # Loop-and-a-half
    while (command := input("> ")) != "quit":
        print("You entered:", command)

    # Capturing regular expression match objects
    # See, for instance, Lib/pydoc.py, which uses a multiline spelling
    # of this effect
    if match := re.search(pat, text):
        print("Found:", match.group(0))
    # The same syntax chains nicely into 'elif' statements, unlike the
    # equivalent using assignment statements.
    elif match := re.search(otherpat, text):
        print("Alternate found:", match.group(0))
    elif match := re.search(third, text):
        print("Fallback found:", match.group(0))

    # Reading socket data until an empty string is returned
    while data := sock.recv(8192):
        print("Received data:", data)

Particularly with the ``while`` loop, this can remove the need to have an
infinite loop, an assignment, and a condition. It also creates a smooth
parallel between a loop which simply uses a function call as its condition,
and one which uses that as its condition but also uses the actual value.

特に ``while`` ループの場合には無限ループで条件を代入しておく必要性をなくすことができます。また、単純に関数呼び出しをその条件として使用するループと、それをその条件として使用するが実際の値も使用するループとの間に滑らかな並列処理を作成します。

Fork
----

An example from the low-level UNIX world::

    if pid := os.fork():
        # Parent code
    else:
        # Child code


Rejected alternative proposals
==============================

Proposals broadly similar to this one have come up frequently on python-ideas.
Below are a number of alternative syntaxes, some of them specific to
comprehensions, which have been rejected in favour of the one given above.

これと広く似たプロポーザルがpython-ideasに頻繁に出ています。 以下はいくつかの代替構文で、そのうちのいくつかは内包表記に固有のもので、上記の構文を支持して却下されています。

Changing the scope rules for comprehensions
-------------------------------------------

A previous version of this PEP proposed subtle changes to the scope
rules for comprehensions, to make them more usable in class scope and
to unify the scope of the "outermost iterable" and the rest of the
comprehension.  However, this part of the proposal would have caused
backwards incompatibilities, and has been withdrawn so the PEP can
focus on assignment expressions.

このPEPの以前のバージョンは、クラススコープ内でスコープルールをより使いやすくし、「最も外側の反復可能」のスコープと残りの理解を統一するために、スコープルールの微妙な変更を提案しました。 しかし、プロポーザルのこの部分では後方互換性がないため、PEPが代入式に焦点を当てることができるように撤回されました。

Alternative spellings
---------------------

Broadly the same semantics as the current proposal, but spelled differently.

現在のプロポーザルとほぼ同じ意味ですが、スペルが異なります。

1. ``EXPR as NAME``::

       stuff = [[f(x) as y, x/y] for x in range(5)]

   Since ``EXPR as NAME`` already has meaning in ``import``,
   ``except`` and ``with`` statements (with different semantics), this
   would create unnecessary confusion or require special-casing
   (e.g. to forbid assignment within the headers of these statements).

   ``EXPR as NAME`` は ``import`` 、 ``except`` 、 ``with`` 文の中で既に意味を持っているので（別のセマンティクスで）、これは不必要な混乱を招くか、または特別なケースを要求するでしょう（例えばこれらのステートメントのヘッダー内の割り当ての禁止）。

   (Note that ``with EXPR as VAR`` does *not* simply assign the value
   of ``EXPR`` to ``VAR`` -- it calls ``EXPR.__enter__()`` and assigns
   the result of *that* to ``VAR``.)

   (``EXPR with VAR`` は単に ``EXPR`` の値を ``VAR`` に割り当てるのではなく、 ``EXPR .__enter__()`` の結果を ``VAR`` に代入します）

   Additional reasons to prefer ``:=`` over this spelling include

   このスペルよりも ``:=`` を好む追加の理由には以下のものがあります:

   - In ``if f(x) as y`` the assignment target doesn't jump out at you
     -- it just reads like ``if f x blah blah`` and it is too similar
     visually to ``if f(x) and y``.

     ``if f（x）as y`` では代入先はあなたの目に飛び込んでこない - 単に ``if fx blah blah`` のようになり、視覚的には ``if f(x) and y`` と似すぎている。

   - In all other situations where an ``as`` clause is allowed, even
     readers with intermediary skills are led to anticipate that
     clause (however optional) by the keyword that starts the line,
     and the grammar ties that keyword closely to the as clause

     as句が許される他のすべての状況では、中級スキルを持つ読者でさえその行を始めるキーワードによってその句を予測するように導かれます（文法はas句にそのキーワードを密接に結び付けます）:

     - ``import foo as bar``
     - ``except Exc as var``
     - ``with ctxmgr() as var``

     To the contrary, the assignment expression does not belong to the
     ``if`` or ``while`` that starts the line, and we intentionally
     allow assignment expressions in other contexts as well.

     反対に、代入式は行を開始する ``if`` や ``while`` には属しません。他の文脈でも代入式を意図的に許可します。

   - The parallel cadence between

     次のものが並行した感じ

     - ``NAME = EXPR``
     - ``if NAME := EXPR``

     reinforces the visual recognition of assignment expressions.

     代入表現の視覚的認識を強化します。

2. ``EXPR -> NAME``::

       stuff = [[f(x) -> y, x/y] for x in range(5)]

   This syntax is inspired by languages such as R and Haskell, and some
   programmable calculators. (Note that a left-facing arrow ``y <- f(x)`` is
   not possible in Python, as it would be interpreted as less-than and unary
   minus.) This syntax has a slight advantage over 'as' in that it does not
   conflict with ``with``, ``except`` and ``import``, but otherwise is
   equivalent.  But it is entirely unrelated to Python's other use of
   ``->`` (function return type annotations), and compared to ``:=``
   (which dates back to Algol-58) it has a much weaker tradition.

   この構文は、RやHaskellなどの言語、およびいくつかのプログラム可能な計算機に触発されています。 （左向きの矢印 ``y <-  f(x)`` は、小なりマイナス単項マイナスとして解釈されるため、Pythonでは使用できないことに注意してください）。 それが ``with`` 、 ``except`` および ``import`` と衝突しないこと、それ以外は同等です。 しかし、Pythonが他の ``->`` （関数戻り型アノテーション）を使用することとは全く関係がなく、 ``:=`` （Algol-58までさかのぼる）と比較すると、はるかに弱い伝統があります。

3. Adorning statement-local names with a leading dot

  先頭にドットを付けてステートメントローカル名を修飾する::

       stuff = [[(f(x) as .y), x/.y] for x in range(5)] # with "as"
       stuff = [[(.y := f(x)), x/.y] for x in range(5)] # with ":="

   This has the advantage that leaked usage can be readily detected, removing
   some forms of syntactic ambiguity.  However, this would be the only place
   in Python where a variable's scope is encoded into its name, making
   refactoring harder.

   これには、リークされた使用法を簡単に検出できるという利点があり、構文上のあいまいさが解消されます。 ただし、これがPythonの唯一の場所で、変数のスコープが名前にエンコードされているため、リファクタリングが難しくなります。

4. Adding a ``where:`` to any statement to create local name bindings

  ローカルな名前の束縛を作成するために任意のステートメントに ``where: `` を追加する::

       value = x**2 + 2*x where:
           x = spam(1, 4, 7, q)

   Execution order is inverted (the indented body is performed first, followed
   by the "header").  This requires a new keyword, unless an existing keyword
   is repurposed (most likely ``with:``).  See PEP 3150 for prior discussion
   on this subject (with the proposed keyword being ``given:``).

   実行順序が逆になります（インデントされた本文が最初に実行され、その後に "header"が続きます）。 既存のキーワードが再利用されない限り、これは新しいキーワードを必要とします（おそらく ``with: `` ）。 この主題に関する以前の議論についてはPEP 3150を参照してください（提案されたキーワードは ``given: `` です）。

5. ``TARGET from EXPR``::

       stuff = [[y from f(x), x/y] for x in range(5)]

   This syntax has fewer conflicts than ``as`` does (conflicting only with the
   ``raise Exc from Exc`` notation), but is otherwise comparable to it. Instead
   of paralleling ``with expr as target:`` (which can be useful but can also be
   confusing), this has no parallels, but is evocative.

   この構文は ``as`` よりも衝突が少ないです（ ``Exc from from Exc`` 表記とのみ衝突します）が、それ以外はそれと同等です。 ``with expr as target:`` を並列化する代わりに（これは便利かもしれませんが混乱するかもしれません）、これには並行性はありませんが、イノベーティブです。


Special-casing conditional statements
-------------------------------------

One of the most popular use-cases is ``if`` and ``while`` statements.  Instead
of a more general solution, this proposal enhances the syntax of these two
statements to add a means of capturing the compared value

最も一般的なユースケースの1つは、 ``if`` と ``while`` ステートメントです。 より一般的な解決策の代わりに、この提案は比較された値を捉える手段を追加するためにこれら二つのステートメントの構文を強化します::

    if re.search(pat, text) as match:
        print("Found:", match.group(0))

This works beautifully if and ONLY if the desired condition is based on the
truthiness of the captured value.  It is thus effective for specific
use-cases (regex matches, socket reads that return `''` when done), and
completely useless in more complicated cases (e.g. where the condition is
``f(x) < 0`` and you want to capture the value of ``f(x)``).  It also has
no benefit to list comprehensions.

これは、必要な条件が取得した値の真実性に基づいている場合に限り、美しく機能します。 したがって、これは特定のユースケースにのみ有効です（正規表現の一致、終了したときに `''` を返すソケットの読み込み）、そしてより複雑なケースに関しては完全に役に立ちません（コンディションが ``f(x) <0`` で ``f(x)`` の値をキャプチャーしたい場合など）リスト内包表記にも利点はありません。

Advantages: No syntactic ambiguities. Disadvantages: Answers only a fraction
of possible use-cases, even in ``if``/``while`` statements.

利点：構文上のあいまいさがありません。 デメリット： ``if`` / ``while`` ステートメントであっても、可能なユースケースのごく一部にしか答えない。

Special-casing comprehensions
-----------------------------

Another common use-case is comprehensions (list/set/dict, and genexps). As
above, proposals have been made for comprehension-specific solutions.

もう1つの一般的なユースケースは内包表記（list / set / dict、およびgenexps）です。 上記のように、理解固有の解決策についての提案がなされてきた。

1. ``where``, ``let``, or ``given``::

       stuff = [(y, x/y) where y = f(x) for x in range(5)]
       stuff = [(y, x/y) let y = f(x) for x in range(5)]
       stuff = [(y, x/y) given y = f(x) for x in range(5)]

   This brings the subexpression to a location in between the 'for' loop and
   the expression. It introduces an additional language keyword, which creates
   conflicts. Of the three, ``where`` reads the most cleanly, but also has the
   greatest potential for conflict (e.g. SQLAlchemy and numpy have ``where``
   methods, as does ``tkinter.dnd.Icon`` in the standard library).

   これにより、 'for' ループと式の間にある部分式が表示されます。 それは追加の言語キーワードを導入します、それは衝突を引き起こします。 3つのうち、 ``where`` は最もきれいに読みますが、競合の可能性が最も大きいです（例えば、標準ライブラリの ``tkinter.dnd.Icon`` のように、SQLAlchemyとnumpyは ``where`` メソッドを持ちます。 ）

2. ``with NAME = EXPR``::

       stuff = [(y, x/y) with y = f(x) for x in range(5)]

   As above, but reusing the ``with`` keyword. Doesn't read too badly, and needs
   no additional language keyword. Is restricted to comprehensions, though,
   and cannot as easily be transformed into "longhand" for-loop syntax. Has
   the C problem that an equals sign in an expression can now create a name
   binding, rather than performing a comparison. Would raise the question of
   why "with NAME = EXPR:" cannot be used as a statement on its own.

   上記と同じですが、 ``with`` キーワードを再利用します。 ひどく読むことはなく、追加の言語キーワードも必要ありません。 ただし、内包表記に限定されており、「簡単な」forループ構文に簡単に変換することはできません。 式の中の等号が比較を実行するのではなく、名前バインディングを作成できるというCの問題があります。 ``with NAME = EXPR:`` を単独で文として使用できないのはなぜかという疑問が生じます。

3. ``with EXPR as NAME``::

       stuff = [(y, x/y) with f(x) as y for x in range(5)]

   As per option 2, but using ``as`` rather than an equals sign. Aligns
   syntactically with other uses of ``as`` for name binding, but a simple
   transformation to for-loop longhand would create drastically different
   semantics; the meaning of ``with`` inside a comprehension would be
   completely different from the meaning as a stand-alone statement, while
   retaining identical syntax.

   オプション2と同じですが、等号の代わりに ``as`` を使います。 名前のバインドのための ``as`` の他の使い方と構文的に揃えますが、for-loop longhandへの単純な変換は劇的に異なる意味を作り出します。 内包内の ``with`` の意味は、同一の文法を保持しながら、独立したステートメントとしての意味とは完全に異なるでしょう。

Regardless of the spelling chosen, this introduces a stark difference between
comprehensions and the equivalent unrolled long-hand form of the loop.  It is
no longer possible to unwrap the loop into statement form without reworking
any name bindings.  The only keyword that can be repurposed to this task is
``with``, thus giving it sneakily different semantics in a comprehension than
in a statement; alternatively, a new keyword is needed, with all the costs
therein.

選択したスペルに関係なく、これは内包表記と同等の展開された長い形式のループとの間に大きな違いをもたらします。 名前の束縛をやり直さずにループをステートメント形式に展開することはできなくなりました。 このタスクに再利用できる唯一のキーワードは ``with`` なので、ステートメント内と内包内では意味の異なる意味があります。 あるいは、新しいキーワードが必要で、その中にすべてのコストが含まれています。

Lowering operator precedence
----------------------------

There are two logical precedences for the ``:=`` operator. Either it should
bind as loosely as possible, as does statement-assignment; or it should bind
more tightly than comparison operators. Placing its precedence between the
comparison and arithmetic operators (to be precise: just lower than bitwise
OR) allows most uses inside ``while`` and ``if`` conditions to be spelled
without parentheses, as it is most likely that you wish to capture the value
of something, then perform a comparison on it::

``:=`` 演算子には2つの論理的な優先順位があります。 文割り当てと同様に、可能な限り緩やかにバインドする必要があります。 または比較演算子よりも緊密にバインドする必要があります。比較演算子と算術演算子の間に優先順位を置く（正確には:ビット単位のORよりもわずかに低い）ことで、ほとんどの場合、 ``while`` および ``if`` 条件内の使用は括弧なしで綴ることができます 何かの価値を捉え、それからそれを比較する

    pos = -1
    while pos := buffer.find(search_term, pos + 1) >= 0:
        ...

Once find() returns -1, the loop terminates. If ``:=`` binds as loosely as
``=`` does, this would capture the result of the comparison (generally either
``True`` or ``False``), which is less useful.

find() が-1を返すと、ループは終了します。 ``:=`` が ``=`` と同程度に緩く結合している場合、これは比較の結果（通常は ``True`` または ``False`` のどちらか）を捉えますが、それほど役に立ちません。

While this behaviour would be convenient in many situations, it is also harder
to explain than "the := operator behaves just like the assignment statement",
and as such, the precedence for ``:=`` has been made as close as possible to
that of ``=`` (with the exception that it binds tighter than comma).

この振る舞いは多くの状況で便利ですが、 ":= 演算子は代入文のように振る舞う" よりも説明するのが難しく、そのため、 ``:=`` の優先順位をできるだけ近づけています。 コンマよりも束縛されていることを除いて、 ``=`` と同じです。


Allowing commas to the right
----------------------------

Some critics have claimed that the assignment expressions should allow
unparenthesized tuples on the right, so that these two would be equivalent

何人かの批評家は、代入式は右辺の括弧で囲まれていないタプルを許すべきであると主張しました。::

    (point := (x, y))
    (point := x, y)

(With the current version of the proposal, the latter would be
equivalent to ``((point := x), y)``.)

（現在のバージョンの提案では、後者は ``((point:= x),y)`` と同等です。）

However, adopting this stance would logically lead to the conclusion
that when used in a function call, assignment expressions also bind
less tight than comma, so we'd have the following confusing equivalence

しかし、このスタンスを採用することは、論理的には、関数呼び出しで使用された場合、代入式がコンマよりもタイトにバインドされているという結論につながります。::

    foo(x := 1, y)
    foo(x := (1, y))

The less confusing option is to make ``:=`` bind more tightly than comma.

混乱を招くことの少ないオプションは、 ``:= `` をコンマよりも強くバインドすることです。


Always requiring parentheses
----------------------------

It's been proposed to just always require parenthesize around an
assignment expression.  This would resolve many ambiguities, and
indeed parentheses will frequently be needed to extract the desired
subexpression.  But in the following cases the extra parentheses feel
redundant

代入式を括弧で囲むことを常に要求することが提案されています。 これは多くのあいまいさを解決するでしょう、そして確かに括弧はしばしば望ましい部分式を抽出するために必要とされるでしょう。 しかし、次のような場合、余分な括弧は冗長に感じます::

    # Top level in if
    if match := pattern.match(line):
        return match.group(1)

    # Short call
    len(lines := f.readlines())


Frequently Raised Objections
============================

Why not just turn existing assignment into an expression?
---------------------------------------------------------

C and its derivatives define the ``=`` operator as an expression, rather than
a statement as is Python's way.  This allows assignments in more contexts,
including contexts where comparisons are more common.  The syntactic similarity
between ``if (x == y)`` and ``if (x = y)`` belies their drastically different
semantics.  Thus this proposal uses ``:=`` to clarify the distinction.

Cとその派生物はPythonのやり方のようにステートメントではなく式として ``=`` 演算子を定義します。 これにより、比較がより一般的なコンテキストを含む、より多くのコンテキストでの割り当てが可能になります。 ``if(x == y)``と ``if(x = y)`` の間の構文上の類似性は、まったく異なるセマンティクスを裏付けています。 したがって、この提案は区別を明確にするために ``:=`` を使用します。

With assignment expressions, why bother with assignment statements?
-------------------------------------------------------------------

The two forms have different flexibilities.  The ``:=`` operator can be used
inside a larger expression; the ``=`` statement can be augmented to ``+=`` and
its friends, can be chained, and can assign to attributes and subscripts.

2つの形式は異なる柔軟性を持っています。 ``:=`` 演算子は大きな式の中で使うことができます。 ``=`` ステートメントは ``+=`` とその仲間に拡張することができ、連鎖させ、属性や添え字に代入することができます。

Why not use a sublocal scope and prevent namespace pollution?
-------------------------------------------------------------

Previous revisions of this proposal involved sublocal scope (restricted to a
single statement), preventing name leakage and namespace pollution.  While a
definite advantage in a number of situations, this increases complexity in
many others, and the costs are not justified by the benefits. In the interests
of language simplicity, the name bindings created here are exactly equivalent
to any other name bindings, including that usage at class or module scope will
create externally-visible names.  This is no different from ``for`` loops or
other constructs, and can be solved the same way: ``del`` the name once it is
no longer needed, or prefix it with an underscore.

この提案の以前の改訂は、名前の漏洩と名前空間の汚染を防ぐために、（単一のステートメントに限定された）サブローカルスコープを含んでいました。 多くの状況で明確な利点がありますが、他の多くの状況ではこれが複雑さを増し、その利点によってコストが正当化されるわけではありません。 言語を簡単にするために、ここで作成された名前バインディングは、クラスまたはモジュールスコープでの使用が外部から見える名前を作成することを含め、他の名前バインディングとまったく同じです。 これは ``for`` ループや他の構成要素と同じで、同じように解決できます。必要でなくなったら ``del`` の名前を付けるか、またはアンダースコアを前に付けます。

(The author wishes to thank Guido van Rossum and Christoph Groth for their
suggestions to move the proposal in this direction. [2]_)

（著者はこの方向に提案を進めるための彼らの提案についてGuido van RossumとChristoph Grothに感謝します。[2] _）

Style guide recommendations
===========================

As expression assignments can sometimes be used equivalently to statement
assignments, the question of which should be preferred will arise. For the
benefit of style guides such as PEP 8, two recommendations are suggested.

式の代入は文の代入と同等に使用できることがあるため、どちらを優先するかが問題になります。 PEP 8のようなスタイルガイドの利益のために、2つの勧告が提案されています。

1. If either assignment statements or assignment expressions can be
   used, prefer statements; they are a clear declaration of intent.

   代入文または代入式のいずれかを使用できる場合は、文を優先してください。 彼らは意図の明確な宣言です。

2. If using assignment expressions would lead to ambiguity about
   execution order, restructure it to use statements instead.

   代入式を使用すると実行順序があいまいになる場合は、代わりに文を使用するように再構成してください。


Acknowledgements
================

The authors wish to thank Nick Coghlan and Steven D'Aprano for their
considerable contributions to this proposal, and members of the
core-mentorship mailing list for assistance with implementation.

作者は、この提案への多大なる貢献と、実施支援のためのコアメンターシップメーリングリストのメンバーであるNick CoghlanとSteven D'Apranoに感謝します。

Appendix A: Tim Peters's findings
=================================

Here's a brief essay Tim Peters wrote on the topic.

これがTim Petersがこのトピックについて書いた簡単なエッセイです。

I dislike "busy" lines of code, and also dislike putting conceptually
unrelated logic on a single line.  So, for example, instead of::

私は「忙しい」コード行が嫌いで、概念的に関係のないロジックを1行に置くのも嫌いです。 だから、例えば、の代わりに

    i = j = count = nerrors = 0

I prefer::

    i = j = 0
    count = 0
    nerrors = 0

instead.  So I suspected I'd find few places I'd want to use
assignment expressions.  I didn't even consider them for lines already
stretching halfway across the screen.  In other cases, "unrelated"
ruled

代わりに。 そのため、代入式を使用したい場所がいくつかあると思います。 私はそれらをスクリーンの向こう側にすでに伸びている線のためにさえ考えなかった。 他の場合では、「無関係な」判決::

    mylast = mylast[1]
    yield mylast[0]

is a vast improvement over the briefer

参照者に対する大幅な改善です。::

    yield (mylast := mylast[1])[0]

The original two statements are doing entirely different conceptual
things, and slamming them together is conceptually insane.

最初の2つのステートメントはまったく異なる概念的なことをしています、そしてそれらを一緒にスラミングすることは概念的には不可解です。

In other cases, combining related logic made it harder to understand,
such as rewriting

他の場合では、関連するロジックを組み合わせると、書き換えなど理解しにくくなります。::

    while True:
        old = total
        total += term
        if old == total:
            return total
        term *= mx2 / (i*(i+1))
        i += 2

as the briefer

より簡単な::

    while total != (total := total + term):
        term *= mx2 / (i*(i+1))
        i += 2
    return total

The ``while`` test there is too subtle, crucially relying on strict
left-to-right evaluation in a non-short-circuiting or method-chaining
context.  My brain isn't wired that way.

ここでの ``while`` テストは微妙すぎ、重大なことに非短絡またはメソッド連鎖の文脈における厳密な左から右への評価に頼っています。 私の脳はそのように配線されていません。

But cases like that were rare.  Name binding is very frequent, and
"sparse is better than dense" does not mean "almost empty is better
than sparse".  For example, I have many functions that return ``None``
or ``0`` to communicate "I have nothing useful to return in this case,
but since that's expected often I'm not going to annoy you with an
exception".  This is essentially the same as regular expression search
functions returning ``None`` when there is no match.  So there was lots
of code of the form

しかし、そのようなケースはまれでした。 名前のバインディングは非常に頻繁であり、「疎は密よりも優れている」という意味では「ほとんど空の方が疎よりも優れている」という意味ではありません。 例えば、私はコミュニケーションのために `` None``や `` 0``を返す関数をたくさん持っています。「この場合、返すのに役立つものは何もありませんが、例外が発生して煩わされることはないでしょう」 。 これは、正規表現検索関数がマッチしないときに `` None``を返すのと本質的に同じです。 それで、フォームのコードがたくさんありました::

    result = solution(xs, n)
    if result:
        # use result

I find that clearer, and certainly a bit less typing and
pattern-matching reading, as

私はそれをより明確に、そして確かに少し少ないタイピングとパターンマッチングの読みを見つけます、::

    if result := solution(xs, n):
        # use result

It's also nice to trade away a small amount of horizontal whitespace
to get another _line_ of surrounding code on screen.  I didn't give
much weight to this at first, but it was so very frequent it added up,
and I soon enough became annoyed that I couldn't actually run the
briefer code.  That surprised me!

画面上の周囲のコードの別の_line_を取得するために、少量の水平方向の空白を削除するのもいいでしょう。 最初はあまり重視していませんでしたが、非常に頻繁に追加されたため、すぐに十分なイライラを起こして実際に簡単なコードを実行できなくなりました。 それは私を驚かせた！

There are other cases where assignment expressions really shine.
Rather than pick another from my code, Kirill Balunov gave a lovely
example from the standard library's ``copy()`` function in ``copy.py``

代入式が本当に輝く他のケースがあります。 私のコードから別のコードを選ぶのではなく、Kirill Balunovさんが標準ライブラリの ``copy.py`` の中の ``copy()`` 関数から素敵な例を挙げました::

    reductor = dispatch_table.get(cls)
    if reductor:
        rv = reductor(x)
    else:
        reductor = getattr(x, "__reduce_ex__", None)
        if reductor:
            rv = reductor(4)
        else:
            reductor = getattr(x, "__reduce__", None)
            if reductor:
                rv = reductor()
            else:
                raise Error("un(shallow)copyable object of type %s" % cls)

The ever-increasing indentation is semantically misleading: the logic
is conceptually flat, "the first test that succeeds wins"

増え続けるインデントは意味的に誤解を招くものです。論理は概念的にフラットで、「最初に成功したテストが勝利する」::

    if reductor := dispatch_table.get(cls):
        rv = reductor(x)
    elif reductor := getattr(x, "__reduce_ex__", None):
        rv = reductor(4)
    elif reductor := getattr(x, "__reduce__", None):
        rv = reductor()
    else:
        raise Error("un(shallow)copyable object of type %s" % cls)

Using easy assignment expressions allows the visual structure of the
code to emphasize the conceptual flatness of the logic;
ever-increasing indentation obscured it.

簡単な代入式を使用すると、コードの視覚的な構造で論理の概念的な平坦性を強調できます。 増え続けるインデントはそれを覆い隠しました。

A smaller example from my code delighted me, both allowing to put
inherently related logic in a single line, and allowing to remove an
annoying "artificial" indentation level

私のコードからのより小さな例は私を楽しませました、両方とも本質的に関連した論理を単一行に入れることを可能にして、そして迷惑な「人工的な」インデントレベルを削除することを可能にします::

    diff = x - x_base
    if diff:
        g = gcd(diff, n)
        if g > 1:
            return g

became::

    if (diff := x - x_base) and (g := gcd(diff, n)) > 1:
        return g

That ``if`` is about as long as I want my lines to get, but remains easy
to follow.

その「if」は私が自分の行を取得したい限りだが、従うのは簡単なままである。

So, in all, in most lines binding a name, I wouldn't use assignment
expressions, but because that construct is so very frequent, that
leaves many places I would.  In most of the latter, I found a small
win that adds up due to how often it occurs, and in the rest I found a
moderate to major win.  I'd certainly use it more often than ternary
``if``, but significantly less often than augmented assignment.

つまり、名前を束縛するほとんどの行では代入式を使用しませんが、その構造は非常に頻繁に使用されるため、多くの場所に残ることになります。 後者のほとんどで、私はそれがどれくらいの頻度で起こるかのために合算する小さな勝利を見つけました、そして、残りで私は中程度から主要な勝利を見つけました。 私は確かにそれを三項の「if」よりももっと頻繁に使うでしょうが、増強された代入よりはかなり少ない頻度で使います。

A numeric example
-----------------

I have another example that quite impressed me at the time.

私は当時私にかなり感銘を与えた別の例があります。

Where all variables are positive integers, and a is at least as large
as the n'th root of x, this algorithm returns the floor of the n'th
root of x (and roughly doubling the number of accurate bits per
iteration)

すべての変数が正の整数で、aが少なくともxのn乗根と同じ大きさである場合、このアルゴリズムはxのn乗根の下限を返します（繰り返しあたりの正確なビット数を約2倍にします）。::

    while a > (d := x // a**(n-1)):
        a = ((n-1)*a + d) // n
    return a

It's not obvious why that works, but is no more obvious in the "loop
and a half" form. It's hard to prove correctness without building on
the right insight (the "arithmetic mean - geometric mean inequality"),
and knowing some non-trivial things about how nested floor functions
behave. That is, the challenges are in the math, not really in the
coding.

それがなぜうまくいくのかは明らかではありませんが、「ループと半分」の形ではもう明らかではありません。 正しい洞察（「算術平均 - 幾何平均の不等式」）を基にして、入れ子になったフロア関数の振る舞いについての自明でないことを知っていないと、正確さを証明するのは困難です。 つまり、課題は数学の問題であり、実際のコーディングの問題ではありません。

If you do know all that, then the assignment-expression form is easily
read as "while the current guess is too large, get a smaller guess",
where the "too large?" test and the new guess share an expensive
sub-expression.

すべて知っているのであれば、代入式の形式は「現在の推定値が大きすぎるときは小さめの推定値を得る」と読みやすくなります。 testと新しい推測は高価な部分式を共有します。

To my eyes, the original form is harder to understand

私の目には、元の形式は理解するのが難しいです::

    while True:
        d = x // a**(n-1)
        if a <= d:
            break
        a = ((n-1)*a + d) // n
    return a


Appendix B: Rough code translations for comprehensions
======================================================

This appendix attempts to clarify (though not specify) the rules when
a target occurs in a comprehension or in a generator expression.
For a number of illustrative examples we show the original code,
containing a comprehension, and the translation, where the
comprehension has been replaced by an equivalent generator function
plus some scaffolding.

この付録では、対象が内包表記または生成式に含まれるときの規則を明確にすることを試みます（ただし、指定はしません）。 いくつかの実例として、内包表記を含む元のコードと翻訳を示します。ここでは、内包表記は同等の生成関数と足場で置き換えられています。

Since ``[x for ...]`` is equivalent to ``list(x for ...)`` these
examples all use list comprehensions without loss of generality.
And since these examples are meant to clarify edge cases of the rules,
they aren't trying to look like real code.

`` [x for ...] ``は `` list（x for ...） ``と同じなので、これらの例はすべて一般性を失うことなくリスト内包表記を使用します。 そして、これらの例はルールのエッジケースを明確にすることを目的としているので、実際のコードのようには見えません。

Note: comprehensions are already implemented via synthesizing nested
generator functions like those in this appendix.  The new part is
adding appropriate declarations to establish the intended scope of
assignment expression targets (the same scope they resolve to as if
the assignment were performed in the block containing the outermost
comprehension).  For type inference purposes, these illustrative
expansions do not imply that assignment expression targets are always
Optional (but they do indicate the target binding scope).

注意：内包表記は、この付録のようなネストされたジェネレータ関数を合成することによってすでに実装されています。 新しい部分では、代入式の対象の意図された範囲（最も外側の内包を含むブロックで代入が実行された場合と同じ範囲）を確立するための適切な宣言を追加します。 型推論の目的のために、これらの例示的な拡張は代入式のターゲットが常にOptionalであることを意味しません（しかしそれらはターゲットバインディングスコープを示します）。

Let's start with a reminder of what code is generated for a generator
expression without assignment expression.

代入式を使わずにジェネレータ式に対してどのようなコードが生成されるかを思い出すことから始めましょう。

- Original code (EXPR usually references VAR)::

    def f():
        a = [EXPR for VAR in ITERABLE]

- Translation (let's not worry about name conflicts)::

    def f():
        def genexpr(iterator):
            for VAR in iterator:
                yield EXPR
        a = list(genexpr(iter(ITERABLE)))

Let's add a simple assignment expression.

簡単な代入式を追加しましょう。

- Original code::

    def f():
        a = [TARGET := EXPR for VAR in ITERABLE]

- Translation::

    def f():
        if False:
            TARGET = None  # Dead code to ensure TARGET is a local variable
        def genexpr(iterator):
            nonlocal TARGET
            for VAR in iterator:
                TARGET = EXPR
                yield TARGET
        a = list(genexpr(iter(ITERABLE)))

Let's add a ``global TARGET`` declaration in ``f()``.

``f()`` に ``global TARGET`` 宣言を追加しましょう。

- Original code::

    def f():
        global TARGET
        a = [TARGET := EXPR for VAR in ITERABLE]

- Translation::

    def f():
        global TARGET
        def genexpr(iterator):
            global TARGET
            for VAR in iterator:
                TARGET = EXPR
                yield TARGET
        a = list(genexpr(iter(ITERABLE)))

Or instead let's add a ``nonlocal TARGET`` declaration in ``f()``.

あるいはその代わりに ``f()``に ``nonlocal TARGET`` 宣言を追加しましょう。

- Original code::

    def g():
        TARGET = ...
        def f():
            nonlocal TARGET
            a = [TARGET := EXPR for VAR in ITERABLE]

- Translation::

    def g():
        TARGET = ...
        def f():
            nonlocal TARGET
            def genexpr(iterator):
                nonlocal TARGET
                for VAR in iterator:
                    TARGET = EXPR
                    yield TARGET
            a = list(genexpr(iter(ITERABLE)))

Finally, let's nest two comprehensions.

最後に、2つの内包表記を入れ子にしましょう。

- Original code::

    def f():
        a = [[TARGET := i for i in range(3)] for j in range(2)]
        # I.e., a = [[0, 1, 2], [0, 1, 2]]
        print(TARGET)  # prints 2

- Translation::

    def f():
        if False:
            TARGET = None
        def outer_genexpr(outer_iterator):
            nonlocal TARGET
            def inner_generator(inner_iterator):
                nonlocal TARGET
                for i in inner_iterator:
                    TARGET = i
                    yield i
            for j in outer_iterator:
                yield list(inner_generator(range(3)))
        a = list(outer_genexpr(range(2)))
        print(TARGET)


Appendix C: No Changes to Scope Semantics
=========================================

Because it has been a point of confusion, note that nothing about Python's
scoping semantics is changed.  Function-local scopes continue to be resolved
at compile time, and to have indefinite temporal extent at run time ("full
closures").  Example

混乱の原因となっているので、Pythonのスコープの意味については何も変わっていないことに注意してください。 関数ローカルスコープはコンパイル時に解決され続け、実行時には無限の一時的な範囲を持ちます（ "完全クロージャ"）。 例::

    a = 42
    def f():
        # `a` is local to `f`, but remains unbound
        # until the caller executes this genexp:
        yield ((a := i) for i in range(3))
        yield lambda: a + 100
        print("done")
        try:
            print(f"`a` is bound to {a}")
            assert False
        except UnboundLocalError:
            print("`a` is not yet bound")

Then::

    >>> results = list(f()) # [genexp, lambda]
    done
    `a` is not yet bound
    # The execution frame for f no longer exists in CPython,
    # but f's locals live so long as they can still be referenced.
    >>> list(map(type, results))
    [<class 'generator'>, <class 'function'>]
    >>> list(results[0])
    [0, 1, 2]
    >>> results[1]()
    102
    >>> a
    42


References
==========

.. [1] Proof of concept implementation
   (https://github.com/Rosuav/cpython/tree/assignment-expressions)
.. [2] Pivotal post regarding inline assignment semantics
   (https://mail.python.org/pipermail/python-ideas/2018-March/049409.html)


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
