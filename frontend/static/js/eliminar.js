// ===============================
// MODAL DE CONFIRMACIÓN (eliminar)
// ===============================

let videoAEliminar = null;
let playlistItemAEliminar = null;

function eliminarPartido(videoId, playlistItemId) {

    videoAEliminar = videoId;
    playlistItemAEliminar = playlistItemId;

    const overlay = document.getElementById("modal-overlay");
    if (overlay) {
        overlay.classList.remove("hidden");
    }

}

const modalCancelar = document.getElementById("modal-cancelar");
const modalConfirmar = document.getElementById("modal-confirmar");
const modalOverlay = document.getElementById("modal-overlay");

if (modalCancelar) {
    modalCancelar.addEventListener("click", () => {
        modalOverlay.classList.add("hidden");
        videoAEliminar = null;
        playlistItemAEliminar = null;
    });
}

if (modalOverlay) {
    // Cerrar si clickean fuera de la tarjeta
    modalOverlay.addEventListener("click", (event) => {
        if (event.target === modalOverlay) {
            modalOverlay.classList.add("hidden");
            videoAEliminar = null;
            playlistItemAEliminar = null;
        }
    });
}

if (modalConfirmar) {

    modalConfirmar.addEventListener("click", async () => {

        if (!videoAEliminar) return;

        modalConfirmar.disabled = true;
        modalConfirmar.textContent = "Eliminando...";

        try {

            const resp = await fetch(`/partidos/${videoAEliminar}/eliminar`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ playlist_item_id: playlistItemAEliminar })
            });

            const data = await resp.json();

            if (resp.ok) {
                window.location.reload();
            } else {
                alert(data.detail || "Error eliminando el video");
            }

        } catch (error) {
            console.error(error);
            alert("Error de conexión");
        } finally {
            modalConfirmar.disabled = false;
            modalConfirmar.textContent = "Eliminar";
            modalOverlay.classList.add("hidden");
        }

    });

}
/*
async function eliminarPartido(videoId) {

    const confirmar = confirm("¿Estás seguro de eliminar el video?");

    if (!confirmar) {
        return;
    }

    try {

        const resp = await fetch(
            `/partidos/${videoId}/eliminar`,{
            method: "POST" ,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ playlist_item_id: playlistItemId })
        });

        const data = await resp.json();

        if (resp.ok) {
            alert("Video eliminado correctamente");
            window.location.reload();
        } else {
            alert(data.detail || "Error eliminando el video");
        }

    } catch (error) {
        console.error(error);
        alert("Error de conexión");
    }

}*/