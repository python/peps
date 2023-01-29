"use strict";

// Inject a style element into the document head that adds scroll-margin-top to
// all elements with an id attribute. This is used to offset the scroll position
// when clicking on a link to an element with an id attribute. The offset is
// equal to the height of the sticky banner.
document.addEventListener("DOMContentLoaded", () => {
    let stickyBanners = document.getElementsByClassName("sticky-banner");
    if (!stickyBanners) {
        return;
    }
    let stickyBanner = stickyBanners[0];
    let node = document.createElement("style");
    let text = document.createTextNode(":target { scroll-margin-top: " + stickyBanner.offsetHeight + "px; }")
    node.appendChild(text);
    document.head.appendChild(node);
});
