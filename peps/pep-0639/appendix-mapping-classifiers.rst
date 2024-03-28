:orphan:

.. _639-spec-mapping-classifiers-identifiers:

Appendix: Mapping License Classifiers to SPDX Identifiers
=========================================================

Most single license classifiers (namely, all those not mentioned below)
map to a single valid SPDX license identifier,
allowing tools to infer the SPDX license identifier they correspond to,
both for use when analyzing and auditing packages,
and providing a semi-automated mechanism of filling the ``license`` key
or the ``License-Expression`` field
following the :ref:`PEP 639 specification <639-spec-converting-metadata>`.

Some legacy license classifiers intend to specify a particular license,
but do not specify the particular version or variant, leading to a
`critical ambiguity <classifierissue_>`__
as to their terms, compatibility and acceptability.
Tools MUST NOT attempt to automatically infer a ``License-Expression``
when one of these classifiers is used without affirmative user action:

- ``License :: OSI Approved :: Academic Free License (AFL)``
- ``License :: OSI Approved :: Apache Software License``
- ``License :: OSI Approved :: Apple Public Source License``
- ``License :: OSI Approved :: Artistic License``
- ``License :: OSI Approved :: BSD License``
- ``License :: OSI Approved :: GNU Affero General Public License v3``
- ``License :: OSI Approved :: GNU Free Documentation License (FDL)``
- ``License :: OSI Approved :: GNU General Public License (GPL)``
- ``License :: OSI Approved :: GNU General Public License v2 (GPLv2)``
- ``License :: OSI Approved :: GNU General Public License v3 (GPLv3)``
- ``License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)``
- ``License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)``
- ``License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)``
- ``License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)``

A comprehensive mapping of these classifiers to their possible specific
identifiers was `assembled by Dustin Ingram <badclassifiers_>`__, which tools
MAY use as a reference for the identifier selection options to offer users
when prompting the user to explicitly select the license identifier
they intended for their project.

.. note::

    Several additional classifiers, namely the "or later" variants of
    the AGPLv3, GPLv2, GPLv3 and LGPLv3, are also listed in the aforementioned
    mapping, but unambiguously map to their respective licenses,
    and so are not listed here.
    However, LGPLv2 is included above, as it could ambiguously
    refer to either the distinct v2.0 or v2.1 variants of that license.

In addition, for the various special cases, the following mappings are
considered canonical and normative for the purposes of this specification:

- Classifier ``License :: Public Domain`` MAY be mapped to the generic
  ``License-Expression: LicenseRef-Public-Domain``.
  If tools do so, they SHOULD issue an informational warning encouraging
  the use of more explicit and legally portable license identifiers,
  such as those for the `CC0 1.0 license <cc0_>`__ (``CC0-1.0``),
  the `Unlicense <unlicense_>`__ (``Unlicense``),
  or the `MIT license <mitlicense_>`__ (``MIT``),
  since the meaning associated with the term "public domain" is thoroughly
  dependent on the specific legal jurisdiction involved,
  some of which lack the concept entirely.
  Alternatively, tools MAY choose to treat these classifiers as ambiguous.

- The generic and sometimes ambiguous classifiers:

  - ``License :: Free For Educational Use``
  - ``License :: Free For Home Use``
  - ``License :: Free for non-commercial use``
  - ``License :: Freely Distributable``
  - ``License :: Free To Use But Restricted``
  - ``License :: Freeware``
  - ``License :: Other/Proprietary License``

  MAY be mapped to the generic
  ``License-Expression: LicenseRef-Proprietary``,
  but tools MUST issue a prominent, informative warning if they do so.
  Alternatively, tools MAY choose to treat these classifiers as ambiguous.

- The generic and ambiguous classifiers ``License :: OSI Approved`` and
  ``License :: DFSG approved`` do not map to any license expression,
  and thus tools SHOULD treat them as ambiguous, or if not MUST ignore them.

- The classifiers ``License :: GUST Font License 1.0`` and
  ``License :: GUST Font License 2006-09-30`` have no mapping to SPDX license
  identifiers, and no PyPI package uses them as of 2022-07-09.

When multiple license classifiers are used, their relationship is ambiguous,
and it is typically not possible to determine if all the licenses apply or if
there is a choice that is possible among the licenses,
In this case, tools MUST NOT automatically infer a license expression,
unless one license classifier is a parent of the other,
i.e. the child contains all ``::``-delineated components of the parent,
in which case tools MAY ignore the parent classifier
but SHOULD issue an informative warning when doing so.


.. _badclassifiers: https://github.com/pypa/trove-classifiers/issues/17#issuecomment-385027197
.. _cc0: https://creativecommons.org/publicdomain/zero/1.0/
.. _classifierissue: https://github.com/pypa/trove-classifiers/issues/17
.. _mitlicense: https://opensource.org/licenses/MIT
.. _unlicense: https://unlicense.org/
