:orphan:

.. _pep825-metadata-consistency:

Appendix: Rationale for the Metadata Consistency Requirements
=============================================================

This appendix supplements the `Metadata consistency
<https://peps.python.org/pep-0825/#metadata-consistency>`__ section of
:pep:`825`. That section states what is required; this one argues that
the requirement is justified, sets out what it costs, and is explicit
about the motivation behind it and the trade-offs involved.

It also sets out the reasoning behind the `variant environment markers
<https://peps.python.org/pep-0825/#variant-environment-markers>`__,
since the case for markers and the case for consistent metadata are
substantially the same argument.


What is actually being required
-------------------------------

Metadata consistency has come up in several forms during the discussion
of this PEP. Before defending the requirement it is worth being precise
about how small it is.

**Two keys are constrained**, both in variant metadata:
``default-priorities.namespace`` and ``variants``.

**Neither requires identity.** The requirement is that the values be
*combinable without conflict*:

- ``default-priorities.namespace``: the lists must either be identical,
  or the longer must start with the elements of the shorter, in the same
  order. Combining yields the longer list.
- ``variants``: the same variant label must always map to the same set
  of properties. Combining yields the union.

Both rules are symmetric, so the result does not depend on the order in
which wheels are processed.

**Nothing else is constrained, and nothing is foreclosed.** In
particular, this PEP places no consistency requirement on dependency
metadata. :doc:`packaging:specifications/core-metadata` already permits
``Requires-Dist`` to differ between the wheels of one release when
declared ``Dynamic``, and nothing here changes that. A publisher may
still take that route.

The corollary should be stated openly. Variant environment markers exist
partly so that dependency metadata *can* stay consistent across a
release. That is a key motivation, and we do not claim neutrality on the
question. What we are not doing is requiring anything, or removing an
option that exists today.


The empirical question was largely settled in the 2024 thread
-------------------------------------------------------------

The 2024 thread `Enforcing consistent metadata for packages`__ asked the
ecosystem to describe situations where a consistency rule would cause
problems. It did the scanning work, and the results bear directly on
this PEP.

__ https://discuss.python.org/t/enforcing-consistent-metadata-for-packages/50008

Cemici found no interesting variation in the top 100 wheels
(`post 3`__), and going considerably deeper, **32 packages** with
meaningful variation at their latest release (`post 6`__). Of those 32,
on a superficial pass only one looked as though it might not be
replaceable by static dependencies plus
:ref:`packaging:dependency-specifiers` markers.

__ https://discuss.python.org/t/enforcing-consistent-metadata-for-packages/50008/3
__ https://discuss.python.org/t/enforcing-consistent-metadata-for-packages/50008/6

Both prominent cases have since dissolved.


``apache-beam``: a missing marker variable, not an intrinsic gap
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

Beam avoids requiring ``pyarrow`` on 32-bit Windows, which was judged
hard or impossible to express with :pep:`508` markers (`post 5`__). The
obstacle is specific and incidental: :pep:`508` has no way to
distinguish a 32-bit from a 64-bit interpreter, which matters only on
Windows, where both are widely used on x86-64.

__ https://discuss.python.org/t/enforcing-consistent-metadata-for-packages/50008/5

:pep:`780` adds precisely that, defining ``32-bit`` and ``64-bit`` as
ABI features exposed through a new ``sys_abi_features`` marker. Its own
worked example is the same shape as Beam's case:

.. code:: text

    scipy; platform_system != "Windows" or "32-bit" not in sys_abi_features

:pep:`780` is still in Draft, so this is not a promise that the gap is
closed. The point is narrower: it is a missing *marker variable*, not a
case where per-wheel dependency divergence is intrinsically necessary.

Worth noting alongside: Beam emits ``Dynamic: requires-dist``. Its
divergence is properly declared. The one genuine candidate gap is also
the one project using the existing mechanism correctly, which is a
reason to treat that mechanism as a serious alternative rather than a
straw man.


