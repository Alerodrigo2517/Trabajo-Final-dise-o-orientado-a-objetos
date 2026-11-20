"""Roles de aplicación guardados en la columna usuarios.rol de MySQL."""
ADMINISTRADOR = "ADMINISTRADOR"
OPERADOR = "OPERADOR"
AUDITOR = "AUDITOR"
CODIGOS_ROL = (ADMINISTRADOR, OPERADOR, AUDITOR)
ETIQUETAS_ROL = {ADMINISTRADOR: "Administrador", OPERADOR: "Operador", AUDITOR: "Auditor · solo lectura"}

def normalizar_rol(rol: str | None) -> str:
    valor = (rol or "").strip().upper()
    return valor if valor in CODIGOS_ROL else AUDITOR

def puede_escribir(usuario: dict | None) -> bool:
    return bool(usuario) and normalizar_rol(usuario.get("role")) in (ADMINISTRADOR, OPERADOR)

def es_administrador(usuario: dict | None) -> bool:
    return bool(usuario) and normalizar_rol(usuario.get("role")) == ADMINISTRADOR
