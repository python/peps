---
name: New PEP
about: Submit a new draft PEP
labels: "new-pep"
---

<!--

Please read and follow PEP 1 and PEP 12 before submitting a new PEP:

https://peps.python.org/pep-0001/#submitting-a-pep

https://peps.python.org/pep-0012/#how-to-use-this-template

Make sure to include the PEP number in the pull request title; for example:

PEP 9999: <Title of PEP>

See our Contributing Guidelines (CONTRIBUTING.rst) for more information.

Thanks!

-->


# New PEP

<!--

You can use the following checklist when double-checking your PEP,
and you can help complete some of it yourself if you like
by ticking any boxes you're sure about, like this: [x]
If you're unsure about anything, just leave it blank and we'll take a look.

If your PEP is not Standards Track, remove the corresponding section.

-->

## Basic requirements (all PEP Types)

* [ ] File created from the [latest PEP template](https://github.com/python/peps/blob/main/pep-0012/pep-NNNN.rst?plain=1)
* [ ] PEP has next available number, with filename (``pep-NNNN.rst``) and ``PEP`` header set accordingly
* [ ] Title clearly, accurately and concisely describes the content in 79 characters or less
* [ ] ``PEP``, ``Title``, ``Author``, ``Status`` (``Draft``), ``Type`` and ``Created`` headers filled out correctly
* [ ] ``Sponsor``, ``PEP-Delegate``, ``Topic``, ``Requires`` and ``Replaces`` headers completed if appropriate
* [ ] Required sections included
    * [ ] Abstract (first section)
    * [ ] Copyright (last section; exact wording from template required)
* [ ] Code is well-formatted (PEP 7/PEP 8) and is in [code blocks, with the right lexer names](https://peps.python.org/pep-0012/#literal-blocks) if non-Python
* [ ] PEP builds with no warnings, pre-commit checks pass and content displays as intended in the rendered HTML
* [ ] Authors/sponsor added to ``.github/CODEOWNERS`` for the PEP


## Standards Track requirements

* [ ] PEP topic [discussed in a suitable venue](https://peps.python.org/pep-0001/#start-with-an-idea-for-python) with general agreement that a PEP is appropriate
* [ ] [Suggested sections](https://peps.python.org/pep-0012/#suggested-sections) included (unless not applicable)
    * [ ] Motivation
    * [ ] Rationale
    * [ ] Specification
    * [ ] Backwards Compatibility
    * [ ] Security Implications
    * [ ] How to Teach This
    * [ ] Reference Implementation
    * [ ] Rejected Ideas
    * [ ] Open Issues
* [ ] ``Python-Version`` set to valid (pre-beta) future Python version
* [ ] Any project stated in the PEP as supporting/endorsing/benefiting from it confirms such
* [ ] Right before or after initial merging, [PEP discussion thread](https://peps.python.org/pep-0001/#discussing-a-pep) created and linked to in ``Discussions-To`` and ``Post-History``
