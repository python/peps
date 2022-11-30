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
Initially, this would merely cause a warning (or even pass silently),
but would eventually be treated as an error by modern tooling.

This offered the potential benefit of greater backwards-compatibility,
easing the community into using SPDX license expressions while taking advantage
of packages that already have them (either intentionally or coincidentally),
and avoided adding yet another license-related field.

However, following substantial discussion, consensus was reached that a
dedicated ``License-Expression`` field was the preferred overall approach.
The presence of this field is an unambiguous signal that a package
intends it to be interpreted as a valid SPDX identifier, without the need
for complex and potentially erroneous heuristics, and allows tools to
easily and unambiguously detect invalid content.

This avoids both false positive (``License`` values that a package author
didn't explicitly intend as an explicit SPDX identifier, but that happen
to validate as one), and false negatives (expressions the author intended
to be valid SPDX, but due to a typo or mistake are not), which are otherwise
not clearly distinguishable from true positives and negatives, an ambiguity
at odds with the goals of PEP 639.

Furthermore, it allows both the existing ``License`` field and
the license classifiers to be more easily deprecated,
with tools able to cleanly distinguish between packages intending to
affirmatively conform to the updated specification in PEP 639 or not,
and adapt their behavior (warnings, errors, etc) accordingly.
Otherwise, tools would either have to allow duplicative and potentially
conflicting ``License`` fields and classifiers, or warn/error on the
substantial number of existing packages that have SPDX identifiers as the
value for the ``License`` field, intentionally or otherwise (e.g. ``MIT``).

Finally, it avoids changing the behavior of an existing metadata field,
and avoids tools having to guess the ``Metadata-Version`` and field behavior
based on its value rather than merely its presence.

While this would mean the subset of existing distributions containing
``License`` fields valid as SPDX license expressions wouldn't automatically be
recognized as such, this only requires appending a few characters to the key
name in the project's source metadata, and PEP 639 provides extensive
guidance on how this can be done automatically by tooling.

Given all this, it was decided to proceed with defining a new,
purpose-created field, ``License-Expression``.


Re-Use the ``License`` field with a value prefix
''''''''''''''''''''''''''''''''''''''''''''''''

As an alternative to the previous, prefixing SPDX license expressions with,
e.g. ``spdx:`` was suggested to reduce the ambiguity inherent in re-using
the ``License`` field. However, this effectively amounted to creating
a field within a field, and doesn't address all the downsides of
keeping the ``License`` field. Namely, it still changes the behavior of an
existing metadata field, requires tools to parse its value
to determine how to handle its content, and makes the specification and
deprecation process more complex and less clean.

Yet, it still shares a same main potential downside as just creating a new
field: projects currently using valid SPDX identifiers in the ``License``
field, intentionally or not, won't be automatically recognized, and requires
about the same amount of effort to fix, namely changing a line in the
project's source metadata. Therefore, it was rejected in favor of a new field.


