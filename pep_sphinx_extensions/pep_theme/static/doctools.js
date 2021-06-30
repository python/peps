/* JavaScript utilities for all documentation. */

// Footnote fixer
document.querySelectorAll("span.brackets").forEach(el => el.innerHTML = "[" + el.innerHTML + "]")
document.querySelectorAll("a.brackets").forEach(el => el.innerHTML = "[" + el.innerHTML + "]")
