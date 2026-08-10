//console.log("app.js cargado");

let playlistSeleccionada = null;

const clubes = [
    "Seleccione un club",
    "Marista",
    "Los Tordos",
    "Banco Mendoza B",
    "Regatas-Andino",
    "Peumayen", 
    "Banco Mendoza",
    "Vistalba",
    "Murialdo",
    "Teque",
    "Aleman",
    "Universidad de Cuyo",
    "Liceo",
    "Universidad de San Juan",
    "San Juan Rugby",
    "Tacuru",
    "Marista de San Rafael"
];

const fechas = [ 
    "Seleccione una fecha",
    "Fecha 1",
    "Fecha 2",
    "Fecha 3",
    "Fecha 4",
    "Fecha 5",
    "Fecha 6",
    "Fecha 7",
    "Fecha 8",
    "Fecha 9",
    "Fecha 10",
    "Fecha 11",
    "Fecha 12",
    "Fecha 13",
    "Fecha 14",
    "Fecha 15"
];

function cargarFechas(){

    const select = document.getElementById("fecha-select");

    // Si no estamos en subir.html, salimos
    if (!select) {
        return;
    }

    select.innerHTML = "";

    fechas.forEach((fecha, index) => {

        const option = document.createElement("option");

        option.value = index === 0 ? "" : fecha;
        option.textContent = fecha;

        if (index === 0) {
            option.disabled = true;
            option.selected = true;
        }

        select.appendChild(option);

    });

}

cargarFechas();


function cargarClubes(){

    const local = document.getElementById("club-local");
    const visitante = document.getElementById("club-visitante");

    // Si no estamos en subir.html, salimos
    if (!local || !visitante) {
        return;
    }

    clubes.forEach((club, index) => {

        const opcionLocal = document.createElement("option");

        opcionLocal.value = index === 0 ? "" : club;
        opcionLocal.textContent = club;

        if (index === 0) {
            opcionLocal.disabled = true;
            opcionLocal.selected = true;
        }

        local.appendChild(opcionLocal);


        const opcionVisitante = document.createElement("option");

        opcionVisitante.value = index === 0 ? "" : club;
        opcionVisitante.textContent = club;

        if (index === 0) {
            opcionVisitante.disabled = true;
            opcionVisitante.selected = true;
        }

        visitante.appendChild(opcionVisitante);

    });

}

const clubLocal = document.getElementById("club-local");

if (clubLocal) {
    cargarClubes();
}
//cargarClubes();

async function cargarPlaylists(){

    const select = document.getElementById(
        "playlist-select"
    );

    // Si no estamos en subir.html, salimos
    if (!select) {
        return;
    }

    try {

        const response = await fetch("/playlists");

        const playlists = await response.json();


        select.innerHTML = "";

        // Opción por defecto
        const opcionInicial = document.createElement("option");

        opcionInicial.value = "";
        opcionInicial.textContent = "Seleccionar";
        opcionInicial.disabled = true;
        opcionInicial.selected = true;

        select.appendChild(opcionInicial);


        playlists.forEach(playlist => {

            const option = document.createElement("option");

            option.value = playlist.id;

            option.textContent = playlist.nombre;

            select.appendChild(option);

        });

        // Guardamos la primera playlist por defecto
        playlistSeleccionada = null;

    } catch(error){

        select.innerHTML =
            "<option>Error cargando playlists</option>";

        console.error(error);

    }

}


cargarPlaylists();

const playlistSelect =

    document.getElementById("playlist-select");

if (playlistSelect){ 
    playlistSelect.addEventListener(
        "change",
        () => {

            // Guardamos la playlist elegida
            playlistSeleccionada = playlistSelect.value;

            const uploadSection = document.getElementById("upload-section");
            if (uploadSection) {
                uploadSection.classList.remove("hidden");
            }

/*
            document
            .getElementById("upload-section")
            .classList
            .remove("hidden");

            console.log(
            "Playlist elegida:",
            playlistSeleccionada
            ); */

        }
    );
}
    



