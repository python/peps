const pygmentsLight = document.getElementById("pyg-light")
const pygmentsDark = document.getElementById("pyg-dark")

const prefersDark = window.matchMedia("(prefers-color-scheme: dark)")

const getColourScheme = () => document.documentElement.dataset.colour_scheme
const setColourScheme = (colourScheme = getColourScheme()) => {
    document.documentElement.dataset.colour_scheme = colourScheme
    setPygments(colourScheme)
    setTooltip(nextColourScheme(colourScheme))
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
    pygmentsDark.disabled = colourScheme === "light"
    pygmentsLight.disabled = colourScheme === "dark"
    pygmentsDark.media = colourScheme === "auto" ? "(prefers-color-scheme: dark)" : ""
    pygmentsLight.media = colourScheme === "auto" ? "(prefers-color-scheme: light)" : ""
}

const setTooltip = (schemeOnClick = nextColourScheme()) => {
    const label = schemeOnClick === "auto" ? "Adapt to system theme" : `Switch to ${schemeOnClick} mode`
    const button = document.getElementById("colour-scheme-cycler")
    button.setAttribute( "aria-label", label)
    button.setAttribute( "title", label)
}

// (Re)set tooltip and pygments state (page theme is set inline in page.html)
document.addEventListener("DOMContentLoaded", () => setColourScheme())
prefersDark.addEventListener("change", () => setColourScheme())
