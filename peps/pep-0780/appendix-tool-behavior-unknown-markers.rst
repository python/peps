:orphan:

.. _pep780-tool-behavior-unknown-markers:

Appendix: Compatibility behavior in existing tools
==================================================

This non-normative appendix supplements the :ref:`Backwards Compatibility
<pep780-backwards-compatibility>` section of :pep:`780`. It describes how
existing packaging tools handle dependencies containing markers they do not
understand.

To test whether tools can fall back to an older release, two versions of a
package named ``marker-test`` are made available as wheels. Version 1.0 has no
dependencies. Version 2.0 adds a dependency on ``idna`` conditional on
``sys_abi_info``, which the tested tools do not recognize. Its wheel metadata
contains::

    Requires-Dist: idna; "pointer_bits::64" in sys_abi_info

A consumer that does not understand ``sys_abi_info`` should reject version 2.0
and may select version 1.0. The marker expression tests whether the interpreter
has 64-bit pointers, but consumers that do not recognize the field name cannot
interpret that condition.

The following table summarizes the wheel case. The detailed sections below
separate resolver tests from source inspection and metadata-conversion tests.

.. list-table:: Wheel dependency metadata containing an unknown marker
   :header-rows: 1
   :widths: 20 55 25

   * - Tool
     - Behavior
     - Older-release fallback
   * - pip
     - 24.0 (Feb 2024) aborts; 24.1 (Jun 2024) and later reject the package version
     - Yes from 24.1
   * - uv
     - 0.7.0 (Apr 2025) and 0.13.6 (Oct 2026), without preview features,
       select the older release
     - Yes
   * - PDM
     - 2.13.0 (Mar 2024) and 2.29.5 (Oct 2026) reject candidates with invalid
       dependency metadata
     - Yes
   * - Poetry
     - 1.8.2 (Mar 2024) and 2.5.1 (Sep 2026) drop the dependency containing
       the unknown marker rather than reject the package version
     - No


For their pip-based resolver paths, Pipenv and pip-tools do not add independent
resolver behavior here: Pipenv uses an embedded/patched pip resolver, while
pip-tools invokes pip's resolver internals. Their behavior therefore follows
the corresponding pip version.

pip
---

The table below shows how pip handles an unsupported marker in runtime or
build dependencies when installing a local project, a wheel, or a source
distribution. Local tests with
pip 26.2.2 (Oct 2026) used ``--find-links`` candidates, isolated setuptools builds, and
dry-run installation; packages were not uploaded to TestPyPI. Backend
validation of ``project.dependencies`` failed during
``get_requires_for_build_wheel``, before metadata could be generated.

.. list-table:: pip behavior with an unsupported marker
   :header-rows: 1
   :widths: 40 40 20

   * - Installation case
     - Outcome
     - Older-release fallback
   * - ``pip install .``; marker in ``project.dependencies``
     - Backend validation fails before dependency metadata is available
     - Not applicable
   * - ``pip install .``; marker in ``build-system.requires``
     - Frontend fails while reading ``pyproject.toml``
     - Not applicable
   * - ``pip install marker-test``; marker in wheel ``Requires-Dist``
     - pip 24.1 and later reject the version as invalid metadata
     - Yes
   * - ``pip install marker-test``; marker in sdist ``project.dependencies``
     - Backend validation fails before dependency metadata is available
     - No
   * - ``pip install marker-test``; marker in sdist ``build-system.requires``
     - Frontend fails while preparing the candidate
     - No
   * - Release has a usable wheel and an sdist with an unsupported marker in
       ``build-system.requires``
     - Wheel installs without inspecting the sdist's build requirements
     - Not applicable

The sdist cases fail earlier than wheel dependency processing. Build requirement
parsing occurs before invoking the backend, and backend metadata validation can
fail before the resolver receives dependency metadata. The wheel fallback
behavior therefore does not imply fallback for arbitrary build or backend
errors. Local source installs have no older index candidate to select in any
case.

The remainder of this appendix considers only the third row, the case where a
wheel's dependency metadata contains an unsupported marker. This is the key case for fallback to an older
package version. The other cases are not expected to provide such fallback,
as discussed in the :ref:`Backwards Compatibility
<pep780-backwards-compatibility>` section of :pep:`780`.