Don't make ``License-Expression`` mutually exclusive
''''''''''''''''''''''''''''''''''''''''''''''''''''

For backwards compatibility, the ``License`` field and/or the license
classifiers could still be allowed together with the new
``License-Expression`` field, presumably with a warning. However, this
could easily lead to inconsistent, and at the very least duplicative
license metadata in no less than *three* different fields, which is
squarely contrary to the goals of PEP 639 of making the licensing story
simpler and unambiguous. Therefore, and in concert with clear community
consensus otherwise, this idea was soundly rejected.


Don't deprecate existing ``License`` field and classifiers
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

Several community members were initially concerned that deprecating the
existing ``License`` field and classifiers would result in
excessive churn for existing package authors and raise the barrier to
entry for new ones, particularly everyday Python developers seeking to
package and publish their personal projects without necessarily caring
too much about the legal technicalities or being a "license lawyer".
Indeed, every deprecation comes with some non-zero short-term cost,
and should be carefully considered relative to the overall long-term
net benefit. And at the minimum, this change shouldn't make it more
difficult for the average Python developer to share their work under
a license of their choice, and ideally improve the situation.

Following many rounds of proposals, discussion and refinement,
the general consensus was clearly in favor of deprecating the legacy
means of specifying a license, in favor of "one obvious way to do it",
to improve the currently complex and fragmented story around license
documentation. Not doing so would leave three different un-deprecated ways of
specifying a license for a package, two of them ambiguous, less than
clear/obvious how to use, inconsistently documented and out of date.
This is more complex for all tools in the ecosystem to support
indefinitely (rather than simply installers supporting older packages
implementing previous frozen metadata versions), resulting in a non-trivial
and unbounded maintenance cost.

Furthermore, it leads to a more complex and confusing landscape for users with
three similar but distinct options to choose from, particularly with older
documentation, answers and articles floating around suggesting different ones.
Of the three, ``License-Expression`` is the simplest and clearest to use
correctly; users just paste in their desired license identifier, or select it
via a tool, and they're done; no need to learn about Trove classifiers and
dig through the list to figure out which one(s) apply (and be confused
by many ambiguous options), or figure out on their own what should go
in the ``license`` key (anything from nothing, to the license text,
to a free-form description, to the same SPDX identifier they would be
entering in the ``license`` key anyway, assuming they can
easily find documentation at all about it). In fact, this can be
made even easier thanks to the new field. For example, GitHub's popular
`ChooseALicense.com <choosealicense_>`__ links to how to add SPDX license
identifiers to the project source metadata of various languages that support
them right in the sidebar of every license page; the SPDX support in this
PEP enables adding Python to that list.

For current package maintainers who have specified a ``License`` or license
classifiers, PEP 639 only recommends warnings and prohibits errors for
all but publishing tools, which are allowed to error if their intended
distribution platform(s) so requires. Once maintainers are ready to
upgrade, for those already using SPDX license expressions (accidentally or not)
this only requires appending a few characters to the key name in the
project's source metadata, and for those with license classifiers that
map to a single unambiguous license, or another defined case (public domain,
proprietary), they merely need to drop the classifier and paste in the
corresponding license identifier. PEP 639 provides extensive guidance and
examples, as will other resources, as well as explicit instructions for
automated tooling to take care of this with no human changes needed.
More complex cases where license metadata is currently specified may
need a bit of human intervention, but in most cases tools will be able
to provide a list of options following the mappings in PEP 639, and
these are typically the projects most likely to be constrained by the
limitations of the existing license metadata, and thus most benefited
by the new fields in PEP 639.

Finally, for unmaintained packages, those using tools supporting older
metadata versions, or those who choose not to provide license metadata,
no changes are required regardless of the deprecation.


Don't mandate validating new fields on PyPI
'''''''''''''''''''''''''''''''''''''''''''

Previously, while PEP 639 did include normative guidelines for packaging
publishing tools (such as Twine), it did not provide specific guidance
for PyPI (or other package indices) as to whether and how they
should validate the ``License-Expression`` or ``License-File`` fields,
nor how they should handle using them in combination with the deprecated
``License`` field or license classifiers. This simplifies the specification
and either defers implementation on PyPI to a later PEP, or gives
discretion to PyPI to enforce the stated invariants, to minimize
disruption to package authors.

However, this had been left unstated from before the ``License-Expression``
field was separate from the existing ``License``, which would make
validation much more challenging and backwards-incompatible, breaking
existing packages. With that change, there was a clear consensus that
the new field should be validated from the start, guaranteeing that all
distributions uploaded to PyPI that declare Core Metadata version 2.4
or higher and have the ``License-Expression`` field will have a valid
expression, such that PyPI and consumers of its packages and metadata
can rely upon to follow the specification here.

The same can be extended to the new ``License-File`` field as well,
to ensure that it is valid and the legally required license files are
present, and thus it is lawful for PyPI, users and downstream consumers
to distribute the package. (Of course, this makes no *guarantee* of such
as it is ultimately reliant on authors to declare them, but it improves
assurance of this and allows doing so in the future if the community so
decides.) To be clear, this would not require that any uploaded distribution
have such metadata, only that if they choose to declare it per the new
specification in PEP 639, it is assured to be valid.


Source metadata ``license`` key
-------------------------------

Alternate possibilities related to the ``license`` key in the
``pyproject.toml`` project source metadata.


Add ``expression`` and ``files`` subkeys to table
'''''''''''''''''''''''''''''''''''''''''''''''''

A previous working draft of PEP 639 added ``expression`` and ``files`` subkeys
to the existing ``license`` table in the project source metadata, to parallel
the existing ``file`` and ``text`` subkeys. While this seemed perhaps the
most obvious approach at first glance, it had several serious drawbacks
relative to that ultimately taken here.

Most saliently, this means two very different types of metadata are being
specified under the same top-level key that require very different handling,
and furthermore, unlike the previous arrangement, the subkeys were not mutually
exclusive and can both be specified at once, and with some subkeys potentially
being dynamic and others static, and mapping to different Core Metadata fields.

Furthermore, this leads to a conflict with marking the key as ``dynamic``
(assuming that is intended to specify the ``[project]`` table keys,
as that PEP seems to imprecisely imply,
rather than Core Metadata fields), as either or both would have
to be treated as ``dynamic``.
Grouping both license expressions and license files under the same key
forces an "all or nothing" approach, and creates ambiguity as to user intent.

There are further downsides to this as well. Both users and tools would need to
keep track of which fields are mutually exclusive with which of the others,
greatly increasing cognitive and code complexity, and in turn the probability
of errors. Conceptually, juxtaposing so many different fields under the
same key is rather jarring, and leads to a much more complex mapping between
``[project]`` keys and Core Metadata fields, not in keeping with :pep:`621`.
This causes the ``[project]`` table naming and structure to diverge further
from both the Core Metadata and native formats of the various popular packaging
tools that use it. Finally, this results in the spec being significantly more
complex and convoluted to understand and implement than the alternatives.

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
instead of using the reserved top-level string value,
would be more explicit for readers and writers,
in line with PEP 639's goals.
However, it still has the downsides listed above
that are not specific to the inclusion of the ``files`` key.

Relative to a flat string value,
it adds verbosity, complexity and an extra level of nesting,
and requires users and tools to remember and handle
the mutual exclusivity of the subkeys
and remember which are deprecated and which are not,
instead of cleanly deprecating the table subkeys as a whole.
Furthermore, it is less clearly the "default" choice for modern use,
given users tend to gravitate toward the simplest and most obvious option.
Finally, it seems reasonable to follow the suggested guidance in :pep:`621`,
given the top-level string value was specifically reserved for this purpose.


Define a new top-level ``license-expression`` key
'''''''''''''''''''''''''''''''''''''''''''''''''

An earlier version of PEP 639 defined a new, top-level ``license-expression``
under the ``[project]`` table,
rather than using the reserved string value of the ``license`` key.
This was seen as clearer and more explicit for readers and writers,
in line with the goals of PEP 639.

Additionally, while differences from existing tool formats (and Core Metadata
field names) have precedent in :pep:`621`,
using a key with an identical name as in most/all current tools
to mean something different (and map to a different Core Metadata field),
with distinct and incompatible syntax and semantics, does not,
and could cause confusion and ambiguity for readers and authors.

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

This is shorter and simpler for users to remember and type,
avoids adding a new top-level key while taking advantage of an existing one,
guides users toward using a license expression as the default,
and follows what was envisioned in the original :pep:`621`.

Additionally, this allows cleanly deprecating the table values
without deprecating the key itself,
and makes them inherently mutually exclusive without users having to remember
and tools having to enforce it.

Finally, consistency with other tool formats and the underlying Core Metadata
was not considered a sufficient priority
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
backward compatibility a little more seamless, as older tools could ignore
it and always treat ``text`` as ``license``, while newer tools would
know to treat it as a license expression, if ``type`` was set appropriately.
Indeed, :pep:`621` seems to suggest something of this sort as a possible
alternative way that SPDX license expressions could be implemented.

However, all the same downsides as in the previous item apply here,
including greater complexity, a more complex mapping between the project
source metadata and Core Metadata and inconsistency between the presentation
in tool config, project source metadata and Core Metadata,
a much less clean deprecation, further bikeshedding over what to name it,
and inability to mark one but not the other as dynamic, among others.

In addition, while theoretically potentially a little easier in the short
term, in the long term it would mean users would always have to remember
to specify the correct ``type`` to ensure their license expression is
interpreted correctly, which adds work and potential for error; we could
never safety change the default while being confident that users
understand that what they are entering is unambiguously a license expression,
with all the false positive and false negative issues as above.

Therefore, for these as well as the same reasons this approach was rejected
for the Core Metadata in favor of a distinct ``License-Expression`` field,
we similarly reject this here in favor of
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
static, verbatim literal value of the ``license`` key, as specified
strictly in PEP 639. Therefore, any conforming tool can trivially,
deterministically and unambiguously derive this using only the static data
in the ``pyproject.toml`` file itself.

Furthermore, this actually adds significant ambiguity, as it means the value
could get filled arbitrarily by other tools, which would in turn compromise
and conflict with the value of the new ``License-Expression`` field, which is
why such is explicitly prohibited by PEP 639. Therefore, not marking it as
``dynamic`` will ensure it is only handled in accordance with PEP 639's
requirements.

Finally, users explicitly being told to mark it as ``dynamic``, or not, to
control filling behavior seems to be a bit of a mis-use of the ``dynamic``
field as apparently intended, and prevents tools from adapting to best
practices (fill, don't fill, etc) as they develop and evolve over time.


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
a ``type`` subkey for how to interpret it. However, the latter offers no
real advantage over the former, in exchange for requiring more keystrokes,
verbosity and complexity, as well as less flexibility in allowing both,
or another additional subkey in the future, as well as the need to bikeshed
over the subkey name. Therefore, it was summarily rejected.


Only accept verbatim paths
''''''''''''''''''''''''''

Globs could be disallowed completely as values to the ``license-files``
key in ``pyproject.toml`` and only verbatim literal paths allowed.
This would ensure that all license files are explicitly specified, all
specified license files are found and included, and the source metadata
is completely static in the strictest sense of the term, without tools
having to inspect the rest of the project source files to determine exactly
what license files will be included and what the ``License-File`` values
will be. This would also modestly simplify the spec and tool implementation.

However, practicality once again beats purity here. Globs are supported and
used by many existing tools for finding license files, and explicitly
specifying the full path to every license file would be unnecessarily tedious
for more complex projects with vendored code and dependencies. More
critically, it would make it much easier to accidentally miss a required
legal file, silently rendering the package illegal to distribute.

Tools can still statically and consistently determine the files to be included,
based only on those glob patterns the user explicitly specified and the
filenames in the package, without installing it, executing its code or even
examining its files. Furthermore, tools are still explicitly allowed to warn
if specified glob patterns (including full paths) don't match any files.
And, of course, sdists, wheels and others will have the full static list
of files specified in their distribution metadata.

Perhaps most importantly, this would also preclude the currently specified
default value, as widely used by the current most popular tools, and thus
be a major break to backward compatibility, tool consistency, and safe
and sane default functionality to avoid unintentional license violations.
And of course, authors are welcome and encouraged to specify their license
files explicitly via the ``paths`` table subkey, once they are aware of it and
if it is suitable for their project and workflow.


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
error should any be missing. This is not practical to do, at least without
serious limitations for many workflows, if we must assume the items
are glob patterns rather than literal paths.

This allows tools to locate them and know the exact values of the
``License-File`` Core Metadata fields without having to traverse the
source tree of the project and match globs, potentially allowing easier,
more efficient and reliable programmatic inspection and processing.

Therefore, given the relatively small cost and the significant benefits,
this approach was not adopted.


Infer whether paths or globs
''''''''''''''''''''''''''''

