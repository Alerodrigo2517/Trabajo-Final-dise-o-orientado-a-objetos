from src.core.database import get_session
from src.core.security import verify_password
from src.models.entities import Usuario
from src.repositories.user_repository import UsuarioRepository


class AuthService:
    def login(self, usuario: str, password: str) -> tuple[Usuario | None, str | None]:
        nombre_usuario = usuario.strip()

        if not nombre_usuario or not password:
            return None, "Completa el usuario y la contraseña."

        with get_session() as session:
            repo = UsuarioRepository(session)
            usuario_encontrado = repo.buscar_por_usuario(nombre_usuario)

            if usuario_encontrado is None:
                return None, "Las credenciales no son válidas."

            if not verify_password(password, usuario_encontrado.contrasena_hash):
                return None, "Las credenciales no son válidas."

            return usuario_encontrado, None
"""  ----"""