For the wheel case, pip 24.0 aborts with a requirement-parsing error
instead of trying version 1.0. The behavior changed in pip 24.1 through
`pypa/pip#12300 <https://github.com/pypa/pip/pull/12300>`__, which discards
candidates with invalid dependencies and excludes other candidates of the same
version. This is package-version rejection, rather than permission to choose
another artifact with inconsistent dependency metadata.

Local dry-run resolution with pip 24.0, 24.1, and 26.2.2 reproduced the wheel
version boundary using the current ``sys_abi_info`` example. Both newer versions
selected 1.0, and both failed when the requirement pinned version 2.0.

The pip 24.1 and 26.2.2 diagnostic begins with a warning
that version 2.0 has invalid metadata, followed by the parser's explanation. It also suggests using
``pip<24.1``. That diagnostic addresses invalid metadata generally;
it is not appropriate upgrade advice for a newly standardized marker. An
unsupported marker needs a consumer that understands it, or rejection of the
affected version, rather than removal of the condition.

uv
--

Local tests with uv 0.7.0 and 0.13.6, using ``uv pip compile --no-index`` with
``--find-links`` pointing at the two wheels, selected version 1.0. No preview
feature was enabled.

PDM
---

PDM provides an independent implementation of candidate-level fallback.
`PDM 2.13.0
<https://github.com/pdm-project/pdm/blob/2.13.0/src/pdm/resolver/providers.py>`__
has a resolver that catches requirement and specifier errors when obtaining
candidate dependencies and marks that candidate as conflicting. The same policy is present in
`PDM 2.29.5
<https://github.com/pdm-project/pdm/blob/2.29.5/src/pdm/resolver/providers.py>`__.
With wheels for both versions of ``marker-test`` available from a local index,
PDM 2.29.5 rejected version 2.0 as invalid metadata and locked version 1.0.

Poetry
------

Poetry has long used permissive recovery when converting published
``Requires-Dist`` entries into dependencies. Both
`Poetry 1.8.2
<https://github.com/python-poetry/poetry/blob/1.8.2/src/poetry/inspection/info.py>`__
and `Poetry 2.5.1
<https://github.com/python-poetry/poetry/blob/2.5.1/src/poetry/inspection/info.py>`__
catch an invalid-marker exception, remove everything after the semicolon, and
parse the dependency again. This turns a conditional dependency into an
unconditional one. The exception name changed from ``InvalidMarker`` to
``InvalidMarkerError``, but the recovery policy remained.
Metadata-conversion tests with both versions confirmed that
``idna; python_version == "not a version"`` becomes unconditional ``idna``.

Unknown marker names follow a different recovery path. Both versions parse
``idna; "pointer_bits::64" in sys_abi_info`` as an invalid requirement, log a
warning, and skip the entire dependency. Full ``poetry lock`` runs against a
local index confirmed this behavior in both versions: they locked
``marker-test`` 2.0 without ``idna``, rather than rejecting version 2.0 and
selecting version 1.0.

Related issues document the history of this inspection path:

* `Poetry #3629 <https://github.com/python-poetry/poetry/issues/3629>`__
  reported malformed Kivy wheel dependencies in 2021. The reporter quoted the
  marker-stripping code and questioned whether warning instead of raising could
  have consequences. Closing the issue did not remove that recovery policy.
* `Poetry #7729 <https://github.com/python-poetry/poetry/issues/7729>`__
  reported a parsing failure with malformed ``super-state-machine`` metadata,
  where older Poetry versions had warned and skipped the dependency. It shows
  that recovery versus failure has varied across versions and parsing errors.
* `Poetry #9154 <https://github.com/python-poetry/poetry/issues/9154>`__
  concerns a Windows file URL in dependency metadata, with a traceback through
  the same inspection code. It is a related cross-platform metadata problem,
  rather than a report about unknown markers.

None of these issues specifically addresses a future standardized marker that
an older consumer does not understand. In that case, the producer's metadata
can be valid even though the consumer rejects it. Stripping the condition can
add an unsuitable dependency; skipping the requirement can omit a needed one.
Neither preserves dependency semantics. The safe fallback is to reject the
containing package version and consider alternatives.
