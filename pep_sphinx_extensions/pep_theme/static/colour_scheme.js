const dark = document.getElementById("css-dark");
const pygmentsNormal = document.getElementById("pyg");
const pygmentsDark = document.getElementById("pyg-dark");

const makeLight = () => {
    dark.media = pygmentsNormal.media = pygmentsDark.media = ""
    dark.disabled = pygmentsDark.disabled = true
    pygmentsNormal.disabled = false

}

const makeDark = () => {
    dark.media = pygmentsNormal.media = pygmentsDark.media = ""
    dark.disabled = pygmentsDark.disabled = false
    pygmentsNormal.disabled = true
}


const toggleColourScheme = () => {
    if (localStorage.getItem("colour_scheme") === "dark") {
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
