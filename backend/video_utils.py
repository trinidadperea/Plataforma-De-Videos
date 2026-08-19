import re


def parsear_titulo(titulo: str):
    """
    'Marista vs Los Tordos - Fecha 3' -> ('Marista', 'Los Tordos', 'Fecha 3')
    """
    if " - " in titulo:
        resto, fecha = titulo.rsplit(" - ", 1)
    else:
        resto, fecha = titulo, ""

    if " vs " in resto:
        club_local, club_visitante = resto.split(" vs ", 1)
    else:
        club_local, club_visitante = resto, ""

    return club_local.strip(), club_visitante.strip(), fecha.strip()


def parsear_resultado(description: str):
    """
    'Torneo Clausura 2026, Resultado: Marista 2* - 1 Los Tordos.'
    -> ('2', '1', 'local')   # bonus: 'local', 'visitante' o ''
    """
    match = re.search(
        r"Resultado:\s*.+?\s(\d+)(\*?)\s*-\s*(\d+)(\*?)\s+.+?\.",
        description
    )

    if not match:
        return "", "", ""

    gol_local, bonus_local, gol_visitante, bonus_visitante = match.groups()

    bonus = ""
    if bonus_local:
        bonus = "local"
    elif bonus_visitante:
        bonus = "visitante"

    return gol_local, gol_visitante, bonus


def armar_titulo(club_local: str, club_visitante: str, fecha: str) -> str:
    return f"{club_local} vs {club_visitante} - {fecha}"


def armar_descripcion(
    club_local: str,
    club_visitante: str,
    gol_local: str,
    gol_visitante: str,
    bonus: str  # 'local', 'visitante' o ''
) -> str:

    if bonus == "local":
        return f"Torneo Clausura 2026, Resultado: {club_local} {gol_local}* - {gol_visitante} {club_visitante}."
    elif bonus == "visitante":
        return f"Torneo Clausura 2026, Resultado: {club_local} {gol_local} - {gol_visitante}* {club_visitante}."
    else:
        return f"Torneo Clausura 2026, Resultado: {club_local} {gol_local} - {gol_visitante} {club_visitante}."