It was considered whether to simply allow specifying an array of strings
directly for the ``license-files`` key, rather than making it a table with
explicit ``paths`` and ``globs``. This would be somewhat simpler and avoid
an extra level of nesting, and more closely match the configuration format
of existing tools. However, it was ultimately rejected in favor of separate,
mutually exclusive ``paths`` and ``globs`` table subkeys.

In practice, it only saves six extra characters in the ``pyproject.toml``
(``license-files = [...]`` vs ``license-files.globs = [...]``), but allows
the user to more explicitly declare their intent, ensures they understand how
the values are going to be interpreted, and serves as an unambiguous indicator
for tools to parse them as globs rather than verbatim path literals.

This, in turn, allows for more appropriate, clearly specified tool
behaviors for each case, many of which would be unreliable or impossible
without it, to avoid common traps, provide more helpful feedback and
behave more sensibly and intuitively overall. These include, with ``paths``,
guaranteeing that each and every specified file is included and immediately
raising an error if one is missing, and with ``globs``, checking glob syntax,
excluding unwanted backup, temporary, or other such files (as current tools
already do), and optionally warning if a glob doesn't match any files.
This also avoids edge cases (e.g. paths that contain glob characters) and
reliance on heuristics to determine interpretation—the very thing PEP 639
seeks to avoid.


