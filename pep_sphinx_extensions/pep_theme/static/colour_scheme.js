const sheet = document.getElementById("css-dark");

const toggleColourScheme = () => {
    sheet.media = ""
    if (localStorage.getItem("colour_scheme") === "dark") {
        sheet.disabled = true
        localStorage.setItem("colour_scheme", "light")
    } else {
        sheet.disabled = false
        localStorage.setItem("colour_scheme", "dark")
    }
}

/* set colour scheme from local storage */
document.addEventListener("DOMContentLoaded", () => {
    if (localStorage.getItem("colour_scheme") === "light") {
        sheet.media = ""
        sheet.disabled = true
    } else if (localStorage.getItem("colour_scheme") === "dark") {
        sheet.media = ""
        sheet.disabled = false
    }
})
