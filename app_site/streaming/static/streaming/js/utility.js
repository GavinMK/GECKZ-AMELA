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