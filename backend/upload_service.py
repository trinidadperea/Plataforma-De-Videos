from fastapi import HTTPException

import httpx
import config
import youtube
import gc


# Obtengo los datos para ponerle el nombre en yotube
def obtener_datos_upload(request):
    title = request.headers.get(
        "X-Title",
        "Video hockey"
    )

    fecha = request.headers.get(
        "X-Fecha",
        ""
    )

    playlist_id = request.headers.get(
        "X-Playlist-ID"
    )

    description = request.headers.get(
        "X-Description",
        ""
    )

    if not playlist_id:
        raise HTTPException(
            status_code=400,
            detail="No se recibió playlist"
        )

    content_length = int(
        request.headers["Content-Length"]
    )

    content_type = request.headers.get(
        "Content-Type",
        "video/mp4"
    )


    if fecha:
        title = f"{title} - {fecha}"

    return (
        title,
        playlist_id,
        description,
        content_length,
        content_type
    )

# -----------------------------
# INICIAR SUBIDA A YOUTUBE
# -----------------------------
async def iniciar_upload_youtube(
    title,
    description,
    content_length,
    content_type
):

    return await youtube.initiate_upload(
        title=title,
        description=description,
        content_length=content_length,
        content_type=content_type
    )


# -----------------------------
# SUBIR CHUNKS
# -----------------------------
async def subir_chunks_a_youtube(
    request,
    upload_url,
    content_length,
    content_type,
    client
):

    buffer = bytearray()

    youtube_offset = 0

    video_result = None


    async for chunk in request.stream():

        buffer.extend(chunk)


        while len(buffer) >= config.PART_SIZE:

            data = bytes(
                buffer[:config.PART_SIZE]
            )

            del buffer[:config.PART_SIZE]

            # para limpiar garbage
            gc.collect()

            respuesta = await youtube.upload_chunk(
                upload_url=upload_url,
                chunk=data,
                start=youtube_offset,
                content_length=content_length,
                content_type=content_type,
                client=client
            )


            if respuesta:

                if respuesta.get("status") == 200:

                    video_result = respuesta["data"]


                elif respuesta.get("range"):

                    ultimo_byte = int(
                        respuesta["range"].split("-")[1]
                    )

                    youtube_offset = ultimo_byte + 1


    return (
        buffer,
        youtube_offset,
        video_result
    )


# -----------------------------
# SUBIR ÚLTIMO CHUNK
# -----------------------------

async def subir_ultimo_chunk(
    buffer,
    upload_url,
    youtube_offset,
    content_length,
    content_type,
    client
):

    if not buffer:
        return None


    data = bytes(buffer)


    respuesta = await youtube.upload_chunk(
        upload_url=upload_url,
        chunk=data,
        start=youtube_offset,
        content_length=content_length,
        content_type=content_type,
        client=client
    )


    if respuesta:

        if respuesta.get("status") == 200:

            return respuesta["data"]


    return None

# -----------------------------
# AGREGAR VIDEO A PLAYLIST
# -----------------------------

async def agregar_a_playlist(
    video_id,
    playlist_id
):

    await youtube.add_to_playlist(
        video_id,
        playlist_id
    )



# -----------------------------
# Funcion principal subida
# -----------------------------
async def upload_video(
    request,
    title,
    playlist_id,
    description,
    content_length,
    content_type

):

    # -----------------------------
    # Iniciar subida a YouTube
    # -----------------------------

    upload_url = await iniciar_upload_youtube(
        title=title,
        description=description,
        content_length=content_length,
        content_type=content_type
    )

    video_result = None
    youtube_offset = 0

    # -----------------------------
    # Cliente HTTP
    # -----------------------------

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(
            600.0,
            connect=60.0
        )
    ) as client:

        # -----------------------------
        # Subir chunks a YouTube
        # -----------------------------
        (
            buffer,
            youtube_offset,
            video_result
        ) = await subir_chunks_a_youtube(
            request=request,
            upload_url=upload_url,
            content_length=content_length,
            content_type=content_type,
            client=client
        )

        # -----------------------------
        # Subir ultimo chunk a YouTube
        # -----------------------------

        ultimo_resultado = await subir_ultimo_chunk(
            buffer=buffer,
            upload_url=upload_url,
            youtube_offset=youtube_offset,
            content_length=content_length,
            content_type=content_type,
            client=client
        )

        if ultimo_resultado:
            video_result = ultimo_resultado

    # -----------------------------
    # Verificar resultado
    # -----------------------------

    if not video_result:

        raise HTTPException(
            status_code=500,
            detail="YouTube no devolvió el ID del video"
        )

    video_id = video_result["id"]

    # -----------------------------
    # Agregar a playlist
    # -----------------------------

    await youtube.add_to_playlist(
        video_id,
        playlist_id
    )

    # -----------------------------
    #  resultado
    # ----------------------------- 

    return {
        "ok": True,
        "video_url": f"https://youtu.be/{video_id}"
    }

