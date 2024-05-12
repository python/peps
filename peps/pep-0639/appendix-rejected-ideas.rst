:orphan:

.. _639-rejected-ideas-details:

Appendix: Rejected Ideas
========================

Abstract
--------

This document contains a list of the alternative ideas to the ones proposed
in PEP 639 with detailed explanations why they were rejected.


Core Metadata fields
--------------------

Potential alternatives to the structure, content and deprecation of the
Core Metadata fields specified in :pep:`639`.


Re-use the ``License`` field
''''''''''''''''''''''''''''

Following `initial discussion <reusediscussion_>`__, earlier versions of
PEP 639 proposed re-using the existing ``License`` field, which tools would
attempt to parse as a SPDX license expression with a fallback to free text.
Initially, this would cause a warning and eventually it would be treated as an
error.

This would be more backwards-compatibile, allowed a smooth adoption
of SPDX license expressions in the community,
and avoided adding yet another license-related field.

Eventually, consensus was reached that a
dedicated ``License-Expression`` field was a better approach.
The presence of this field unambiguously signals support for the SPDX
identifiers, without the need for complex heuristics, and allows tools to
easily detect invalid content.

Furthermore, it allows both the existing ``License`` field and
the license classifiers to be easily deprecated,
with tools able to distinguish between packages conforming to PEP 639 or not,
and adapt their behavior accordingly.

Finally, it avoids changing the behavior of an existing metadata field,
and avoids tools having to guess the ``Metadata-Version`` and field behavior
based on its value rather than merely its presence.

Distributions which already contain valid SPDX license expressions in the
``License`` fields will not automatically be recognized as such.
The migration is simple though, and PEP 639 provides
guidance on how this can be done automatically by tooling.


Re-Use the ``License`` field with a value prefix
''''''''''''''''''''''''''''''''''''''''''''''''

As an alternative to the previous, prefixing SPDX license expressions with,
e.g. ``spdx:`` was suggested to reduce the ambiguity of re-using
the ``License`` field. However, this effectively amounted to creating
a field within a field, and doesn't address the downsides of
keeping the ``License`` field. Namely, it still changes the behavior of an
existing metadata field, requires tools to parse its value
to determine how to handle its content, and makes the specification and
deprecation process more complex and less clean.

Projects currently using valid SPDX identifiers in the ``License``
field won't be automatically recognized, and require
about the same amount of effort to fix as in the case of introducing a new
field, namely changing a line in the
project's source metadata. Therefore, it was rejected in favor of a new field.


Don't make ``License-Expression`` mutually exclusive
''''''''''''''''''''''''''''''''''''''''''''''''''''

For backwards compatibility, the ``License`` field and/or the license
classifiers could still be allowed together with the new
``License-Expression`` field, presumably with a warning. However, this
could easily lead to inconsistent
license metadata in no less than *three* different fields, which is
contrary to the goal of PEP 639 of making the licensing story
unambiguous. Therefore, with the community
consensus this idea was rejected.


Don't deprecate existing ``License`` field and classifiers
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

Several community members were concerned that deprecating the
existing ``License`` field and classifiers would result in
much churn for package authors and raise the barrier to
entry for new ones, particularly developers seeking to
package their personal projects without caring
too much about the legal technicalities.
Indeed, every deprecation should be carefully considered relative to the
long-term
net benefit. At the minimum, this change shouldn't make it more
difficult for a Python developer to share their work under
a license of their choice, and ideally improve the situation.

Following many rounds of discussion,
the general consensus was in favor of deprecating the legacy
means of specifying a license and in favor of "one obvious way to do it".
Not doing so would leave three different un-deprecated ways of
specifying a license for a package, two of them ambiguous,
inconsistently documented and out of date.
This is more complex for tools to support
indefinitely, resulting in a non-trivial maintenance cost.

Finally, for unmaintained packages, those using tools supporting older
metadata versions, or those who choose not to provide license metadata,
no changes are required regardless of the deprecation.


Don't mandate validating new fields on PyPI
'''''''''''''''''''''''''''''''''''''''''''

