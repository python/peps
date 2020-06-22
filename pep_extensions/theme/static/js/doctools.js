/*
 * doctools.js
 * ~~~~~~~~~~~
 *
 * Sphinx JavaScript utilities for all documentation.
 *
 * :copyright: Copyright 2007-2020 by the Sphinx team, see AUTHORS.
 * :license: BSD, see LICENSE for details.
 *
 */

/**
 * Footnote fixer
 */
document.querySelectorAll("span.brackets").forEach(el => {
    if (!el.children.length) {
        el.innerText = "[" + el.innerText + "]"
    }
})

/**
 * select a different prefix for underscore
 */

const ready = (callback) => {
  if (document.readyState !== "loading") callback();
  else document.addEventListener("DOMContentLoaded", callback);
}

const removeElements = (elms) => {for (let el of elms) { el.remove() }}

/**
 * highlight a given string on a node by wrapping it in
 * span elements with the given class name.
 */
const highlightText = function(text, className, curNode) {
  function highlight(node, addItems) {
    if (node.nodeType === 3) {  // Text node
      const val = node.nodeValue;
      const parent = node.parentNode
      const pos = val.toLowerCase().indexOf(text);
      if (pos >= 0
          && !parent.classList.contains(className)
          && !parent.classList.contains("nohighlight")
      ) {
        let span;
        const closestNode = node.parentNode.closest("body, svg, foreignObject");
        const isInSVG = closestNode && closestNode.matches("svg")
        if (isInSVG) {
          span = document.createElementNS("http://www.w3.org/2000/svg", "tspan");
        } else {
          span = document.createElement("span");
          span.classList.add(className);
        }

        span.appendChild(document.createTextNode(val.substr(pos, text.length)));
        parent.insertBefore(span, parent.insertBefore(
          document.createTextNode(val.substr(pos + text.length)),
          node.nextSibling));
        node.nodeValue = val.substr(0, pos);
        if (isInSVG) {
          const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
          const bbox = parent.getBBox();
          rect.x.baseVal.value = bbox.x;
          rect.y.baseVal.value = bbox.y;
          rect.width.baseVal.value = bbox.width;
          rect.height.baseVal.value = bbox.height;
          rect.setAttribute('class', className);
          addItems.push({
              "parent": node.parentNode,
              "target": rect});
        }
      }
    }
    else if (node.matches("button, select, textarea")) {
      node.childNodes.forEach(el => highlight(el, addItems));
    }
    else if (node.nodeType === 1)
    {
      node.childNodes.forEach(el => highlight(el, addItems));
    }
  }
  let addItems = [];
  // const content = document.querySelector('[role="main"]');
  highlight(curNode, addItems)
  for (let i = 0; i < addItems.length; ++i) {
    addItems[i].parent.insertAdjacentHTML("beforebegin", addItems[i].target)
  }
  return curNode;
};

/**
 * Small JavaScript module for the documentation.
 */
const Documentation = {
  init : function() {
    this.highlightSearchWords();
  },

  gettext : string => string,

  /**
   * highlight the search words provided in the urle in the text
   */
  highlightSearchWords : function() {
    const urlParams = new URLSearchParams(window.location.search);
    const terms = urlParams.get("highlight") ? urlParams.get("highlight").split(/\s+/) : [];
    if (terms.length) {
      window.setTimeout(() => {
        terms.forEach(term => highlightText(term.toLowerCase(), 'highlighted', document.querySelector("body")))
      }, 10);
      let hideMatches = document.createElement("p")
      let hideMatchesLink = document.createElement("a")
      hideMatches.classList.add("highlight-link")
      hideMatchesLink.href = "javascript:Documentation.hideSearchWords()"
      hideMatchesLink.innerText = _('Hide Search Matches')
      hideMatchesLink.style.fontStyle = "italic"
      hideMatches.appendChild(hideMatchesLink)
      document.getElementById("searchbox").appendChild(hideMatches)
    }
  },

  /**
   * helper function to hide the search marks again
   */
  hideSearchWords : function() {
    removeElements(document.querySelectorAll("#searchbox .highlight-link"))
    document.querySelectorAll("span.highlighted").forEach(el => el.classList.remove("highlighted"))
  },
};

// quick alias for translations
_ = Documentation.gettext;

ready(() => {
  Documentation.init();
});