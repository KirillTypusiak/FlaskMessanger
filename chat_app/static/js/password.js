const buttons = document.querySelectorAll(".password_toggle")

buttons.forEach(button => {
    let parent = button.parentElement;
    let text_field = parent.querySelector("input")
    let icon = button.querySelector("img")
    button.addEventListener("click", () => {
        if(text_field.type === "password") {
            text_field.type = "text"
            icon.src = "/static/images/eye_off.svg";
            button.setAttribute("aria-label", "Приховати пароль");
        }

        else if(text_field.type === "text") {
            text_field.type = "password"
            icon.src = "/static/images/eye.svg";
            button.setAttribute("aria-label", "Показати пароль");
        }
    })
});