``open3d``: not an expressive gap
'''''''''''''''''''''''''''''''''

Reported in `post 14`__ as a case that has repeatedly bitten Poetry
users: open3d ships different dependencies depending on the platform the
wheel was built for (`isl-org/Open3D#5747`__). The cause is a build that
loads a different requirements file per build into ``install_requires``,
not anything markers cannot express. The maintainers indicated they
would accept a fix; a PR was opened and has not been reviewed.

__ https://discuss.python.org/t/enforcing-consistent-metadata-for-packages/50008/14
__ https://github.com/isl-org/Open3D/issues/5747

So open3d is evidence that divergence persists through maintainer
inertia, rather than because anyone needs it.


What this does and does not establish
'''''''''''''''''''''''''''''''''''''

Across the top PyPI packages there is **no confirmed case** of
dependency divergence that markers could not express, once the single
candidate gap is closed.

It does not establish that no such case exists. The scan was a
superficial pass, covered latest releases only, and could not see
projects that publish sdists without wheels. The 2024 post was
explicitly soliciting cases nobody had yet found, and that solicitation
stands.


Variant wheels would be the first real gap, and markers close it
----------------------------------------------------------------

This is the part we think matters most, and it is an argument for
markers on the terms set out in the 2024 thread, not on ours.

If there is no confirmed case where divergent dependencies are genuinely
necessary, then variant wheels would be the first. A CUDA variant really
does need different dependencies from a CPU variant, and the
alternatives do not work:

- taking the union installs CUDA libraries for CPU-only users
  [#cuda-size]_;
- separate package names (``torch-cuda``, ``torch-cpu``) are the status
  quo that variants exist to replace;
- vendoring the libraries into every wheel is what size limits already
  rule out.

So without variant markers, every project shipping variant wheels must
declare ``Dynamic: Requires-Dist`` and publish divergent dependency
metadata. The population of packages with divergent metadata would go
from roughly 32 accidental and largely fixable cases to **many
variant-publishing projects, deliberately and permanently**.

There is a second edge to this, which bears on how available the
alternative actually is. In `post 13`__ the question was asked whether
any backend other than setuptools can produce Core Metadata 2.2 dynamic
data, and it was never answered. We have now checked, and the answer is
in `Which build backends can emit Dynamic in wheel METADATA`_ below:
**setuptools is the only backend that can emit** ``Dynamic:
Requires-Dist`` **in a wheel alongside the dependencies it applies to**,
and it does so only when ``install_requires`` is genuinely computed,
which in practice means a ``setup.py``.

__ https://discuss.python.org/t/enforcing-consistent-metadata-for-packages/50008/13

This is a limitation of the backends rather than of the libraries.
``pyproject-metadata`` supports the field fully. But scikit-build-core
restricts ``Dynamic`` to sdists by explicit choice, meson-python does
not permit dynamic dependencies, maturin never writes a ``Dynamic``
header, and hatchling emits ``Dynamic`` only for fields left unresolved,
so never alongside the dependencies in question. Those are the backends
the compiled scientific and GPU stack is built with.

So a project on meson-python or scikit-build-core that wanted
per-variant dependencies through ``Dynamic`` would first have to change
build backend. We are not claiming this could never be implemented, only
that the alternative is considerably less available today than it
appears on paper, and that the backends which have considered the
question have converged on not emitting ``Dynamic`` in wheels.


Forced divergence would move a cost onto every resolution
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''

Resolvers today read the ``METADATA`` of one wheel per release and apply
it to the release. uv and Poetry both do this. It is formally
unsupported, and its consequences are not hypothetical: open3d's
divergence is what bit Poetry users repeatedly, and is how that case
reached the 2024 thread.

Variant wheels with divergent dependencies would make that assumption
unsafe for the first time at scale. There are two ways out, and neither
is free.

A resolver could keep the assumption. It might then read the CPU
variant's metadata and install a CUDA wheel without the CUDA runtime
dependencies, or read a CUDA variant's metadata and pull several hundred
megabytes of unused libraries in alongside the CPU wheel. In a release
that also contains a non-variant wheel, the wrong dependency set could
be applied to that wheel too. There is a mitigation available for that
particular case: an index could decline to serve ``core-metadata`` for
variant wheels, so that only the non-variant wheel's metadata is cheaply
reachable. That is a specification change in its own right, and it
withholds from variant-aware resolvers precisely the data they need.

Or a resolver could drop the assumption and fetch ``METADATA`` per
candidate wheel. This is correct, and it is what we would expect tools
to do. It is also the cost that the index-level metadata file exists to
avoid, and it would be paid on every resolution by every user, not only
by those using variants.

Markers avoid the dilemma rather than resolving it in anyone's favour.
The ``Requires-Dist`` lines are textually identical across the wheels of
the release and carry the conditionals, so reading one wheel's
``METADATA`` remains sound, and the per-variant evaluation is done from
the combined variant metadata, which a variant-aware resolver has
already obtained in order to make the selection. [#index-json]_

None of this is an argument that divergence should be forbidden. Beam
does it, declares it correctly, and that is fine. [#beam-scope]_ The
objection is to making it the default for an entire new class of wheels.


Conclusion
''''''''''

