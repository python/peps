// Handle setting and changing the site's color scheme (light/dark)

"use strict";

const prefersDark = window.matchMedia("(prefers-color-scheme: dark)")

const getColourScheme = () => document.documentElement.dataset.colour_scheme
const setColourScheme = (colourScheme = getColourScheme()) => {
    document.documentElement.dataset.colour_scheme = colourScheme
    localStorage.setItem("colour_scheme", colourScheme)
    setPygments(colourScheme)
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

// Update Pygments state (the page theme is initialised inline, see page.html)
document.addEventListener("DOMContentLoaded", () => setColourScheme())
