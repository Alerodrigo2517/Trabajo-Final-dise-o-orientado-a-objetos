"""Reglas de negocio para clientes y sus datos de contacto."""

import re

from sqlalchemy.exc import IntegrityError

from src.core.database import get_session
from src.core.validators import clean_text, display_cuit, normalize_cuit
from src.repositories.client_repository import ClientRepository


def list_clients() -> list[dict]:
    with get_session() as session:
        clients = ClientRepository.list_clients(session)
        return [
            {
                "cuit_cliente": client.cuit_cliente,
                "cuit_display": display_cuit(client.cuit_cliente) if len(re.sub(r"\D", "", client.cuit_cliente)) == 11 else client.cuit_cliente,
                "nombre": client.nombre,
                "apellido": client.apellido,
                "nombre_completo": f"{client.nombre} {client.apellido}",
                "contactos": [
                    {
                        "id_contacto": contact.id_contacto,
                        "direccion": contact.direccion,
                        "ciudad": contact.ciudad.nombre_ciudad,
                        "telefono": contact.telefono,
                        "fecha_desde": contact.fecha_desde,
                        "fecha_hasta": contact.fecha_hasta,
                    }
                    for contact in client.contactos
                ],
            }
            for client in clients
        ]


def create_client(cuit: str, nombre: str, apellido: str) -> dict:
    normalized_cuit = normalize_cuit(cuit)
    cleaned_name = clean_text(nombre, "el nombre", 45)
    cleaned_surname = clean_text(apellido, "el apellido", 45)

    try:
        with get_session() as session:
            existing = ClientRepository.list_clients(session)
            if any(re.sub(r"\D", "", client.cuit_cliente) == normalized_cuit for client in existing):
                raise ValueError("Ya existe un cliente con ese CUIT.")
            client = ClientRepository.create_client(
                session,
                cuit=normalized_cuit,
                nombre=cleaned_name,
                apellido=cleaned_surname,
            )
            return {
                "cuit_cliente": client.cuit_cliente,
                "cuit_display": display_cuit(client.cuit_cliente),
                "nombre": client.nombre,
                "apellido": client.apellido,
                "nombre_completo": f"{client.nombre} {client.apellido}",
            }
    except IntegrityError as exc:
        raise ValueError("Ya existe un cliente con ese CUIT.") from exc


def list_client_contacts(cuit: str) -> list[dict]:
    legacy_cuit = (cuit or "").strip()
    try:
        normalized_cuit = normalize_cuit(cuit)
    except ValueError:
        normalized_cuit = legacy_cuit
    with get_session() as session:
        client = ClientRepository.get_by_cuit(session, legacy_cuit)
        if client is None and normalized_cuit != legacy_cuit:
            client = ClientRepository.get_by_cuit(session, normalized_cuit)
        if client is None:
            return []
        contacts = ClientRepository.contacts_for_client(session, client.cuit_cliente)
        return [
            {
                "id_contacto": contact.id_contacto,
                "direccion": contact.direccion,
                "ciudad": contact.ciudad.nombre_ciudad,
                "telefono": contact.telefono,
                "fecha_desde": contact.fecha_desde,
                "fecha_hasta": contact.fecha_hasta,
            }
            for contact in contacts
        ]