.. _639-license-files-allow-flat-array:

Also allow a flat array value
'''''''''''''''''''''''''''''

Initially, after deciding to define ``license-files`` as a table of ``paths``
and ``globs``, thought was given to making a top-level string array under the
``license-files`` key mean one or the other (probably ``globs``, to match most
current tools). This is slightly shorter and simpler, would allow gently
nudging users toward a preferred one, and allow a slightly cleaner handling of
the empty case (which, at present, is treated identically for either).

However, this again only saves six characters in the best case, and there
isn't an obvious choice; whether from a perspective of preference (both had
clear use cases and benefits), nor as to which one users would naturally
assume.

Flat may be better than nested, but in the face of ambiguity, users
may not resist the temptation to guess. Requiring users to explicitly specify
one or the other ensures they are aware of how their inputs will be handled,
and is more readable for others, both human and machine alike. It also makes
the spec and tool implementation slightly more complicated, and it can always
be added in the future, but not removed without breaking backward
compatibility. And finally, for the "preferred" option, it means there is
more than one obvious way to do it.

Therefore, per :pep:`20`, the Zen of Python, this approach is hereby rejected.


Allow both ``paths`` and ``globs`` subkeys
''''''''''''''''''''''''''''''''''''''''''

Allowing both ``paths`` and ``globs`` subkeys to be specified under the
``license-files`` table was considered, as it could potentially allow
more flexible handling for particularly complex projects, and specify on a
per-pattern rather than overall basis whether ``license-files`` entries
should be treated as ``paths`` or ``globs``.

However, given the existing proposed approach already matches or exceeds the
power and capabilities of those offered in tools' config files, there isn't
clear demand for this and few likely cases that would benefit, it adds a large
amount of complexity for relatively minimal gain, in terms of the
specification, in tool implementations and in ``pyproject.toml`` itself.

There would be many more edge cases to deal with, such as how to handle files
matched by both lists, and it conflicts in multiple places with the current
specification for how tools should behave with one or the other, such as when
no files match, guarantees of all files being included and of the file paths
being explicitly, statically specified, and others.

Like the previous, if there is a clear need for it, it can be always allowed
in the future in a backward-compatible manner (to the extent it is possible
in the first place), while the same is not true of disallowing it.
Therefore, it was decided to require the two subkeys to be mutually exclusive.


Rename ``paths`` subkey to ``files``
''''''''''''''''''''''''''''''''''''

Initially, it was considered whether to name the ``paths`` subkey of the
``license-files`` table ``files`` instead. However, ``paths`` was ultimately
chosen, as calling the table subkey ``files`` resulted in duplication between
the table name (``license-files``) and the subkey name (``files``), i.e.
``license-files.files = ["LICENSE.txt"]``, made it seem like the preferred/
default subkey when it was not, and lacked the same parallelism with ``globs``
in describing the format of the string entry rather than what was being
pointed to.


Must be marked dynamic to use defaults
''''''''''''''''''''''''''''''''''''''

It may seem outwardly sensible, at least with a particularly restrictive
interpretation of :pep:`621`'s description of the ``dynamic`` list, to
consider requiring the ``license-files`` key to be explicitly marked as
``dynamic`` in order for the default glob patterns to be used, or alternatively
for license files to be matched and included at all.

However, this is merely declaring a static, strictly-specified default value
for this particular key, required to be used exactly by all conforming tools
(so long as it is not marked ``dynamic``, negating this argument entirely),
and is no less static than any other set of glob patterns the user themself
may specify. Furthermore, the resulting ``License-File`` Core Metadata values
can still be determined with only a list of files in the source, without
installing or executing any of the code, or even inspecting file contents.

Moreover, even if this were not so, practicality would trump purity, as this
interpretation would be strictly backwards-incompatible with the existing
format, and be inconsistent with the behavior with the existing tools.
Further, this would create a very serious and likely risk of a large number of
projects unknowingly no longer including legally mandatory license files,
making their distribution technically illegal, and is thus not a sane,
much less sensible default.

Finally, aside from adding an additional line of default-required boilerplate
to the file, not defining the default as dynamic allows authors to clearly
and unambiguously indicate when their build/packaging tools are going to be
handling the inclusion of license files themselves rather than strictly
conforming to the project source metadata portions of PEP 639;
to do otherwise would defeat the primary purpose of the ``dynamic`` list
as a marker and escape hatch.


License file paths
------------------

Alternatives related to the paths and locations of license files in the source
and built distributions.


Flatten license files in subdirectories
'''''''''''''''''''''''''''''''''''''''

