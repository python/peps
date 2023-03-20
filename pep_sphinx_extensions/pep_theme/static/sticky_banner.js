"use strict";

// Inject a style element into the document head that adds scroll-margin-top to
// all elements with an id attribute. This is used to offset the scroll position
// when clicking on a link to an element with an id attribute. The offset is
// equal to the height of the sticky banner.
document.addEventListener("DOMContentLoaded", () => {
  const stickyBanners = document.getElementsByClassName("sticky-banner");
  if (!stickyBanners.length) {
    return;
  }

  const stickyBanner = stickyBanners[0];
  const node = document.createElement("style");
  node.id = "sticky-banner-style";
  document.head.appendChild(node);

  // Handle changes in banner height
  function adjustBannerMargin() {
    const text = document.createTextNode(
      ":target { scroll-margin-top: " + stickyBanner.offsetHeight + "px; }"
    );
    node.replaceChildren(text);
  }

  document.addEventListener("resize", adjustBannerMargin);

  // Handle on-load banner height and scrolling to anchor
  function adjustBannerMarginAndScroll() {
    adjustBannerMargin();
    if (location.hash.length > 1) {
      document.getElementById(location.hash.substring(1)).scrollIntoView();
    }
  }

  adjustBannerMarginAndScroll();
  document.addEventListener("load", adjustBannerMarginAndScroll);
});