// Evento botón subir

// ===============================
// Evitar mismo club local/visitante
// ===============================

const clubLocalSelect = document.getElementById("club-local");
const clubVisitanteSelect = document.getElementById("club-visitante");
const nombreLocal = document.getElementById("nombre-local");
const nombreVisitante = document.getElementById("nombre-visitante");

if (clubLocalSelect && clubVisitanteSelect) {

    clubLocalSelect.addEventListener(
        "change",
        () => {

            const seleccionado = clubLocalSelect.value;

            Array.from(clubVisitanteSelect.options)
                .forEach(option => {

                    option.disabled = (
                        option.value === seleccionado
                    );

                });

            // Si ya estaba elegido el mismo club
            if (clubVisitanteSelect.value === seleccionado) {

                clubVisitanteSelect.value = "";

            }

        }
    );

}


// mostrar clubes en goles

if (
    clubLocalSelect &&
    clubVisitanteSelect &&
    nombreLocal &&
    nombreVisitante
) {


    clubLocalSelect.addEventListener(
        "change",
        () => {

            nombreLocal.textContent =
                clubLocalSelect.value || "Local";

        }
    );


    clubVisitanteSelect.addEventListener(
        "change",
        () => {

            nombreVisitante.textContent =
                clubVisitanteSelect.value || "Visitante";

        }
    );

}

// mostrar bonus si hay empate
const bonusSection = document.getElementById("bonus-section");
const bonusClub = document.getElementById("bonus-club");
const golesLocal = document.getElementById("goles-local");
const golesVisitante = document.getElementById("goles-visitante");

// Ocultar el bonus al cargar la página
if (bonusSection) {
    bonusSection.style.display = "none";
}

// Actualizar bonus cuando cambian goles o clubes
if (
    golesLocal &&
    golesVisitante &&
    clubLocalSelect &&
    clubVisitanteSelect
) {
    golesLocal.addEventListener("input",actualizarBonus);
    golesVisitante.addEventListener("input",actualizarBonus);
    clubLocalSelect.addEventListener("change",actualizarBonus);
    clubVisitanteSelect.addEventListener("change",actualizarBonus);

}

function actualizarBonus() {

    const gl = Number(golesLocal.value);
    const gv = Number(golesVisitante.value);

    if (!golesLocal.value || !golesVisitante.value) {
        //bonusSection.classList.add("hidden");
        bonusSection.style.display = "none";
        bonusClub.innerHTML = "";
        return;
    }


    //if (golesLocal.value === golesVisitante.value) {
    if (gl == gv){ 

        bonusSection.style.display = "block";

        //bonusClub.innerHTML = "";
        bonusClub.innerHTML = `
            <option value="">Seleccionar club</option>
        `;
/*
        const opcionInicial =
            document.createElement("option");

        opcionInicial.value = "";
        opcionInicial.textContent =
            "Seleccionar club";

        bonusClub.appendChild(opcionInicial);*/


        [clubLocalSelect.value, clubVisitanteSelect.value]
            .forEach(club => {

                const option =
                    document.createElement("option");

                option.value = club;
                option.textContent = club;

                bonusClub.appendChild(option);

            });

    } else {

        //bonusSection.classList.add("hidden");
        bonusSection.style.display = "none";
        bonusClub.innerHTML = "";

    }

}

// ===============================
// Botón subir video
// ===============================


const uploadButton = document.getElementById(
    "upload-button"
);