Previously, PEP 639 did not provide specific guidance
for PyPI (or other package indices) as to whether and how they
should validate the ``License-Expression`` or ``License-File`` fields,
nor how they should handle using them in combination with the deprecated
``License`` field or license classifiers. This simplifies the specification
and defers implementation on PyPI to a later PEP to minimize
disruption to package authors.

This was in place for an earlier draft of PEP 639 which didn't separate
``License-Expression`` from the ``License`` field. The validation would have
been difficult and backwards-incompatible, breaking existing packages.
With the current proposal, there was a clear consensus that
the new field should be validated from the start, guaranteeing that all
distributions uploaded to PyPI that declare Core Metadata version 2.4
or higher and have the ``License-Expression`` field will have a valid
expression, such that PyPI and consumers of its packages and metadata
can rely upon to follow the specification here.

The same can be extended to the new ``License-File`` field as well,
to ensure that it is valid and the legally required license files are
present. To be clear, this would not require that any uploaded distribution
have such metadata, only that if they choose to declare it per the
specification in PEP 639, it is assured to be valid.


Source metadata ``license`` key
-------------------------------

Alternative possibilities related to the ``license`` key in the
``pyproject.toml`` project source metadata.


Add ``expression`` and ``files`` subkeys to table
'''''''''''''''''''''''''''''''''''''''''''''''''

A previous draft of PEP 639 added ``expression`` and ``files`` subkeys
to the existing ``license`` table in the project source metadata, to parallel
the existing ``file`` and ``text`` subkeys. While this seemed the
most obvious approach at first glance, it had serious drawbacks
relative to that ultimately taken here.

This means two very different types of metadata are being
specified under the same top-level key that require very different handling,
and unlike the previous arrangement, the subkeys were not mutually
exclusive and could both be specified at once, with some subkeys potentially
being dynamic and others static, and mapping to different Core Metadata fields.

There are further downsides to this as well. Both users and tools would need to
keep track of which fields are mutually exclusive with which of the others,
greatly increasing complexity, and the probability
of errors. Having so many different fields under the
same key leads to a much more complex mapping between
``[project]`` keys and Core Metadata fields, not in keeping with :pep:`621`.
This causes the ``[project]`` table naming and structure to diverge further
from both the Core Metadata and native formats of the various popular packaging
tools that use it. Finally, this results in the spec being significantly more
complex to understand and implement than the alternatives.

The approach PEP 639 now takes, using the reserved top-level string value
of the ``license`` key, adding a new ``license-files`` key
and deprecating the ``license`` table subkeys (``text`` and ``file``),
avoids most of the issues identified above,
and results in a much clearer and cleaner design overall.
It allows ``license`` and ``license-files`` to be tagged
``dynamic`` independently, separates two independent types of metadata
(syntactically and semantically), restores a closer to 1:1 mapping of
``[project]`` table keys to Core Metadata fields,
and reduces nesting by a level for both.
Other than adding one extra key to the file, there was no significant
apparent downside to this latter approach, so it was adopted for PEP 639.


Add an ``expression`` subkey instead of a string value
''''''''''''''''''''''''''''''''''''''''''''''''''''''

Adding just an ``expression`` subkey to the ``license`` table,
instead of using the top-level string value,
would be more explicit for readers and writers,
in line with PEP 639's goals.
However, it still has the downsides listed above
that are not specific to the inclusion of the ``files`` key.

Relative to a flat string value,
it adds complexity and an extra level of nesting,
and requires users and tools to remember and handle
the mutual exclusivity of the subkeys
and remember which are deprecated,
instead of cleanly deprecating the table subkeys as a whole.
Furthermore, it is less clearly the "default" choice for modern use,
given users tend to gravitate toward the most obvious option.
Finally, it seems reasonable to follow the suggested guidance in :pep:`621`,
given the top-level string value was specifically reserved for this purpose.


Define a new top-level ``license-expression`` key
'''''''''''''''''''''''''''''''''''''''''''''''''

An earlier version of PEP 639 defined a new, top-level ``license-expression``
under the ``[project]`` table,
rather than using the string value of the ``license`` key.
This was seen as clearer for readers and writers,
in line with the goals of PEP 639.

While differences from existing tool formats (and Core Metadata
field names) have precedent in :pep:`621`, repurposing an existing key to mean
something different (and map to a different Core Metadata field),
with distinct and incompatible syntax does not, 
and could cause ambiguity for readers and authors.