We should be plain about our own position rather than presenting this as
balanced. Markers are the right mechanism, and this document is the case
for them. The reason is not tooling convenience. It is that the two
routes deliver the same per-variant differentiation while differing in
what they cost everyone downstream, and that one of them is today
reachable only through a single build backend. The specification
therefore adopts markers, and the question is settled for the purposes
of this PEP.

Being explicit about what would un-settle it: a case where per-variant
dependencies genuinely cannot be expressed with markers, or evidence
that the divergence route costs consumers less than we have assumed
here. Neither has been produced, and the first of them is what the 2024
thread solicited and did not find.


Divergent variant metadata, specifically, has no use case
---------------------------------------------------------

The arguments above concern dependency metadata. The two keys this PEP
actually constrains are a narrower and easier case.

**A divergent** ``variants`` **mapping is incoherent rather than
expressive.** A label is a release-scoped identifier for a property set.
Two wheels of one release disagreeing about what ``cu128`` maps to are
not expressing anything about the target platform; the identifier is
simply broken. Dependency divergence at least *could* express something
real, whereas a divergent label mapping cannot.

**The data is a projection of a single source.** It originates in one
place per project — a subsequent PEP will propose the ``pyproject.toml``
integration — and is copied into each wheel at build time. Consistency
therefore holds by construction unless the wheels of one release are
built from different inputs. Divergence is a build accident, not an
intent.

**Nobody has described wanting it.** Across the discussion, the closest
case is the third-party publisher who needs a new namespace, and that is
*extension* rather than conflict: the prefix rule accommodates it
directly, with the appended namespace landing at lowest priority.


What breaks without the constraint
----------------------------------

**Ordering becomes undefined.** This is the load-bearing one, and it
concerns correctness rather than performance. If two wheels of a release
disagree about namespace order, there is no total order over the
variants, so the selection algorithm has no defined output and two
conforming installers can select different wheels from the same inputs.

**Locks stop being reproducible.** ``pylock.toml`` inlines combined
variant metadata. Non-deterministic combination means two lock runs over
the same release can produce different lock files.

**The index-level file could not be generated from wheels alone.** The
design lets an index build ``{name}-{version}-variants.json`` from the
uploaded wheels with no additional input and no changes to upload
workflows. That works only because the inputs combine deterministically.

**The PEP's own optimization becomes unsound.** The index-level metadata
file exists so that a resolver need not fetch wheels to learn what
variants exist. If metadata could diverge, a correct resolver would have
to download every candidate wheel to discover the true combined picture.
The constraint is not there to help any particular tool; it is what
makes a mechanism this PEP defines actually work.


The cost is close to zero
-------------------------

**Satisfied by construction**, as above.

**There is no installed base.** Nobody publishes variant wheels yet. The
2024 effort faced an ecosystem where divergent publishers already
existed; here the migration cost is nil.

**The asymmetry runs one way.** Specifying this now costs nothing.
Omitting it forecloses it permanently, because once divergent publishers
exist the constraint can never be introduced. We are conscious that the
reverse move, relaxing a constraint later, was rightly identified in
`post 152`__ as its own trap, and we are not relying on it.

__ https://discuss.python.org/t/pep-825-wheel-variants-package-format-split-from-pep-817/106196/152

**No backwards-compatibility surface.** Non-variant wheels are
untouched, and existing tools are untouched.


What we ask of publishers, and what of tools
--------------------------------------------