Previous drafts of PEP 639 were silent on the issue of handling license files
in subdirectories. Currently, the `Wheel <wheelfiles_>`__ and (following its
example) `Setuptools <setuptoolsfiles_>`__ projects flatten all license files
into the ``.dist-info`` directory without preserving the source subdirectory
hierarchy.

While this is the simplest approach and matches existing ad hoc practice,
this can result in name conflicts and license files clobbering others,
with no obvious defined behavior for how to resolve them, and leaving the
package legally un-distributable without any clear indication to users that
their specified license files have not been included.

Furthermore, this leads to inconsistent relative file paths for non-root
license files between the source, sdist and wheel, and prevents the paths
given in the "static" ``[project]`` table metadata from being truly static,
as they need to be flattened, and may potentially overwrite one another.
Finally, the source directory structure often implies valuable information
about what the licenses apply to, and where to find them in the source,
which is lost when flattening them and far from trivial to reconstruct.

To resolve this, the PEP now proposes, as did contributors on both of the
above issues, reproducing the source directory structure of the original
license files inside the ``.dist-info`` directory. This would fully resolve the
concerns above, with the only downside being a more nested ``.dist-info``
directory. There is still a risk of collision with edge-case custom
filenames (e.g. ``RECORD``, ``METADATA``), but that is also the case
with the previous approach, and in fact with fewer files flattened
into the root, this would actually reduce the risk. Furthermore,
the following proposal rooting the license files under a ``licenses``
subdirectory eliminates both collisions and the clutter problem entirely.