if (uploadButton) {

    uploadButton.addEventListener(
        "click",
        async () => {

            const file =
                document.getElementById("video-file").files[0];

            if (!file) {
                alert(
                    "Elegí un video"
                );
                return;
            }

            // Tamaño máximo: 3 GB
            const MAX_SIZE = 3 * 1024 * 1024 * 1024;

            if (file.size > MAX_SIZE) {
                alert(
                    "El video supera el tamaño máximo permitido (3 GB)."
                );
                return;
            }

            // Solo archivos .mp4
            if (!file.name.toLowerCase().endsWith(".mp4")) {
                alert(
                    "El video debe estar en formato .mp4."
                );
                return;
            }

            // se debe seleciconar una playlist
            if (!playlistSeleccionada) {
                alert("Seleccioná una fecha.");
                return;
            }

            const fecha = document.getElementById("fecha-select").value;

            if (!fecha) {
                alert("Seleccioná una fecha.");
                return;
            }

            const clubLocal =
                document.getElementById("club-local").value;

            const clubVisitante =
                document.getElementById("club-visitante").value;


            if (!clubLocal || !clubVisitante) {

                alert(
                    "Seleccioná los dos clubes antes de subir el video"
                );

                return;

            }  

            const resultadoLocal =
                document.getElementById("goles-local").value;


            const resultadoVisitante =
                document.getElementById("goles-visitante").value;

            if (resultadoLocal === "" || resultadoVisitante === "") {
                alert(
                    "Ingresá el resultado del partido"
                );
                return;
            }

            const bonusSeleccionado = document.getElementById("bonus-club")?.value || "";

            if (resultadoLocal === resultadoVisitante &&!bonusSeleccionado) {
                alert("Seleccioná el equipo que obtuvo el bonus.");
                return;
            }
            

            const title =`${clubLocal} vs ${clubVisitante}`;
            //const fecha = document.getElementById("fecha-select").value;
            const bonus = document.getElementById("bonus-club").value;
            let description; 

            if (bonus != ""){ // es decir hay algun club en bonus
                if (bonus == clubLocal){
                    description =`Torneo Clausura 2026, Resultado: ${clubLocal} ${resultadoLocal}* - ${clubVisitante} ${resultadoVisitante}.`;
                }
                else {
                    description = `Torneo Clausura 2026, Resultado: ${clubLocal} ${resultadoLocal} - ${resultadoVisitante}* ${clubVisitante} .`;
                }
            }
            else {
                description = `Torneo Clausura 2026, Resultado: ${clubLocal} ${resultadoLocal} - ${resultadoVisitante} ${clubVisitante}.`;
            }

            const headers = {

                "X-Title": title,

                "X-Fecha": fecha,

                "X-Description": description,

                "X-Playlist-ID": playlistSeleccionada

            };

            const status =
                document.getElementById("upload-status");

            const button =
                document.getElementById("upload-button");

            const warning = document.getElementById("upload-warning");
            if (warning){
                warning.classList.remove("hidden");
            }

            /*status.textContent =
                "Puede demorar unos minutos, no cierres la pagina";*/

            button.disabled = true;

            button.textContent =
                "Subiendo...";


            try {

                /*
                const filename = `${title.trim()}.mp4`;
                // 1) Pedir URL a Render
                const infoUpload = await fetch("/crear-upload", {

                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        filename: filename
                    })
                    

                });

                const datos = await infoUpload.json();

                // 2) Subir directo a R2
                const response = await subirVideoProgreso(
                    file,
                    datos.upload_url
                ); */

                const response = await subirVideoProgreso(file, headers);

/*
                const response = await fetch(
                    "/upload",
                    {
                        method: "POST",
                        headers: headers,
                        body: file
                    }
                );
*/
                //const data =
                  //  await response.json();

                const data = response.data;
                  
                if (response.ok) {

                    status.textContent =
                        "Video subido correctamente";

                   // console.log(data);

                } else {
                    status.textContent =
                       // "Error subiendo video";
                       data.detail || "Error subiendo el video";

                       alert(
                            data.detail || "Error subiendo video"
                       );

                    console.error(data);
                }

            } catch(error) {

                console.error(error);

                alert(
                    "Error"
                );

            } finally {

                button.disabled = false;

                button.textContent =
                    "Subir video";

                if (warning) {
                    warning.classList.add("hidden");
                }
            }

        }
    );

}
    

