# Authors: David Goodger, Ueli Schlaepfer
# Contact: goodger@users.sourceforge.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
This package contains modules for standard tree transforms available
to Docutils components. Tree transforms serve a variety of purposes:

- To tie up certain syntax-specific "loose ends" that remain after the
  initial parsing of the input plaintext. These transforms are used to
  supplement a limited syntax.

- To automate the internal linking of the document tree (hyperlink
  references, footnote references, etc.).

- To extract useful information from the document tree. These
  transforms may be used to construct (for example) indexes and tables
  of contents.

Each transform is an optional step that a Docutils Reader may choose to
perform on the parsed document, depending on the input context. A Docutils
Reader may also perform Reader-specific transforms before or after performing
these standard transforms.
"""

__docformat__ = 'reStructuredText'


from docutils import languages, ApplicationError, TransformSpec


class TransformError(ApplicationError): pass


class Transform:

    """
    Docutils transform component abstract base class.
    """

    default_priority = None
    """Numerical priority of this transform, 0 through 999 (override)."""

    def __init__(self, document, startnode=None):
        """
        Initial setup for in-place document transforms.
        """

        self.document = document
        """The document tree to transform."""

        self.startnode = startnode
        """Node from which to begin the transform.  For many transforms which
        apply to the document as a whole, `startnode` is not set (i.e. its
        value is `None`)."""

        self.language = languages.get_language(
            document.settings.language_code)
        """Language module local to this document."""

    def apply(self):
        """Override to apply the transform to the document tree."""
        raise NotImplementedError('subclass must override this method')


class Transformer(TransformSpec):

    """
    Stores transforms (`Transform` classes) and applies them to document
    trees.  Also keeps track of components by component type name.
    """

    from docutils.transforms import universal

    default_transforms = (universal.Decorations,
                          universal.FinalChecks,
                          universal.Messages)
    """These transforms are applied to all document trees."""

    def __init__(self, document):
        self.transforms = []
        """List of transforms to apply.  Each item is a 3-tuple:
        ``(priority string, transform class, pending node or None)``."""

        self.document = document
        """The `nodes.document` object this Transformer is attached to."""

        self.applied = []
        """Transforms already applied, in order."""

        self.sorted = 0
        """Boolean: is `self.tranforms` sorted?"""

        self.components = {}
        """Mapping of component type name to component object.  Set by
        `self.populate_from_components()`."""

        self.serialno = 0
        """Internal serial number to keep track of the add order of
        transforms."""

    def add_transform(self, transform_class, priority=None):
        """
        Store a single transform.  Use `priority` to override the default.
        """
        if priority is None:
            priority = transform_class.default_priority
        priority_string = self.get_priority_string(priority)
        self.transforms.append((priority_string, transform_class, None))
        self.sorted = 0

    def add_transforms(self, transform_list):
        """Store multiple transforms, with default priorities."""
        for transform_class in transform_list:
            priority_string = self.get_priority_string(
                transform_class.default_priority)
            self.transforms.append((priority_string, transform_class, None))
        self.sorted = 0

    def add_pending(self, pending, priority=None):
        """Store a transform with an associated `pending` node."""
        transform_class = pending.transform
        if priority is None:
            priority = transform_class.default_priority
        priority_string = self.get_priority_string(priority)
        self.transforms.append((priority_string, transform_class, pending))
        self.sorted = 0

    def get_priority_string(self, priority):
        """
        Return a string, `priority` combined with `self.serialno`.

        This ensures FIFO order on transforms with identical priority.
        """
        self.serialno += 1
        return '%03d-%03d' % (priority, self.serialno)

    def populate_from_components(self, components):
        """
        Store each component's default transforms, with default priorities.
        Also, store components by type name in a mapping for later lookup.
        """
        self.add_transforms(self.default_transforms)
        for component in components:
            if component is None:
                continue
            self.add_transforms(component.default_transforms)
            self.components[component.component_type] = component
        self.sorted = 0

    def apply_transforms(self):
        """Apply all of the stored transforms, in priority order."""
        self.document.reporter.attach_observer(
            self.document.note_transform_message)
        while self.transforms:
            if not self.sorted:
                # Unsorted initially, and whenever a transform is added.
                self.transforms.sort()
                self.transforms.reverse()
                self.sorted = 1
            priority, transform_class, pending = self.transforms.pop()
            transform = transform_class(self.document, startnode=pending)
            transform.apply()
            self.applied.append((priority, transform_class, pending))
