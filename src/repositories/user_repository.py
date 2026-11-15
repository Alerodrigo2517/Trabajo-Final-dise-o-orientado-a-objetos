from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.entities import Usuario
from src.models.orm import UsuarioORM


class UsuarioRepository:
    def __init__(self, session: Session):
        self.session = session

    def buscar_por_usuario(self, usuario: str) -> Usuario | None:
        consulta = select(UsuarioORM).where(UsuarioORM.usuario == usuario)
        registro = self.session.scalar(consulta)

        if registro is None:
            return None

        return Usuario(
            id_usuario=registro.id_usuario,
            nombre=registro.nombre,
            usuario=registro.usuario,
            contrasena_hash=registro.contrasena_hash,
        )

    def crear(self, usuario: Usuario) -> Usuario:
        registro = UsuarioORM(
            nombre=usuario.nombre,
            usuario=usuario.usuario,
            contrasena_hash=usuario.contrasena_hash,
        )
        self.session.add(registro)
        self.session.flush()

        return Usuario(
            id_usuario=registro.id_usuario,
            nombre=registro.nombre,
            usuario=registro.usuario,
            contrasena_hash=registro.contrasena_hash,
        )
"""  ----"""