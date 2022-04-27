const prefersDark = window.matchMedia("(prefers-color-scheme: dark)")

const getColourScheme = () => document.documentElement.dataset.colour_scheme
const setColourScheme = (colourScheme = getColourScheme()) => {
    document.documentElement.dataset.colour_scheme = colourScheme
    setPygments(colourScheme)
    setTooltip(colourScheme)
    localStorage.setItem("colour_scheme", colourScheme)
}

// Map system theme to a cycle of steps
const cycles = {
    dark: ["auto", "light", "dark"], // auto (dark) → light → dark
    light: ["auto", "dark", "light"], // auto (light) → dark → light
}

const nextColourScheme = (colourScheme = getColourScheme()) => {
    const cycle = cycles[prefersDark.matches ? "dark" : "light"]
    return cycle[(cycle.indexOf(colourScheme) + 1) % cycle.length]
}

const setPygments = (colourScheme = getColourScheme()) => {
    const pygmentsDark = document.getElementById("pyg-dark")
    const pygmentsLight = document.getElementById("pyg-light")
    pygmentsDark.disabled = colourScheme === "light"
    pygmentsLight.disabled = colourScheme === "dark"
    pygmentsDark.media = colourScheme === "auto" ? "(prefers-color-scheme: dark)" : ""
    pygmentsLight.media = colourScheme === "auto" ? "(prefers-color-scheme: light)" : ""
}

const setTooltip = (colourScheme = getColourScheme()) => {
    const schemeOnClick = nextColourScheme(colourScheme)
    const currentLabel = colourScheme === "auto" ? 'Following system colour scheme' : `Selected ${colourScheme} mode`
    const actionLabel = schemeOnClick === "auto" ? "adapt to system colour scheme" : `switch to ${schemeOnClick} mode`
    const label = `${currentLabel}.\nClick to ${actionLabel}.`

    const button = document.getElementById("colour-scheme-cycler")
    button.setAttribute("aria-label", label)
    button.setAttribute("title", label)
}

// Update tooltip and Pygments state (see page.html; the page theme is initialised inline)
document.addEventListener("DOMContentLoaded", () => setColourScheme())
prefersDark.addEventListener("change", () => setColourScheme())
