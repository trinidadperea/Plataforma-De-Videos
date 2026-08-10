"""
Backend FastAPI: login simple 
+ subida de videos a YouTube en streaming.
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routes import router

app = FastAPI()


# ===============================
# ARCHIVOS ESTÁTICOS
# ===============================

app.mount(
    "/static",
    StaticFiles(directory="../frontend/static"),
    name="static"
)


# ===============================
# CORS
# ===============================

# Permite que el frontend (servido desde otro origen) llame a esta API.
# En producción, reemplazá "*" por el dominio real de tu frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===============================
# RUTAS
# ===============================

app.include_router(router)




'''
SECRET_KEY = os.environ["APP_SECRET_KEY"]
serializer = URLSafeTimedSerializer(SECRET_KEY)

# Usuarios permitidos: los definís vos como variable de entorno,
# formato "usuario1:clave1,usuario2:clave2"
USERS = dict(
    pair.split(":", 1) for pair in os.environ["APP_USERS"].split(",")
)

COOKIE_NAME = "session"
MAX_AGE_SECONDS = 60 * 60 * 24 * 30  # 30 días




def create_session_cookie(username: str) -> str:
    return serializer.dumps({"username": username})


def get_current_user(request: Request) -> str:
    token = request.cookies.get(COOKIE_NAME)

    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")
    try:
        data = serializer.loads(token, max_age=MAX_AGE_SECONDS)
    except BadSignature:
        raise HTTPException(status_code=401, detail="Sesión inválida")
    return data["username"]


# funcion para que cuando entre a subir sin login
# lo redireccione a login y no de error
def require_user_or_login(request: Request):

    token = request.cookies.get(COOKIE_NAME)

    if not token:
        return RedirectResponse(
            "/login",
            status_code=302
        )

    try:

        data = serializer.loads(
            token,
            max_age=MAX_AGE_SECONDS
        )

        return data["username"]

    except BadSignature:

        return RedirectResponse(
            "/login",
            status_code=302
        )

def get_optional_user(request: Request):

    token = request.cookies.get(COOKIE_NAME)
    # No hay usuario logueado
    if not token:
        return None

    try:
        data = serializer.loads(
            token,
            max_age=MAX_AGE_SECONDS
        )

        return data["username"]

    except BadSignature:

        return None

@app.get("/test-r2")
async def test_r2():

    r2.list_files()

    return {
        "ok": True
    }


NO LO USO, SOLO SUBO A YOUTUBE
@app.get("/download/{filename:path}")
async def download(filename: str):
    #print("descargando key: ",repr(filename))
    url = r2.generate_download_url(
        filename
    )

    return {
        "url": url
    }




@app.post("/crear-upload")
async def crear_upload(request: Request):

    data = await request.json()

    filename = data["filename"]

    url = r2.create_upload_url(filename)

    return {
        "upload_url": url,
        "filename": filename
    }  


@app.get("/me")
async def me(username: str = Depends(get_current_user)):
    return {"username": username}


# endponit para listar las playlists
@app.get("/playlists")
async def playlists():

    return await youtube.get_playlists()

@app.get("/playlists/{playlist_id}/videos")
async def playlist_videos(playlist_id: str):

    return await youtube.get_playlist_videos(
        playlist_id
    )



# R2

@app.get("/test-r2")
async def test():

    return r2.listar_bucket()

'''