async function subirVideoProgreso(file, headers){ //,uploadUrl) {
    return new Promise((resolve, reject) => {

        const xhr = new XMLHttpRequest();

        xhr.open(
            "POST",
            "/upload"
        ); 

        // Mostrar progreso
        xhr.upload.addEventListener("progress", (event) => {

            if (event.lengthComputable) {

                const porcentaje =
                    Math.round(
                        (event.loaded / event.total) * 100
                    );

                const progressBar =
                    document.getElementById("progress-bar");

                const status =
                    document.getElementById("upload-status");

                if (progressBar) {
                    progressBar.style.width =
                        `${porcentaje}%`;
                }

                if (status) {
                    status.textContent =
                        `Subiendo video... ${porcentaje}%`;
                }

            }

        });

        xhr.addEventListener("load", () => {

            let data;

            try {
                data = JSON.parse(xhr.responseText);
            } catch {
                data = {};
            }

            resolve({
                ok: xhr.status >= 200 && xhr.status < 300,
                status: xhr.status,
                data: data
            });

        });

        xhr.addEventListener("error", () => {
            reject(new Error("Error de conexión"));
        });

        // Agregar headers
        Object.entries(headers).forEach(
            ([nombre, valor]) => {
                xhr.setRequestHeader(nombre, valor);
            }
        );

        xhr.send(file);

    });

        /*xhr.open(
            "PUT",
            uploadUrl
        );

        xhr.setRequestHeader(
            "Content-Type",
            file.type
        );*/


        // Agregar headers personalizados
        /*
        Object.entries(headers).forEach(([key, value]) => {

            xhr.setRequestHeader(
                key,
                value
            );

        });*/


        /*
        const progressContainer =
            document.getElementById("progress-container");


        const progressBar =
            document.getElementById("progress-bar");


        const status =
            document.getElementById("upload-status");


        progressContainer.classList.remove("hidden");


        xhr.upload.onprogress = (event) => {

            if (event.lengthComputable) {

                const porcentaje =
                    Math.round(
                        (event.loaded / event.total) * 100
                    );


                progressBar.style.width =
                    porcentaje + "%";


                status.textContent =
                    `Subiendo video... ${porcentaje}%`;

            }

        };


        xhr.onload = () => {

            resolve({

                ok:
                    xhr.status >= 200 &&
                    xhr.status < 300,

                json: async () => {

                    if (!xhr.responseText) {
                        return {};
                    }
                    return JSON.parse(xhr.responseText);
                }
                    

                    //JSON.parse(xhr.responseText)

            });

        };


        xhr.onerror = () => {

            reject(
                new Error("Error de conexión")
            );

        };


        xhr.send(file);

    }); */
}

async function descargarVideo(filename){

   // console.log("ARCHIVO A DESCARGAR:", filename);

    const response = await fetch(
        `/download/${encodeURIComponent(filename)}`
    );

    if (!response.ok) {
        alert("No se pudo generar la descarga");
        return;
    }

    const data = await response.json();

    window.location.href = data.url;

}

/*
const menuToggle = document.getElementById("menu-toggle");

const sidebar = document.querySelector(".sidebar");

if(menuToggle && sidebar){

    menuToggle.addEventListener("click", ()=>{

        sidebar.classList.toggle("open");

    });

}*/
const menuButton = document.getElementById("menu-toggle");
const sidebar = document.querySelector(".sidebar");
const overlay = document.getElementById("menu-overlay");

if(menuButton && sidebar){

    menuButton.addEventListener("click", ()=>{

        sidebar.classList.toggle("open");
        overlay.classList.toggle("show");

    });

    overlay.addEventListener("click", ()=>{

        sidebar.classList.remove("open");
        overlay.classList.remove("show");

    });

}


const videoFile = document.getElementById("video-file");
const fileName = document.getElementById("file-name");

if (videoFile && fileName) {
    videoFile.addEventListener("change", () => {

        if (videoFile.files.length > 0) {

            fileName.textContent = videoFile.files[0].name;

        } else {

            fileName.textContent = "Ningún archivo seleccionado";

        }

    });
}

