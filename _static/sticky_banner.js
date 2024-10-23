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
      ":target { scroll-margin-top: " + stickyBanner.offsetHeight + "px; }"
    );
    node.replaceChildren(text);
  }

  const closeButton = document.querySelector('.close-button');
  if (closeButton) {
    closeButton.addEventListener('click', () => {
      const stickyBanner = document.querySelector('.sticky-banner');
      if (stickyBanner) {
        stickyBanner.style.display = 'none';
      }
    });
  }

  adjustBannerMargin();
  document.addEventListener("resize", adjustBannerMargin);
  document.addEventListener("load", adjustBannerMargin);
});
