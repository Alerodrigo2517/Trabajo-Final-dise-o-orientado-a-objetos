"""Roles de aplicación guardados en la columna usuarios.rol de MySQL."""
ADMINISTRADOR = "ADMINISTRADOR"
OPERADOR = "OPERADOR"
AUDITOR = "AUDITOR"
CODIGOS_ROL = (ADMINISTRADOR, OPERADOR, AUDITOR)
ETIQUETAS_ROL = {ADMINISTRADOR: "Administrador", OPERADOR: "Operador", AUDITOR: "Auditor · solo lectura"}

def normalize_role(rol: str | None) -> str:
    valor = (rol or "").strip().upper()
    return valor if valor in CODIGOS_ROL else AUDITOR

def can_write(usuario: dict | None) -> bool:
    return bool(usuario) and normalize_role(usuario.get("role")) in (ADMINISTRADOR, OPERADOR)

def is_admin(usuario: dict | None) -> bool:
    return bool(usuario) and normalize_role(usuario.get("role")) == ADMINISTRADOR