Also, per the `project source metadata spec <pyprojecttomldynamic_>`__,
this would allow separately marking the ``[project]`` keys
corresponding to the ``License`` and ``License-Expression`` metadata fields
as ``dynamic``,
avoiding a potential concern with back-filling the ``License`` field
from the ``License-Expression`` field as PEP 639 currently allows
without it as ``license`` as dynamic
(which would not be possible, since they both map to the same top-level key).

However, community consensus favored using
the top-level string value of the existing ``license`` key,
as :pep:`reserved for this purpose by PEP 621 <621#license>`:

    A practical string value for the license key has been purposefully left
    out to allow for a future PEP to specify support for SPDX expressions
    (the same logic applies to any sort of "type" field specifying what
    license the file or text represents).

This is simpler for users to remember and type,
avoids adding a new top-level key while taking advantage of an existing one,
guides users toward using a license expression as the default,
and follows what was envisioned in the original :pep:`621`.

Additionally, this allows cleanly deprecating the table values
without deprecating the key itself,
and makes them mutually exclusive without users having to remember
and tools having to enforce it.

Finally, consistency with other tool formats and the underlying Core Metadata
was not a sufficient priority
to override the advantages of using the existing key,
and the ``dynamic`` concerns were mostly mitigated by
not specifying legacy license to license expression conversion at build time,
explicitly specifying backfilling the ``License`` field when not ``dynamic``,
and the fact that both fields are mutually exclusive,
so there is little practical need to distinguish which is dynamic.

Therefore, a top-level string value for ``license`` was adopted for PEP 639,
as an earlier working draft had temporarily specified.


Add a ``type`` key to treat ``text`` as expression
''''''''''''''''''''''''''''''''''''''''''''''''''

Instead of using the reserved top-level string value
of the ``license`` key in the ``[project]`` table,
one could add a ``type`` subkey to the ``license`` table
to control whether ``text`` (or a string value)
is interpreted as free-text or a license expression. This could make
backward compatibility a bit easier, as older tools could ignore
it and always treat ``text`` as ``license``, while newer tools would
know to treat it as a license expression, if ``type`` was set appropriately.
Indeed, :pep:`621` seems to suggest something of this sort as a possible
way that SPDX license expressions could be implemented.

However, it has got all the same downsides as in the previous item,
including greater complexity, a more complex mapping between the project
source metadata and Core Metadata and inconsistency between the presentation
in tool config, project source metadata and Core Metadata,
a harder deprecation, further bikeshedding over what to name it,
and inability to mark one but not the other as dynamic, among others.

In addition, while theoretically a little easier in the short
term, in the long term it would mean users would always have to remember
to specify the correct ``type`` to ensure their license expression is
interpreted correctly, which adds work and potential for error; we could
never safely change the default while being confident that users
understand that what they are entering is unambiguously a license expression,
with all the false positive and false negative issues as above.

Therefore, for these reasons, we reject this here in favor of
the reserved string value of the ``license`` key.


