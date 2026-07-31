const loginButton =
    document.getElementById("login-button");


loginButton.addEventListener(
    "click",
    async () => {
        const username =
            document.getElementById("username").value;


        const password =
            document.getElementById("password").value;

        const response =
            await fetch(
                "/login",
                {
                    method:"POST",

                    headers:{
                        "Content-Type":"application/json"
                    },

                    body:JSON.stringify({
                        username,
                        password
                    })
                }
            );

        const data =
            await response.json();

        if(response.ok){
            window.location.href="/subir";
        }
        else{

            document
            .getElementById("login-error")
            .textContent =
                "Usuario o contraseña incorrectos";

        }


    }
);