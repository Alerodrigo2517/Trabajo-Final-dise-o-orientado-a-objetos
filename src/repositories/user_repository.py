"""Consultas de autenticación y roles sobre la tabla usuarios existente."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from src.models.entities import Usuario
from src.models.orm import UsuarioORM

class UsuarioRepository:
    def __init__(self, session: Session):
        self.session = session

    def buscar_por_usuario(self, usuario: str) -> Usuario | None:
        registro = self.session.scalar(select(UsuarioORM).where(UsuarioORM.usuario == usuario))
        if registro is None:
            return None
        return Usuario(
            id_usuario=registro.id_usuario, nombre=registro.nombre,
            usuario=registro.usuario, contrasena_hash=registro.contrasena_hash,
            rol=registro.rol,
        )

    def buscar_por_id(self, id_usuario: int) -> UsuarioORM | None:
        return self.session.get(UsuarioORM, id_usuario)

    def contar_administradores(self) -> int:
        return int(self.session.scalar(
            select(func.count()).select_from(UsuarioORM).where(
                UsuarioORM.rol == "ADMINISTRADOR"
            )
        ) or 0)

    def listar_usuarios(self) -> list[dict]:
        registros = self.session.scalars(select(UsuarioORM).order_by(UsuarioORM.usuario)).all()
        return [
            {"id_usuario": row.id_usuario, "nombre": row.nombre,
             "usuario": row.usuario, "rol": row.rol}
            for row in registros
        ]

    def crear(self, usuario: Usuario) -> Usuario:
        registro = UsuarioORM(
            nombre=usuario.nombre, usuario=usuario.usuario,
            contrasena_hash=usuario.contrasena_hash, rol=usuario.rol,
        )
        self.session.add(registro)
        self.session.flush()
        return Usuario(
            id_usuario=registro.id_usuario, nombre=registro.nombre,
            usuario=registro.usuario, contrasena_hash=registro.contrasena_hash,
            rol=registro.rol,
        )