Must be marked dynamic to back-fill
'''''''''''''''''''''''''''''''''''

The ``license`` key in the ``pyproject.toml`` could be required to be
explicitly set to dynamic in order for the ``License`` Core Metadata field
to be automatically back-filled from
the top-level string value of the ``license`` key.
This would be more explicit that the filling will be done,
as strictly speaking the ``license`` key is not (and cannot be) specified in
``pyproject.toml``, and satisfies a stricter interpretation of the letter
of the previous :pep:`621` specification that PEP 639 revises.

However, this doesn't seem to be necessary, because it is simply using the
static, literal value of the ``license`` key, as specified
strictly in PEP 639. Therefore, any conforming tool can
deterministically derive this using only the static data
in the ``pyproject.toml`` file itself.

Furthermore, this actually adds significant ambiguity, as it means the value
could get filled arbitrarily by other tools, which would in turn compromise
and conflict with the value of the new ``License-Expression`` field, which is
why such is explicitly prohibited by PEP 639. Therefore, not marking it as
``dynamic`` will ensure it is only handled in accordance with PEP 639's
requirements.

Finally, users explicitly being told to mark it as ``dynamic``, or not, to
control filling behavior seems to be a bit of a misuse of the ``dynamic``
field as apparently intended, and prevents tools from adapting to best
practices (fill, don't fill, etc.) as they develop and evolve over time.


Source metadata ``license-files`` key
-------------------------------------

Alternatives considered for the ``license-files`` key in the
``pyproject.toml`` ``[project]`` table, primarily related to the
path/glob type handling.


Add a ``type`` subkey to ``license-files``
''''''''''''''''''''''''''''''''''''''''''

Instead of defining mutually exclusive ``paths`` and ``globs`` subkeys
of the ``license-files`` ``[project]`` table key, we could
achieve the same effect with a ``files`` subkey for the list and
a ``type`` subkey for how to interpret it. However, it offers no
real advantage in exchange for requiring more keystrokes,
increased complexity, as well as less flexibility in allowing both,
or another additional subkey in the future, as well as the need to bikeshed
over the subkey name. Therefore, it was rejected.


Only accept verbatim paths
''''''''''''''''''''''''''

Globs could be disallowed as values to the ``license-files``
key in ``pyproject.toml`` and only verbatim paths allowed.
This would ensure that all license files are explicitly specified,
found and included, and the source metadata
is completely static in the strictest sense of the term, without tools
having to inspect the rest of the project source files to determine exactly
what license files will be included and what the ``License-File`` values
will be. This would also simplify the spec and tool implementation.

However, practicality beats purity here. Globs are already supported
by many existing tools, and explicitly
specifying the full path to every license file would be unnecessarily tedious
for complex projects with vendored dependencies. More
critically, it would make it much easier to accidentally miss a required
legal file, creating the package illegal to distribute.

Tools can still determine the files to be included,
based only on the glob patterns the user specified and the
filenames in the package, without installing it, executing its code or even
examining its files. Furthermore, tools are explicitly allowed to warn
if specified glob patterns don't match any files.
And, of course, sdists, wheels and others will have the full static list
of files specified in their distribution metadata.

Perhaps most importantly, this would also exclude the currently specified
default value widely used by the most popular tools, and thus
be a major break to backward compatibility.
And of course, authors are welcome to specify their license
files explicitly via the ``paths`` table subkey, once they are aware of it and
find it suitable for their project.


Only accept glob patterns
'''''''''''''''''''''''''

Conversely, all ``license-files`` strings could be treated as glob patterns.
This would slightly simplify the spec and implementation, avoid an extra level
of nesting, and more closely match the configuration format of existing tools.

However, for the cost of a few characters, it ensures users are aware
whether they are entering globs or verbatim paths. Furthermore, allowing
license files to be specified as literal paths avoids edge cases, such as those
containing glob characters (or those confusingly or even maliciously similar
to them, as described in :pep:`672`).

Including an explicit ``paths`` value ensures that the resulting
``License-File`` metadata is correct, complete and purely static in the
strictest sense of the term, with all license paths explicitly specified
in the ``pyproject.toml`` file, guaranteed to be included and with an early
error if any are missing. This is not practical to do, at least without
serious limitations for many workflows, if we must assume the items
are glob patterns rather than literal paths.

This allows tools to locate them and know the exact values of the
``License-File`` Core Metadata fields without having to traverse the
source tree of the project and match globs, potentially allowing
more reliable programmatic inspection and processing.

Therefore, given the relatively small cost and the significant benefits,
this approach was not adopted.


Infer whether paths or globs
''''''''''''''''''''''''''''

It was considered whether to simply allow specifying an array of strings
directly for the ``license-files`` key, rather than making it a table with
explicit ``paths`` and ``globs``. This would be simpler and avoid
an extra level of nesting, and more closely match the configuration format
of existing tools. However, it was ultimately rejected in favor of separate,
mutually exclusive ``paths`` and ``globs`` table subkeys.

In practice, it only saves six extra characters in the ``pyproject.toml``
(``license-files = [...]`` vs ``license-files.globs = [...]``), but allows
the user to explicitly declare their intent and serves as an unambiguous
indicator for tools to parse them as globs rather than verbatim paths.

