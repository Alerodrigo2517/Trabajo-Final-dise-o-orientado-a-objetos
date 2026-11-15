from getpass import getpass

from sqlalchemy import select

from src.core.database import get_session
from src.core.security import hash_password
from src.models.orm import UsuarioORM

nombre = input("Ingrese el nombre completo: ").strip()
usuario = input("Ingrese el nombre de usuario: ").strip()
contrasena = getpass("Ingrese la contraseña: ")

if not nombre or not usuario or not contrasena:
    raise SystemExit("Completa el nombre, el usuario y la contraseña.")

try:
    contrasena_hash = hash_password(contrasena)
except ValueError as error:
    raise SystemExit(str(error))

with get_session() as session:
    existe = session.scalar(
        select(UsuarioORM).where(UsuarioORM.usuario == usuario)
    )

    if existe:
        raise SystemExit("Ese nombre de usuario ya está registrado.")

    nuevo_usuario = UsuarioORM(
        nombre=nombre,
        usuario=usuario,
        contrasena_hash=contrasena_hash,
    )
    session.add(nuevo_usuario)

print("Usuario creado correctamente.")
