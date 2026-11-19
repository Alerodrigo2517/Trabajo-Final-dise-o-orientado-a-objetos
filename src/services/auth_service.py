"""Reglas de autenticación y administración de roles."""
from src.core.authorization import ROLE_CODES
from src.core.database import get_session
from src.core.security import hash_password, verify_password
from src.models.entities import Usuario
from src.repositories.user_repository import UsuarioRepository

class AuthService:
    def login(self, usuario: str, password: str) -> tuple[Usuario | None, str | None]:
        nombre_usuario = usuario.strip()
        if not nombre_usuario or not password:
            return None, "Completa el usuario y la contraseña."
        with get_session() as session:
            repo = UsuarioRepository(session)
            found = repo.buscar_por_usuario(nombre_usuario)
            if found is None or not verify_password(password, found.contrasena_hash):
                return None, "Las credenciales no son válidas."
            return found, None

    def list_users(self) -> list[dict]:
        with get_session() as session:
            return UsuarioRepository(session).listar_usuarios()

    def create_account(self, nombre: str, usuario: str, password: str,
                       role: str = "OPERADOR") -> Usuario:
        clean_name, clean_username = nombre.strip(), usuario.strip()
        clean_role = role.strip().upper()
        if not clean_name or len(clean_name) > 45:
            raise ValueError("El nombre es obligatorio y admite hasta 45 caracteres.")
        if not clean_username or len(clean_username) > 45:
            raise ValueError("El usuario es obligatorio y admite hasta 45 caracteres.")
        if clean_role not in ROLE_CODES:
            raise ValueError("El rol seleccionado no es válido.")
        password_hash = hash_password(password)
        with get_session() as session:
            repo = UsuarioRepository(session)
            if repo.buscar_por_usuario(clean_username) is not None:
                raise ValueError("Ese nombre de usuario ya está registrado.")
            return repo.crear(Usuario(
                nombre=clean_name, usuario=clean_username,
                contrasena_hash=password_hash, rol=clean_role,
            ))

    def update_role(self, user_id: int, role: str, *, actor_user_id: int) -> None:
        clean_role = role.strip().upper()
        if clean_role not in ROLE_CODES:
            raise ValueError("El rol seleccionado no es válido.")
        if user_id == actor_user_id and clean_role != "ADMINISTRADOR":
            raise ValueError("No podés quitarte el rol de administrador desde tu propia sesión.")
        with get_session() as session:
            repo = UsuarioRepository(session)
            target = repo.buscar_por_id(user_id)
            if target is None:
                raise ValueError("No se encontró la cuenta seleccionada.")
            if target.rol == "ADMINISTRADOR" and clean_role != "ADMINISTRADOR":
                if repo.contar_administradores() <= 1:
                    raise ValueError("Debe quedar al menos un administrador en el sistema.")
            target.rol = clean_role