This, in turn, allows for clearly specified tool
behaviors for each case, many of which would be unreliable or impossible
without it and
behave more intuitively overall. These include, with ``paths``,
guaranteeing that each specified file is included and immediately
raising an error if one is missing, and with ``globs``, checking glob syntax,
excluding unwanted backup, temporary, or other such files,
and optionally warning if a glob doesn't match any files.
This also avoids edge cases (e.g. paths that contain glob characters) and
reliance on heuristics to determine interpretation.


.. _639-license-files-allow-flat-array:

Also allow a flat array value
'''''''''''''''''''''''''''''

Initially, after deciding to define ``license-files`` as a table of ``paths``
and ``globs``, thought was given to making a top-level string array under the
``license-files`` key mean one or the other (probably ``globs``, to match most
current tools). This is slightly shorter, indicates to
the users which one is a preferred one, and allows a cleaner handling of
the empty case.

However, this only saves six characters in the best case, and there
isn't an obvious choice.

Flat may be better than nested, but in the face of ambiguity, users
may not resist the temptation to guess. Requiring users to explicitly specify
one or the other ensures they are aware of how their inputs will be handled,
and is more readable for others. It also makes
the spec and tool implementation slightly more complicated, and it can always
be added in the future, but not removed without breaking backward
compatibility. And finally, for the "preferred" option, it means there is
more than one obvious way to do it.

Therefore, per :pep:`20`, the Zen of Python, this approach is rejected.


Allow both ``paths`` and ``globs`` subkeys
''''''''''''''''''''''''''''''''''''''''''

Allowing both ``paths`` and ``globs`` subkeys to be specified under the
``license-files`` table was considered, as it could potentially allow
more flexible handling for particularly complex projects.

However, given the existing proposed approach already matches or exceeds the
capabilities of those offered in tools' config files, there isn't
clear demand for this, and it adds a large
amount of complexity in tool implementations and ``pyproject.toml``
for relatively minimal gain.

There would be many more edge cases to deal with, such as how to handle files
matched by both lists, and it conflicts with the current
specification for how tools should behave, such as when
no files match.

Like the previous, if there is a clear need for it, it can be always allowed
in the future in a backward-compatible manner,
while the same is not true of disallowing it.
Therefore, it was decided to require the two subkeys to be mutually exclusive.


Rename ``paths`` subkey to ``files``
''''''''''''''''''''''''''''''''''''

Initially, the name ``files`` was considered instead of the ``paths`` for the
subkey of ``license-files`` table. However, ``paths`` was ultimately
chosen to avoid duplication between
the table name (``license-files``) and the subkey name (``files``), i.e.
``license-files.files = ["LICENSE.txt"]``. It made it seem like
the preferred subkey when it was not, and didn't describe the format of the
string entry similarly to the existing ``globs``.


Must be marked dynamic to use defaults
''''''''''''''''''''''''''''''''''''''

With a restrictive
interpretation of :pep:`621`'s description of the ``dynamic`` list it may
seem sensible to require the ``license-files`` key to be marked as
``dynamic`` for the default glob patterns to be used, or alternatively
for license files to be matched and included at all.

However, this is just declaring a static, strictly-specified default value,
required to be used exactly by all conforming tools, similarly to any other set
of glob patterns the user themself may specify.
The resulting ``License-File`` Core Metadata values
can be determined through inspecting a list of files in the source, without
executing code, or even inspecting file contents.

Moreover, even if this were not so, this
interpretation would be backwards-incompatible with the existing
format, and be inconsistent with the behavior with the existing tools.
Further, this would create a serious risk of a large number of
projects unknowingly no longer including legally mandatory license files,
and is thus not a sane default.

Finally, not defining the default as dynamic allows authors to unambiguously
indicate when their build/packaging tools are going to be
handling the inclusion of license files themselves;
to do otherwise would defeat the purpose of the ``dynamic`` list.


License file paths
------------------

Alternatives related to the paths and locations of license files in the source
and built distributions.


Flatten license files in subdirectories
'''''''''''''''''''''''''''''''''''''''

Previous drafts of PEP 639 didn't specify how to handle the license files
in subdirectories. Currently, the `Wheel <wheelfiles_>`__ and
`Setuptools <setuptoolsfiles_>`__ projects flatten all license files
into the ``.dist-info`` directory without preserving the source subdirectory
hierarchy.

