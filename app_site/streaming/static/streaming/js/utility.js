function togglePassword() {
    let password = document.getElementById("password");
    let new_password1 = document.getElementById("new_password1");
    let new_password2 = document.getElementById("new_password2");
    if (password.type === "password") {
        password.type = "text";
        new_password1.type = "text";
        new_password2.type = "text";
    }
    else {
        password.type = "password";
        new_password1.type = "password";
        new_password2.type = "password";
    }
}

function submitOnce(b1, b2) {
    document.getElementById(b1).hidden = true;
    document.getElementById(b2).hidden = false;
}