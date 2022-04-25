const pygmentsLight = document.getElementById("pyg-light")
const pygmentsDark = document.getElementById("pyg-dark")

const makeLight = () => {
    document.documentElement.dataset.colour_scheme = "light"
    pygmentsDark.disabled = true
    pygmentsLight.media = pygmentsDark.media = ""
    pygmentsLight.disabled = false
    localStorage.setItem("colour_scheme", "light")
}

const makeDark = () => {
    document.documentElement.dataset.colour_scheme = "dark"
    pygmentsDark.disabled = false
    pygmentsLight.media = pygmentsDark.media = ""
    pygmentsLight.disabled = true
    localStorage.setItem("colour_scheme", "dark")
}

const makeAuto = () => {
    document.documentElement.dataset.colour_scheme = "auto"
    pygmentsLight.media = "(prefers-color-scheme: light)"
    pygmentsDark.media = "(prefers-color-scheme: dark)"
    pygmentsLight.disabled = false
    pygmentsDark.disabled = false
    localStorage.setItem("colour_scheme", "auto")
}

const cycleColourScheme = () => {
    const colourScheme = document.documentElement.dataset.colour_scheme
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches

    if (prefersDark) { // auto (dark) → light → dark
        if (colourScheme === "auto") {
            makeLight()
            setNextButton("dark")
        } else if (colourScheme === "light") {
            makeDark()
            setNextButton("auto")
        } else {
            makeAuto()
            setNextButton("light")
        }
    } else { // auto (light) → dark → light
        if (colourScheme === "auto") {
            makeDark()
            setNextButton("light")
        } else if (colourScheme === "dark") {
            makeLight()
            setNextButton("auto")
        } else {
            makeAuto()
            setNextButton("dark")
        }
    }
}

const setNextButton = (nextTheme) => {
    const label = nextTheme === "auto" ? 'Adapt to system theme' : `Switch to ${nextTheme} mode`
    const button = document.getElementById("colour-scheme-cycler")
    button.setAttribute( "aria-label", label)
    button.setAttribute( "title", label)
}

/* set colour scheme from local storage */
document.addEventListener("DOMContentLoaded", () => {
    if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
        setNextButton("light")
    } else {
        setNextButton("dark")
    }
})
