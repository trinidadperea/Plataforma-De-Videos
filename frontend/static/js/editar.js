// ===============================
// PRECARGAR DATOS EN EDITAR
// ===============================
if (window.datosEdicion) {

    const d = window.datosEdicion;

    // Esperamos a que cargarFechas() y cargarClubes() ya hayan corrido
    // (se ejecutan solas al cargar app.js)

    const fechaSelect = document.getElementById("fecha-select");
    const localSelect = document.getElementById("club-local");
    const visitanteSelect = document.getElementById("club-visitante");
    const golLocal = document.getElementById("goles-local");
    const golVisitante = document.getElementById("goles-visitante");

    if (fechaSelect) fechaSelect.value = d.fecha;
    if (localSelect) localSelect.value = d.clubLocal;
    if (visitanteSelect) visitanteSelect.value = d.clubVisitante;
    if (golLocal) golLocal.value = d.golLocal;
    if (golVisitante) golVisitante.value = d.golVisitante;

    // Disparamos los eventos "change"/"input" para que se actualicen
    // los nombres en el resultado y aparezca el bonus si corresponde
    if (localSelect) localSelect.dispatchEvent(new Event("change"));
    if (visitanteSelect) visitanteSelect.dispatchEvent(new Event("change"));
    if (golLocal) golLocal.dispatchEvent(new Event("input"));
    if (golVisitante) golVisitante.dispatchEvent(new Event("input"));

    // El bonus se precarga después, porque bonus-club recién
    // se llena cuando hay empate (ver actualizarBonus)
    const bonusClub = document.getElementById("bonus-club");
    if (bonusClub && d.bonus) {
        const clubConBonus =
            d.bonus === "local" ? d.clubLocal : d.clubVisitante;

        setTimeout(() => {
            bonusClub.value = clubConBonus;
        }, 0);
    }
}

// ===============================
// BOTÓN GUARDAR CAMBIOS
// ===============================
const guardarButton = document.getElementById("guardar-button");

if (guardarButton) {

    guardarButton.addEventListener("click", async () => {

        const fecha = document.getElementById("fecha-select").value;
        const clubLocal = document.getElementById("club-local").value;
        const clubVisitante = document.getElementById("club-visitante").value;
        const golLocal = document.getElementById("goles-local").value;
        const golVisitante = document.getElementById("goles-visitante").value;
        const bonusClub = document.getElementById("bonus-club")?.value || "";

        if (!fecha || !clubLocal || !clubVisitante) {
            alert("Completá fecha y clubes.");
            return;
        }

        if (golLocal === "" || golVisitante === "") {
            alert("Ingresá el resultado.");
            return;
        }

        if (golLocal === golVisitante && !bonusClub) {
            alert("Seleccioná el equipo que obtuvo el bonus.");
            return;
        }

        let bonus = "";
        if (bonusClub === clubLocal) bonus = "local";
        else if (bonusClub === clubVisitante) bonus = "visitante";

        const status = document.getElementById("editar-status");

        guardarButton.disabled = true;
        guardarButton.textContent = "Guardando...";

        try {
            const resp = await fetch(
                `/partidos/${window.datosEdicion.videoId}/editar`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        club_local: clubLocal,
                        club_visitante: clubVisitante,
                        fecha: fecha,
                        gol_local: golLocal,
                        gol_visitante: golVisitante,
                        bonus: bonus
                    })
                }
            );

            const data = await resp.json();

            if (resp.ok) {
                status.textContent = "Cambios guardados correctamente";
                setTimeout(() => { window.location.href = "/partidos"; }, 1200);
            } else {
                alert(data.detail || "Error guardando los cambios");
            }

        } catch (error) {
            console.error(error);
            alert("Error de conexión");
        } finally {
            guardarButton.disabled = false;
            guardarButton.textContent = "Guardar cambios";
        }

    });

}