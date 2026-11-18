"""Consultas y persistencia sobre clientes y contactos existentes."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from src.models.orm import ClienteORM, ClientesContactoORM


class ClientRepository:
    @staticmethod
    def list_clients(session: Session) -> list[ClienteORM]:
        statement = (
            select(ClienteORM)
            .options(selectinload(ClienteORM.contactos).joinedload(ClientesContactoORM.ciudad))
            .order_by(ClienteORM.apellido, ClienteORM.nombre)
        )
        return list(session.scalars(statement).unique())

    @staticmethod
    def get_by_cuit(session: Session, cuit: str) -> ClienteORM | None:
        for client in session.scalars(select(ClienteORM)):
            if "".join(character for character in client.cuit_cliente if character.isdigit()) == cuit:
                return client
        return None

    @staticmethod
    def create_client(session: Session, *, cuit: str, nombre: str, apellido: str) -> ClienteORM:
        client = ClienteORM(cuit_cliente=cuit, nombre=nombre, apellido=apellido)
        session.add(client)
        session.flush()
        return client

    @staticmethod
    def contacts_for_client(session: Session, cuit: str) -> list[ClientesContactoORM]:
        statement = (
            select(ClientesContactoORM)
            .where(ClientesContactoORM.fk_cliente == cuit)
            .options(joinedload(ClientesContactoORM.ciudad))
            .order_by(ClientesContactoORM.fecha_desde.desc(), ClientesContactoORM.id_contacto.desc())
        )
        return list(session.scalars(statement).unique())