While this approach and matches existing ad hoc practice,
it can result in name conflicts and license files clobbering others,
with no defined behavior for how to resolve them, and leaving the
package legally un-distributable without any clear indication that
the specified license files have not been included.

Furthermore, this leads to inconsistent relative file paths for non-root
license files between the source, sdist and wheel, and prevents the paths
given in the "static" ``[project]`` table metadata from being truly static.
Finally, the source directory structure often holds valuable information
about what the licenses apply to,
which is lost when flattening them and far from trivial to reconstruct.

To resolve this, the PEP now proposes reproducing the source directory
structure of the original
license files inside the ``.dist-info`` directory. The only downside of this
approach is having a more nested ``.dist-info``
directory. The following proposal rooting the license files under a ``licenses``
subdirectory eliminates both name collisions and the clutter problem entirely.


Resolve name conflicts differently
''''''''''''''''''''''''''''''''''

Rather than preserving the source directory structure for license files
inside the ``.dist-info`` directory, we could specify some other mechanism
for conflict resolution, such as pre- or appending the parent directory name
to the license filename, traversing up the tree until the name was unique,
to avoid excessively nested directories.

However, this would not address the path consistency issues, would require
much more discussion and further complicate
the specification. Therefore, it was rejected in
favor of the more obvious solution of just preserving the
source subdirectory layout, as many stakeholders have advocated for.


Dump directly in ``.dist-info``
'''''''''''''''''''''''''''''''

Previously, the included license files were stored directly in the top-level
``.dist-info`` directory of built wheels and installed projects.

However, this leads to a more cluttered ``.dist-info`` directory
as opposed to separating
licenses into their own namespace. There is still a
risk of collision with custom license filenames
(e.g. ``RECORD``, ``METADATA``) in the ``.dist-info`` directory, which
would require limiting the potential filenames used. Finally,
putting licenses into their own specified subdirectory would allow
humans and tools to correctly manipulate
all of them at once (such as in distro packaging, legal checks, etc.)
without having to reference each of their paths from the Core Metadata.

Therefore, the simplest and most obvious solution, as suggested by several
on the Wheel
and Setuptools implementation issues, is to root the license files
relative to a ``licenses`` subdirectory of ``.dist-info``. This is simple
to implement and solves all the problems noted here, without significant
drawbacks relative to other more complex options.

It does make the specification a bit more complex, but
implementation should remain equally simple. It does mean that wheels
produced with following this change will have differently-located licenses
than those prior, but as this was already true for those in subdirectories,
and until PEP 639 there was no way of
accessing these files programmatically, this should not pose
significant problems in practice.


Add new ``licenses`` category to wheel
''''''''''''''''''''''''''''''''''''''

Instead of defining a root license directory (``licenses``) inside
the Core Metadata directory (``.dist-info``) for wheels, we could instead
define a new category (and, presumably, a corresponding install scheme),
similar to the others currently included under ``.data`` in the wheel archive,
specifically for license files, called (e.g.) ``licenses``. This was mentioned
by the wheel creator, and would allow installing licenses somewhere more
platform-appropriate and flexible than just the ``.dist-info`` directory
in the site path.

However, at present, PEP 639 does not implement this idea, and it is
deferred to a future one. It would add significant complexity and friction
to PEP 639, being primarily concerned with standardizing existing practice
and updating the Core Metadata specification. Furthermore, doing so could
require modifying ``sysconfig`` and the install schemes specified
therein, alongside Wheel, Installer and other tools, which would be a
non-trivial undertaking. While potentially slightly more complex for
repackagers, the current proposal still
ensures all license files are included in a single dedicated directory,
and thus should still
greatly improve the status quo in this regard.

In addition, this approach is not fully backwards compatible (since it
isn't transparent to tools that simply extract the wheel), is a greater
departure from existing practice and would lead to more inconsistent
license install locations from wheels of different versions. Finally,
this would mean licenses would not be installed as close to their
associated code, there would be more variability in the license root path
across platforms and between built distributions and installed projects,
accessing installed licenses programmatically would be more difficult, and a
suitable install location and method would need to be created that would avoid
name clashes.

Therefore, to keep PEP 639 in scope, the current approach was retained.


Name the subdirectory ``license_files``
'''''''''''''''''''''''''''''''''''''''

