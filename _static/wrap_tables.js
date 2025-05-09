// Wrap the tables in PEP bodies in a div, to allow for responsive scrolling

"use strict";

const pepContentId = "pep-content";


// Wrap passed table element in wrapper divs
function wrapTable (table) {
    const wrapper = document.createElement("div");
    wrapper.classList.add("table-wrapper");
    table.parentNode.insertBefore(wrapper, table);
    wrapper.appendChild(table);
}


// Wrap all tables in the PEP content in wrapper divs
function wrapPepContentTables () {
    const pepContent = document.getElementById(pepContentId);
    const bodyTables = pepContent.getElementsByTagName("table");
    Array.from(bodyTables).forEach(wrapTable);
}


// Wrap the tables as soon as the DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById(pepContentId)) {
        wrapPepContentTables();
    }
})
