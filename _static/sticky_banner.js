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

  function adjustBannerMargin() {
    const text = document.createTextNode(
      `:target { scroll-margin-top: ${stickyBanner.offsetHeight}px; }`,
    );
    node.replaceChildren(text);
  }

  for (const closeButton of document.getElementsByClassName("close-button")) {
    closeButton.addEventListener("click", () => {
      // search the button's ancestors for a ``sticky-banner`` element.
      const stickyBanner = closeButton.closest(".sticky-banner");
      if (stickyBanner) stickyBanner.remove();
    });
  }

  adjustBannerMargin();
  document.addEventListener("resize", adjustBannerMargin);
  document.addEventListener("load", adjustBannerMargin);
});
