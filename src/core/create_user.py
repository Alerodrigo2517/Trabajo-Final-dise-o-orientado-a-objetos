"""Alta interactiva de usuarios mediante AuthService y UsuarioRepository."""

from getpass import getpass

from src.services.auth_service import AuthService


nombre = input("Ingrese el nombre completo: ").strip()
usuario = input("Ingrese el nombre de usuario: ").strip()
contrasena = getpass("Ingrese la contraseña: ")

if not nombre or not usuario or not contrasena:
    raise SystemExit("Completa el nombre, el usuario y la contraseña.")

try:
    creado = AuthService().crear_cuenta(nombre, usuario, contrasena)
except ValueError as error:
    raise SystemExit(str(error)) from error

print(f"Usuario {creado.usuario} creado correctamente con rol {creado.rol}.")