Both ``licenses`` and ``license_files`` have been suggested as potential
names for the root license directory inside ``.dist-info`` of wheels and
installed projects. An initial draft of the PEP specified the former
due to being slightly clearer and consistent with the
name of the Core Metadata field (``License-File``)
and the ``[project]`` table key (``license-files``).
However, the current version of the PEP adopts the ``licenses`` name,
due to a general preference by the community for its shorter length
and the lack of a separator character.


Other ideas
-----------

Miscellaneous proposals, possibilities and discussion points that were
ultimately not adopted.


Map identifiers to license files
''''''''''''''''''''''''''''''''

This would require using a mapping, which would add extra complexity to how
license are documented and add an additional nesting level.

A mapping would be needed, as it cannot be guaranteed that all expressions
(keys) have a single license file associated with them (e.g.
GPL with an exception may be in a single file) and that any expression
does not have more than one. (e.g. an Apache license ``LICENSE`` and
its ``NOTICE`` file, for instance, are two distinct files).
For most common cases, a single license expression and one or more license
files would be perfectly adequate. In the rarer and more complex cases where
there are many licenses involved, authors can still safely use the fields
specified here, just with a slight loss of clarity by not specifying which
text file(s) map to which license identifier (though each license identifier
has corresponding SPDX-registered
full license text), while not forcing the more complex mapping
on the large majority of users who do not need or want it.

We could of course have a data field with multiple possible value types
but this could be a source of confusion.
This is what has been done, for instance, in npm (historically) and in Rubygems
(still today), and as result tools need to test the type of the metadata field
before using it in code, while users are confused about when to use a list or a
string. Therefore, this approach is rejected.


Map identifiers to source files
'''''''''''''''''''''''''''''''

As discussed previously, file-level notices are out of scope for PEP 639,
and the existing ``SPDX-License-Identifier`` `convention <spdxid_>`__ can
already be used if this is needed without further specification here.


Don't freeze compatibility with a specific SPDX version
'''''''''''''''''''''''''''''''''''''''''''''''''''''''

PEP 639 could omit specifying a specific SPDX specification version,
or one for the list of valid license identifiers, which would allow
more flexible updates as the specification evolves.

However, serious concerns were expressed about a future SPDX update breaking
compatibility with existing expressions and identifiers, leaving current
packages with invalid metadata per the definition in PEP 639. Requiring
compatibility with a specific version of these specifications here
and a PEP or similar process to update it avoids this contingency,
and follows the practice of other packaging ecosystems.

Therefore, it was `decided <spdxversion_>`__ to specify a minimum version
and require tools to be compatible with it, while still allowing updates
so long as they don't break backward compatibility. This enables
tools to immediate take advantage of improvements and accept new
licenses balancing flexibility and compatibility.


.. _639-rejected-ideas-difference-license-source-binary:

Different licenses for source and binary distributions
''''''''''''''''''''''''''''''''''''''''''''''''''''''

As an additional use case, it was asked whether it was in scope for
PEP 639 to handle cases where the license expression for a binary distribution
(wheel) is different from that for a source distribution (sdist), such
as in cases of non-pure-Python packages that compile and bundle binaries
under different licenses than the project itself. An example cited was
`PyTorch <pytorch_>`__, which contains CUDA from Nvidia, which is freely
distributable but not open source.

However, given the inherent complexity here and a lack of an obvious
mechanism to do so, the fact that each wheel would need its own license
information, lack of support on PyPI for exposing license info on a
per-distribution archive basis, and the relatively niche use case, it was
determined to be out of scope for PEP 639, and left to a future PEP
to resolve if sufficient need and interest exists and an appropriate
mechanism can be found.


.. _pyprojecttomldynamic: https://packaging.python.org/en/latest/specifications/pyproject-toml/#dynamic
.. _pytorch: https://pypi.org/project/torch/
.. _reusediscussion: https://github.com/pombredanne/spdx-pypi-pep/issues/7
.. _setuptoolsfiles: https://github.com/pypa/setuptools/issues/2739
.. _spdxid: https://spdx.dev/ids/
.. _spdxversion: https://github.com/pombredanne/spdx-pypi-pep/issues/6
.. _wheelfiles: https://github.com/pypa/wheel/issues/138
