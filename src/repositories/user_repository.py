"""Consultas de autenticación y roles sobre la tabla usuarios existente."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from src.models.entities import Usuario
from src.models.orm import UsuarioORM

class UsuarioRepository:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def buscar_por_usuario(self, usuario: str) -> Usuario | None:
        registro = self.sesion.scalar(select(UsuarioORM).where(UsuarioORM.usuario == usuario))
        if registro is None:
            return None
        return Usuario(
            id_usuario=registro.id_usuario, nombre=registro.nombre,
            usuario=registro.usuario, contrasena_hash=registro.contrasena_hash,
            rol=registro.rol,
        )

    def buscar_por_id(self, id_usuario: int) -> UsuarioORM | None:
        return self.sesion.get(UsuarioORM, id_usuario)

    def contar_administradores(self) -> int:
        return int(self.sesion.scalar(
            select(func.count()).select_from(UsuarioORM).where(
                UsuarioORM.rol == "ADMINISTRADOR"
            )
        ) or 0)

    def listar_usuarios(self) -> list[dict]:
        registros = self.sesion.scalars(select(UsuarioORM).order_by(UsuarioORM.usuario)).all()
        return [
            {"id_usuario": fila.id_usuario, "nombre": fila.nombre,
             "usuario": fila.usuario, "rol": fila.rol}
            for fila in registros
        ]

    def crear(self, usuario: Usuario) -> Usuario:
        registro = UsuarioORM(
            nombre=usuario.nombre, usuario=usuario.usuario,
            contrasena_hash=usuario.contrasena_hash, rol=usuario.rol,
        )
        self.sesion.add(registro)
        self.sesion.flush()
        return Usuario(
            id_usuario=registro.id_usuario, nombre=registro.nombre,
            usuario=registro.usuario, contrasena_hash=registro.contrasena_hash,
            rol=registro.rol,
        )
