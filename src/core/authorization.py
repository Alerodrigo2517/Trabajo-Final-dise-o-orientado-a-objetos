"""Roles de aplicación guardados en la columna usuarios.rol de MySQL."""
ADMIN = "ADMINISTRADOR"
OPERATOR = "OPERADOR"
AUDITOR = "AUDITOR"
ROLE_CODES = (ADMIN, OPERATOR, AUDITOR)
ROLE_LABELS = {ADMIN: "Administrador", OPERATOR: "Operador", AUDITOR: "Auditor · solo lectura"}

def normalize_role(role: str | None) -> str:
    value = (role or "").strip().upper()
    return value if value in ROLE_CODES else AUDITOR

def can_write(user: dict | None) -> bool:
    return bool(user) and normalize_role(user.get("role")) in (ADMIN, OPERATOR)

def is_admin(user: dict | None) -> bool:
    return bool(user) and normalize_role(user.get("role")) == ADMIN
