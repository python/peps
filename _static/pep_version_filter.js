/**
 * Python version filter for PEP Index page
 * Filters PEP tables by Python version using the JSON API
 */
(function () {
  "use strict";

  const STORAGE_KEY = "pep_version_filter";
  const API_URL =
    document.currentScript?.dataset.apiUrl || "/api/peps.json";
  let pepVersionMap = {};
  let allVersions = [];

  /**
   * Parse python_version string and extract individual versions
   * Handles formats like "3.10", "2.4, 2.5, 2.6", "2.7, 3.0"
   */
  function parseVersions(versionStr) {
    if (!versionStr) return [];
    return versionStr
      .split(",")
      .map((v) => v.trim())
      .filter((v) => v);
  }

  /**
   * Extract major.minor version from a version string
   * "3.10.1" -> "3.10", "3.10" -> "3.10"
   */
  function getMajorMinor(version) {
    const match = version.match(/^(\d+\.\d+)/);
    return match ? match[1] : version;
  }

  /**
   * Sort versions in descending order (newest first)
   * Handles both 2.x and 3.x versions
   */
  function sortVersionsDescending(versions) {
    return versions.sort((a, b) => {
      const [aMajor, aMinor] = a.split(".").map(Number);
      const [bMajor, bMinor] = b.split(".").map(Number);
      if (bMajor !== aMajor) return bMajor - aMajor;
      return bMinor - aMinor;
    });
  }

  /**
   * Fetch PEP data and build version map
   */
  async function loadPepData() {
    try {
      const response = await fetch(API_URL);
      if (!response.ok) throw new Error("Failed to fetch PEP data");
      const data = await response.json();

      const versionSet = new Set();

      for (const [pepNum, pep] of Object.entries(data)) {
        const versions = parseVersions(pep.python_version);
        pepVersionMap[pepNum] = versions;

        // Collect unique major.minor versions
        for (const v of versions) {
          const majorMinor = getMajorMinor(v);
          if (/^\d+\.\d+$/.test(majorMinor)) {
            versionSet.add(majorMinor);
          }
        }
      }

      allVersions = sortVersionsDescending([...versionSet]);
      return true;
    } catch (error) {
      console.error("Error loading PEP data:", error);
      return false;
    }
  }

  /**
   * Extract PEP number from a table row
   */
  function getPepNumberFromRow(row) {
    const link = row.querySelector('a[href*="pep-"]');
    if (!link) return null;
    const match = link.getAttribute("href").match(/pep-0*(\d+)/);
    return match ? match[1] : null;
  }

  /**
   * Check if a PEP matches the selected version filter
   */
  function pepMatchesVersion(pepNum, selectedVersion) {
    if (!selectedVersion || selectedVersion === "all") return true;
    const pepVersions = pepVersionMap[pepNum] || [];
    return pepVersions.some((v) => getMajorMinor(v) === selectedVersion);
  }

  /**
   * Apply the filter to all PEP tables
   */
  function applyFilter(selectedVersion) {
    const tables = document.querySelectorAll("table.pep-zero-table");
    let totalVisible = 0;
    let totalPeps = 0;

    tables.forEach((table) => {
      const rows = table.querySelectorAll("tbody tr");
      let visibleInTable = 0;

      rows.forEach((row) => {
        const pepNum = getPepNumberFromRow(row);
        if (pepNum === null) return;

        totalPeps++;
        const matches = pepMatchesVersion(pepNum, selectedVersion);

        if (matches) {
          row.style.display = "";
          visibleInTable++;
          totalVisible++;
        } else {
          row.style.display = "none";
        }
      });

      // Find the section container (h2 + table) and hide if empty
      const section = table.closest("section") || table.parentElement;
      const h2 = section?.querySelector("h2");
      if (h2 && visibleInTable === 0 && selectedVersion !== "all") {
        section.style.display = "none";
      } else if (section) {
        section.style.display = "";
      }
    });

    updateCount(totalVisible, totalPeps, selectedVersion);
  }

  /**
   * Update the count display
   */
  function updateCount(visible, total, selectedVersion) {
    const countEl = document.getElementById("pep-filter-count");
    if (!countEl) return;

    if (!selectedVersion || selectedVersion === "all") {
      countEl.textContent = "";
    } else {
      countEl.textContent = `Showing ${visible} of ${total} PEPs`;
    }
  }

  /**
   * Create the filter UI
   */
  function createFilterUI() {
    const container = document.createElement("div");
    container.id = "pep-version-filter";
    container.innerHTML = `
            <label for="pep-version-select">Filter by Python version:</label>
            <select id="pep-version-select">
                <option value="all">All versions</option>
            </select>
            <span id="pep-filter-count" aria-live="polite"></span>
        `;

    const select = container.querySelector("#pep-version-select");

    // Add version options
    for (const version of allVersions) {
      const option = document.createElement("option");
      option.value = version;
      option.textContent = version;
      select.appendChild(option);
    }

    // Restore saved selection
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && (saved === "all" || allVersions.includes(saved))) {
      select.value = saved;
    }

    // Handle filter changes
    select.addEventListener("change", () => {
      const value = select.value;
      localStorage.setItem(STORAGE_KEY, value);
      applyFilter(value);
    });

    return container;
  }

  /**
   * Insert the filter UI into the page
   */
  function insertFilterUI(filterUI) {
    // Find the "Index by Category" section and insert after its heading
    const indexByCategory = document.getElementById("index-by-category");
    if (indexByCategory) {
      const heading = indexByCategory.querySelector("h2");
      if (heading) {
        heading.after(filterUI);
        return true;
      }
    }

    return false;
  }

  /**
   * Initialize the filter
   */
  async function init() {
    // Only run on PEP 0 (index page)
    const isPepIndex =
      document.querySelector("section#introduction") &&
      document.querySelector("table.pep-zero-table");
    if (!isPepIndex) return;

    const loaded = await loadPepData();
    if (!loaded || allVersions.length === 0) return;

    const filterUI = createFilterUI();
    const inserted = insertFilterUI(filterUI);

    if (inserted) {
      // Apply initial filter
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved && saved !== "all") {
        applyFilter(saved);
      }
    }
  }

  // Run when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
