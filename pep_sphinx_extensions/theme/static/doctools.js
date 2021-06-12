/* Sphinx JavaScript utilities for all documentation.
 * Adapted from https://github.com/sphinx-doc/sphinx/blob/master/sphinx/themes/basic/static/doctools.js
 * Removed libraries (jQuery/underscores) & stripped down
 */

// Footnote fixer
document.querySelectorAll("span.brackets").forEach(el => {
    if (!el.children.length) el.innerText = "[" + el.innerText + "]"
})