`Post 145`__ proposed a formulation, and we think it is the right one.
The specification says, in substance:

__ https://discuss.python.org/t/pep-825-wheel-variants-package-format-split-from-pep-817/106196/145

- Meeting the requirements is the responsibility of the **publisher** of
  the package version.
- Where a user draws wheels for the same package from more than one
  source, no publisher can guarantee consistency with the others;
  ensuring the combined sources are consistent is then the **user's**
  responsibility.
- Tools **MAY** assume the requirements are met. The specification does
  not require them to verify it, and does not prescribe what they do if
  they detect that they do not hold.

This is permission rather than obligation. We are not proposing that
anyone enforce a consistency rule across the ecosystem, and the
objection that such a rule would be unenforceable, because of static
indexes and ``--find-links``, does not apply to it. Indexes that *are*
in a position to check at upload time are the natural place to do so,
but nothing depends on universal enforcement.

For context rather than support: :pep:`808` has been accepted, and in
Core Metadata 2.6 fields specified in the sdist are guaranteed to appear
in the wheel even when ``Dynamic`` is present, where 2.2 through 2.5
place no constraints on ``Dynamic`` entries. Backend implementation is
incomplete but expected to finish within roughly the coming year. The
ecosystem is tightening in the direction of more predictable metadata
rather than less.


Summary
-------

- The constraint covers two keys, requires combinability rather than
  identity, and forecloses nothing that Core Metadata permits today.
- The 2024 survey found 32 packages with meaningful variation and one
  candidate expressive gap. That gap is a missing marker variable which
  :pep:`780` addresses, and the other prominent case is a fixable build
  bug.
- Variant wheels would otherwise become the first large-scale,
  deliberate source of divergent dependency metadata. The ``Dynamic``
  route is today reachable only through setuptools with a ``setup.py``,
  which is not how the compiled scientific and GPU stack is built.
  Environment markers, on the other hand, are a well-known mechanism for
  expressing conditional dependencies.
- Forced divergence would leave resolvers with a dilemma: keep an
  assumption that becomes unsafe, or fetch ``METADATA`` per candidate
  wheel on every resolution. Markers make the assumption sound instead.
- Divergent variant metadata specifically is incoherent rather than
  expressive, and nobody has asked for it.
- Without the constraint, variant ordering is undefined, locks are not
  reproducible, and the index-level metadata file cannot be generated or
  trusted.
- The cost is near zero: satisfied by construction, no installed base,
  no compatibility surface.
- Publishers are responsible, users are responsible across sources, and
  tools may assume while being required to do nothing.


Which build backends can emit Dynamic in wheel METADATA
-------------------------------------------------------

Checked 8 August 2026, against the versions listed. This is a snapshot
of current behavior, not a statement about what these backends could
implement.

.. list-table::
   :header-rows: 1
   :widths: 22 26 52

   * - Backend
     - Version tested
     - Emits ``Dynamic: Requires-Dist`` in a wheel?

   * - setuptools
     - 83.0.0 (released)
     - **Yes**, when ``install_requires`` is computed in ``setup.py``

   * - setuptools (declarative)
     - 83.0.0 (released)
     - No. ``[tool.setuptools.dynamic] dependencies = {file = ...}``
       yields no ``Dynamic`` line

   * - hatchling
     - 1.31.0, ``3a9d853`` (2026-08-06)
     - Only for *unresolved* dynamic fields, so never alongside the
       dependencies themselves

   * - scikit-build-core
     - post-v1.0.3 dev, ``ee120a8`` (2026-08-05)
     - No. Passes ``dynamic_metadata`` through, but gated to sdists by
       choice

   * - meson-python
     - 0.21.0.dev0, ``f915043`` (2026-07-20)
     - No. Rejects dynamic dependencies

   * - maturin
     - 1.14.1, ``c30aa84`` (2026-08-07)
     - No. No ``Dynamic`` writer, and ``project.dynamic`` is not
       consulted for dependencies

   * - flit-core
     - 4.0.2, ``60c0b3d`` (2026-08-04)
     - No

   * - poetry-core
     - 2.4.1, ``5de2411`` (2026-06-19)
     - No

   * - pdm-backend
     - post-2.4.9 dev, ``d9fab37`` (2026-07-27)
     - No

   * - *pyproject-metadata* (library)
     - 0.12.1, ``737644a`` (2026-07-03)
     - *Supports it fully; the constraint is in the backends*