Resolve name conflicts differently
''''''''''''''''''''''''''''''''''

Rather than preserving the source directory structure for license files
inside the ``.dist-info`` directory, we could specify some other mechanism
for conflict resolution, such as pre- or appending the parent directory name
to the license filename, traversing up the tree until the name was unique,
to avoid excessively nested directories.

However, this would not address the path consistency issues, would require
much more discussion, coordination and bikeshedding, and further complicate
the specification and the implementations. Therefore, it was rejected in
favor of the simpler and more obvious solution of just preserving the
source subdirectory layout, as many stakeholders have already advocated for.


Dump directly in ``.dist-info``
'''''''''''''''''''''''''''''''

Previously, the included license files were stored directly in the top-level
``.dist-info`` directory of built wheels and installed projects. This followed
existing ad hoc practice, ensured most existing wheels currently using this
feature will match new ones, and kept the specification simpler, with the
license files always being stored in the same location relative to the core
metadata regardless of distribution type.

However, this leads to a more cluttered ``.dist-info`` directory, littered
with arbitrary license files and subdirectories, as opposed to separating
licenses into their own namespace (which per the Zen of Python, :pep:`20`, are
"one honking great idea"). While currently small, there is still a
risk of collision with specific custom license filenames
(e.g. ``RECORD``, ``METADATA``) in the ``.dist-info`` directory, which
would only increase if and when additional files were specified here, and
would require carefully limiting the potential filenames used to avoid
likely conflicts with those of license-related files. Finally,
putting licenses into their own specified subdirectory would allow
humans and tools to quickly, easily and correctly list, copy and manipulate
all of them at once (such as in distro packaging, legal checks, etc)
without having to reference each of their paths from the Core Metadata.

Therefore, now is a prudent time to specify an alternate approach.
The simplest and most obvious solution, as suggested by several on the Wheel
and Setuptools implementation issues, is to simply root the license files
relative to a ``licenses`` subdirectory of ``.dist-info``. This is simple
to implement and solves all the problems noted here, without clear significant
drawbacks relative to other more complex options.

It does make the specification a bit more complex and less elegant, but
implementation should remain equally simple. It does mean that wheels
produced with following this change will have differently-located licenses
than those prior, but as this was already true for those in subdirectories,
and until PEP 639 there was no way of discovering these files or
accessing them programmatically, this doesn't seem likely to pose
significant problems in practice. Given this will be much harder if not
impossible to change later, once the status quo is standardized, tools are
relying on the current behavior and there is much greater uptake of not
only simply including license files but potentially accessing them as well
using the Core Metadata, if we're going to change it, now would be the time
(particularly since we're already introducing an edge-case change with how
license files in subdirs are handled, along with other refinements).

Therefore, the latter has been incorporated into current drafts of PEP 639.


Add new ``licenses`` category to wheel
''''''''''''''''''''''''''''''''''''''

Instead of defining a root license directory (``licenses``) inside
the Core Metadata directory (``.dist-info``) for wheels, we could instead
define a new category (and, presumably, a corresponding install scheme),
similar to the others currently included under ``.data`` in the wheel archive,
specifically for license files, called (e.g.) ``licenses``. This was mentioned
by the wheel creator, and would allow installing licenses somewhere more
platform-appropriate and flexible than just the ``.dist-info`` directory
in the site path, and potentially be conceptually cleaner than including
them there.

However, at present, PEP 639 does not implement this idea, and it is
deferred to a future one. It would add significant complexity and friction
to PEP 639, being primarily concerned with standardizing existing practice
and updating the Core Metadata specification. Furthermore, doing so would
likely require modifying ``sysconfig`` and the install schemes specified
therein, alongside Wheel, Installer and other tools, which would be a
non-trivial undertaking. While potentially slightly more complex for
repackagers (such as those for Linux distributions), the current proposal still
ensures all license files are included, and in a single dedicated directory
(which can easily be copied or relocated downstream), and thus should still
greatly improve the status quo in this regard without the attendant complexity.

In addition, this approach is not fully backwards compatible (since it
isn't transparent to tools that simply extract the wheel), is a greater
departure from existing practice and would lead to more inconsistent
license install locations from wheels of different versions. Finally,
this would mean licenses would not be installed as proximately to their
associated code, there would be more variability in the license root path
across platforms and between built distributions and installed projects,
accessing installed licenses programmatically would be more difficult, and a
suitable install location and method would need to be created, discussed
and decided that would avoid name clashes.

Therefore, to keep PEP 639 in scope, the current approach was retained.


Name the subdirectory ``license_files``
'''''''''''''''''''''''''''''''''''''''