'''
# funcion upload que funciona para r2 y para youtube
@app.post("/upload")
async def upload(
    request: Request
):

    title = request.headers.get(
        "X-Title",
        "Video hockey"
    )

    playlist_id = request.headers.get(
        "X-Playlist-ID"
    )

    if not playlist_id:
        raise HTTPException(
            status_code=400,
            detail="No se recibió playlist"
        )


    content_length = int(
        request.headers["Content-Length"]
    )

    content_type = request.headers.get(
        "Content-Type",
        "video/mp4"
    )


    description = request.headers.get(
        "X-Description",
        ""
    )


    # ===============================
    # INICIAR YOUTUBE
    # ===============================

    upload_url = await youtube.initiate_upload(
        title=title,
        description=description,
        content_length=content_length,
        content_type=content_type
    )


    # ===============================
    # INICIAR R2
    # ===============================

    filename = f"{title}.mp4"
    #print("GUARDANDO EN R2:", repr(filename))


    upload_id = r2.initiate_upload(
        filename
    )


    # ===============================
    # VARIABLES DE CONTROL
    # ===============================

    part_number = 1
    youtube_offset = 0

    partes_r2 = []

    video_result = None


    # YouTube necesita mínimo 256 KB
    # Usamos 32 MB para que también sirva para R2
    #BUFFER_SIZE = 8 * 1024 * 1024
    PART_SIZE = 32 * 1024 * 1024

    buffer = bytearray()



    # Un único cliente HTTP
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(
            600.0,
            connect=60.0
        )
       # timeout=None
    ) as client:


        # Leer archivo una sola vez
        async for chunk in request.stream():


            buffer.extend(chunk)



            # Cuando juntamos 8 MB
            #if len(buffer) >= BUFFER_SIZE:
            while len(buffer) >= PART_SIZE:

                data = bytes(buffer[:PART_SIZE])
                del buffer[:PART_SIZE]
                #data = bytes(buffer)



                # ===============================
                # SUBIR A YOUTUBE
                # ===============================

                #respuesta = await youtube.upload_chunk(

                respuesta, etag = await asyncio.gather( 
                    youtube.upload_chunk(
                        upload_url=upload_url,
                        chunk=data,
                        start=youtube_offset,
                        content_length=content_length,
                        content_type=content_type,
                        client=client
                    ),

                    asyncio.to_thread(
                        r2.upload_part,
                        filename,
                        upload_id,
                        part_number,
                        data
                    )
                )
            
                #if respuesta:
                #    video_result = respuesta



                # ===============================
                # SUBIR A R2
                # ===============================

                #etag = await asyncio.to_thread(
                #    r2.upload_part,
                #    filename,
                #    upload_id,
                #    part_number,
                #    data
                #)

                # ===============================
                # PROCESAR RESPUESTA YOUTUBE
                # ===============================

                if respuesta:

                    if respuesta.get("status") == 200:
                        video_result = respuesta["data"]

                    elif respuesta.get("range"):

                        ultimo_byte = int(
                            respuesta["range"].split("-")[1]
                        )
                        youtube_offset = ultimo_byte + 1

                # ===============================
                # GUARDAR PARTE R2
                # ===============================

                partes_r2.append(
                    {
                        "ETag": etag,
                        "PartNumber": part_number
                    }
                )

                #offset += len(data)
                part_number += 1


                #buffer.clear()



        # ===============================
        # ÚLTIMO BLOQUE
        # ===============================

        if buffer:


            data = bytes(buffer)



            # ---- YouTube ----

            respuesta = await youtube.upload_chunk(
                upload_url=upload_url,
                chunk=data,
                start=youtube_offset,
                content_length=content_length,
                content_type=content_type,
                client=client
            )


            if respuesta:
                #video_result = respuesta
                if respuesta.get("status") == 200:
                    video_result = respuesta["data"]



            # ---- R2 ----

            etag = await asyncio.to_thread(
                r2.upload_part,
                filename,
                upload_id,
                part_number,
                data
            )


            partes_r2.append(
                {
                    "ETag": etag,
                    "PartNumber": part_number
                }
            )



    # ===============================
    # FINALIZAR R2
    # ===============================

    await asyncio.to_thread(
        r2.complete_upload,
        filename,
        upload_id,
        partes_r2
    )



    if not video_result:

        raise HTTPException(
            status_code=500,
            detail="YouTube no devolvió el ID del video"
        )

    video_id = video_result["id"]

    # ===============================
    # AGREGAR A PLAYLIST
    # ===============================

    await youtube.add_to_playlist(
        video_id,
        playlist_id
    )



    return {
        "ok": True,
        "video_url":
            f"https://youtu.be/{video_id}",
        "r2_file":
            filename
    }
'''