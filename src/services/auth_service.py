"""Reglas de autenticación y administración de roles."""
from src.core.authorization import CODIGOS_ROL
from src.core.database import obtener_sesion_bd
from src.core.security import generar_hash_contrasena, verificar_contrasena
from src.models.entities import Usuario
from src.repositories.user_repository import UsuarioRepository

class AuthService:
    def autenticar_usuario(self, usuario: str, contrasena: str) -> tuple[Usuario | None, str | None]:
        nombre_usuario = usuario.strip()
        if not nombre_usuario or not contrasena:
            return None, "Completa el usuario y la contraseña."
        with obtener_sesion_bd() as sesion:
            repositorio = UsuarioRepository(sesion)
            encontrado = repositorio.buscar_por_usuario(nombre_usuario)
            if encontrado is None or not verificar_contrasena(contrasena, encontrado.contrasena_hash):
                return None, "Las credenciales no son válidas."
            return encontrado, None

    def listar_usuarios(self) -> list[dict]:
        with obtener_sesion_bd() as sesion:
            return UsuarioRepository(sesion).listar_usuarios()

    def crear_cuenta(self, nombre: str, usuario: str, contrasena: str,
                       rol: str = "OPERADOR") -> Usuario:
        nombre_limpio, usuario_limpio = nombre.strip(), usuario.strip()
        rol_limpio = rol.strip().upper()
        if not nombre_limpio or len(nombre_limpio) > 45:
            raise ValueError("El nombre es obligatorio y admite hasta 45 caracteres.")
        if not usuario_limpio or len(usuario_limpio) > 45:
            raise ValueError("El usuario es obligatorio y admite hasta 45 caracteres.")
        if rol_limpio not in CODIGOS_ROL:
            raise ValueError("El rol seleccionado no es válido.")
        hash_contrasena = generar_hash_contrasena(contrasena)
        with obtener_sesion_bd() as sesion:
            repositorio = UsuarioRepository(sesion)
            if repositorio.buscar_por_usuario(usuario_limpio) is not None:
                raise ValueError("Ese nombre de usuario ya está registrado.")
            return repositorio.crear(Usuario(
                nombre=nombre_limpio, usuario=usuario_limpio,
                contrasena_hash=hash_contrasena, rol=rol_limpio,
            ))

    def actualizar_rol(self, id_usuario: int, rol: str, *, id_usuario_actor: int) -> None:
        rol_limpio = rol.strip().upper()
        if rol_limpio not in CODIGOS_ROL:
            raise ValueError("El rol seleccionado no es válido.")
        if id_usuario == id_usuario_actor and rol_limpio != "ADMINISTRADOR":
            raise ValueError("No podés quitarte el rol de administrador desde tu propia sesión.")
        with obtener_sesion_bd() as sesion:
            repositorio = UsuarioRepository(sesion)
            objetivo = repositorio.buscar_por_id(id_usuario)
            if objetivo is None:
                raise ValueError("No se encontró la cuenta seleccionada.")
            if objetivo.rol == "ADMINISTRADOR" and rol_limpio != "ADMINISTRADOR":
                if repositorio.contar_administradores() <= 1:
                    raise ValueError("Debe quedar al menos un administrador en el sistema.")
            objetivo.rol = rol_limpio