Both ``licenses`` and ``license_files`` have been suggested as potential
names for the root license directory inside ``.dist-info`` of wheels and
installed projects. An initial draft of the PEP specified the former
due to being slightly clearer and consistent with the
name of the Core Metadata field (``License-File``)
and the ``[project]`` table key (``license-files``).
However, the current version of the PEP adopts the ``license`` name,
due to a general preference by the community for its shorter length,
greater simplicity and the lack of a separator character (``_``, ``-``, etc.).


Other ideas
-----------

Miscellaneous proposals, possibilities and discussion points that were
ultimately not adopted.


Map identifiers to license files
''''''''''''''''''''''''''''''''

This would require using a mapping (as two parallel lists would be too prone to
alignment errors), which would add extra complexity to how license
are documented and add an additional nesting level.

A mapping would be needed, as it cannot be guaranteed that all expressions
(keys) have a single license file associated with them (e.g.
GPL with an exception may be in a single file) and that any expression
does not have more than one. (e.g. an Apache license ``LICENSE`` and
its ``NOTICE`` file, for instance, are two distinct files).
For most common cases, a single license expression and one or more license
files would be perfectly adequate. In the rarer and more complex cases where
there are many licenses involved, authors can still safety use the fields
specified here, just with a slight loss of clarity by not specifying which
text file(s) map to which license identifier (though this should be clear in
practice given each license identifier has corresponding SPDX-registered
full license text), while not forcing the more complex data model
(a mapping) on the large majority of users who do not need or want it.