Versions are as declared in the source tree at the commit tested. Where
a project derives its version from SCM tags, the most recent tag is
given with a ``post-`` prefix, since the tree is a development state
after that release.

Method and detail:

- **setuptools** gates emission on ``not is_static(val)``, where
  ``_POSSIBLE_DYNAMIC_FIELDS`` maps ``requires-dist`` to
  ``install_requires``. A value declared in ``pyproject.toml`` is
  tracked as ``Static``, so only a computed ``install_requires``
  triggers the header. Verified by building wheels: a ``setup.py``
  computing ``install_requires`` produces ``Metadata-Version: 2.4`` with
  ``Requires-Dist: numpy`` and ``Dynamic: requires-dist``; the
  declarative form produces neither. This also explains
  ``apache-beam``, which uses ``setup.py`` and does emit ``Dynamic:
  requires-dist``.
- **hatchling** writes ``Dynamic:`` for every field remaining in
  ``project.dynamic`` after metadata hooks run. A hook that supplies
  ``dependencies`` removes the field, so no header is written. Leaving
  ``dependencies`` dynamic with no hook does produce ``Dynamic:
  Requires-Dist``, but then there are no dependencies to qualify. Both
  cases verified by building wheels.
- **scikit-build-core** passes ``dynamic_metadata`` to
  ``pyproject-metadata``, and implements :pep:`808` ``dual_dynamic``,
  but gates the value on ``build_state == "sdist"`` with the comment
  "Only SDist metadata may carry Dynamic fields".
- **meson-python** subclasses ``StandardMetadata``, does not accept
  ``dynamic_metadata``, and restricts ``project.dynamic`` to
  ``version``, ``license`` and ``license-files``.
- **maturin** builds its ``METADATA`` field list without any
  ``Dynamic`` entry, and its routine for clearing non-dynamic fields
  does not handle ``dependencies``, so ``project.dynamic`` has no path
  to a ``Dynamic`` header.
- **flit-core, poetry-core, pdm-backend** have no ``Dynamic`` writer;
  matches in ``pdm-backend`` and ``poetry-core`` are in vendored copies
  of ``packaging`` and ``pyproject-metadata``.
- **pyproject-metadata** keeps ``dynamic`` (the :pep:`621` list) and
  ``dynamic_metadata`` (the Core Metadata headers) as separate fields.
  ``project.dynamic`` alone never produces a ``Dynamic:`` header; the
  backend must pass ``dynamic_metadata`` explicitly. Permitted values
  are any known metadata field except ``name``, ``version`` and
  ``dynamic``; setting any bumps ``Metadata-Version`` to 2.2, and
  :pep:`808` dual-dynamic fields bump it to 2.6.

A note on method: setuptools and hatchling were verified by building
actual wheels and reading the resulting ``METADATA``, in two
independently shaped test projects each. ``pyproject-metadata`` was
verified by calling it directly and inspecting the ``METADATA`` it
produces. The remaining six, scikit-build-core, meson-python, maturin,
flit-core, poetry-core and pdm-backend, were established by source
inspection at the commits given, not by building. Source inspection is
the weakest of the three, so a counterexample for any of those six is
worth more than the table suggests.


Footnotes
---------

.. [#cuda-size] These can be 500 MB per wheel, and multiple CUDA
   libraries and wheels are typically necessary, so this would
   potentially be multi-gigabyte downloads extra for CPU-only users of
   popular packages.

.. [#index-json] The index-level ``{name}-{version}-variants.json`` file
   is an optimization rather than a property of the format. It must be
   published when variant wheels are hosted on an index, and its purpose
   is to avoid fetching multiple wheels during resolution. Where a
   source does not provide it, such as a local directory of wheels, the
   combined variant metadata is read from the wheels instead: one wheel
   per distinct variant label, and only the variant metadata file within
   it rather than the whole wheel.

.. [#beam-scope] At least for the purposes of this PEP; we do not aim to
   change that case. Users of Beam may still struggle when using uv or
   Poetry.
