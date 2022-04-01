const dark = document.getElementById("css-dark");
const pygmentsNormal = document.getElementById("pyg");
const pygmentsDark = document.getElementById("pyg-dark");

const makeLight = () => {
    dark.disabled = pygmentsDark.disabled = true
    dark.media = pygmentsNormal.media = pygmentsDark.media = ""
    pygmentsNormal.disabled = false

}

const makeDark = () => {
    dark.disabled = pygmentsDark.disabled = false
    dark.media = pygmentsNormal.media = pygmentsDark.media = ""
    pygmentsNormal.disabled = true
}


const toggleColourScheme = () => {
    const colourScheme = localStorage.getItem("colour_scheme")
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches

    if ((colourScheme === "dark") || (!colourScheme && prefersDark)) {
        makeLight()
        localStorage.setItem("colour_scheme", "light")
    } else {
        makeDark()
        localStorage.setItem("colour_scheme", "dark")
    }
}

/* set colour scheme from local storage */
document.addEventListener("DOMContentLoaded", () => {
    if (localStorage.getItem("colour_scheme") === "light") makeLight()
    if (localStorage.getItem("colour_scheme") === "dark") makeDark()
})
