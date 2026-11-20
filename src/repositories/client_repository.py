"""Consultas y persistencia sobre clientes y contactos existentes."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from src.models.orm import ClienteORM, ClientesContactoORM


class ClientRepository:
    @staticmethod
    def list_clients(sesion: Session) -> list[ClienteORM]:
        sentencia = (
            select(ClienteORM)
            .options(selectinload(ClienteORM.contactos).joinedload(ClientesContactoORM.ciudad))
            .order_by(ClienteORM.apellido, ClienteORM.nombre)
        )
        return list(sesion.scalars(sentencia).unique())

    @staticmethod
    def get_by_cuit(sesion: Session, cuit: str) -> ClienteORM | None:
        for cliente in sesion.scalars(select(ClienteORM)):
            if "".join(caracter for caracter in cliente.cuit_cliente if caracter.isdigit()) == cuit:
                return cliente
        return None

    @staticmethod
    def create_client(sesion: Session, *, cuit: str, nombre: str, apellido: str) -> ClienteORM:
        cliente = ClienteORM(cuit_cliente=cuit, nombre=nombre, apellido=apellido)
        sesion.add(cliente)
        sesion.flush()
        return cliente

    @staticmethod
    def contacts_for_client(sesion: Session, cuit: str) -> list[ClientesContactoORM]:
        sentencia = (
            select(ClientesContactoORM)
            .where(ClientesContactoORM.fk_cliente == cuit)
            .options(joinedload(ClientesContactoORM.ciudad))
            .order_by(ClientesContactoORM.fecha_desde.desc(), ClientesContactoORM.id_contacto.desc())
        )
        return list(sesion.scalars(sentencia).unique())

