function togglePassword() {
    let password = document.getElementById("password");
    let new_password = document.getElementById("new_password");
    if (password.type === "password") {
        password.type = "text";
        new_password.type = "text";
    }
    else {
        password.type = "password";
        new_password.type = "password";
    }
}

function submitOnce(b1, b2) {
    document.getElementById(b1).hidden = true;
    document.getElementById(b2).hidden = false;
}