We could of course have a data field with multiple possible value types (it's a
string, it's a list, it's a mapping!) but this could be a source of confusion.
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
more flexible updates as the specification evolves without another
PEP or equivalent.

However, serious concerns were expressed about a future SPDX update breaking
compatibility with existing expressions and identifiers, leaving current
packages with invalid metadata per the definition in PEP 639. Requiring
compatibility with a specific version of these specifications here
and a PEP or similar process to update it avoids this contingency,
and follows the practice of other packaging ecosystems.

Therefore, it was `decided <spdxversion_>`__ to specify a minimum version
and requires tools to be compatible with it, while still allowing updates
so long as they don't break backward compatibility. This enables
tools to immediate take advantage of improvements and accept new
licenses, but also remain backwards compatible with the version
specified here, balancing flexibility and compatibility.


.. _639-rejected-ideas-difference-license-source-binary:

Different licenses for source and binary distributions
''''''''''''''''''''''''''''''''''''''''''''''''''''''

As an additional use case, it was asked whether it was in scope for this
PEP to handle cases where the license expression for a binary distribution
(wheel) is different from that for a source distribution (sdist), such
as in cases of non-pure-Python packages that compile and bundle binaries
under different licenses than the project itself. An example cited was
`PyTorch <pytorch_>`__, which contains CUDA from Nvidia, which is freely
distributable but not open source. `NumPy <numpyissue_>`__ and
`SciPy <scipyissue_>`__ also had similar issues, as reported by the
original author of PEP 639 and now resolved for those cases.

However, given the inherent complexity here and a lack of an obvious
mechanism to do so, the fact that each wheel would need its own license
information, lack of support on PyPI for exposing license info on a
per-distribution archive basis, and the relatively niche use case, it was
determined to be out of scope for PEP 639, and left to a future PEP
to resolve if sufficient need and interest exists and an appropriate
mechanism can be found.


.. _choosealicense: https://choosealicense.com/
.. _numpyissue: https://github.com/numpy/numpy/issues/8689
.. _pyprojecttomldynamic: https://packaging.python.org/en/latest/specifications/pyproject-toml/#dynamic
.. _pytorch: https://pypi.org/project/torch/
.. _reusediscussion: https://github.com/pombredanne/spdx-pypi-pep/issues/7
.. _scipyissue: https://github.com/scipy/scipy/issues/7093
.. _setuptoolsfiles: https://github.com/pypa/setuptools/issues/2739
.. _spdxid: https://spdx.dev/ids/
.. _spdxversion: https://github.com/pombredanne/spdx-pypi-pep/issues/6
.. _wheelfiles: https://github.com/pypa/wheel/issues/138
