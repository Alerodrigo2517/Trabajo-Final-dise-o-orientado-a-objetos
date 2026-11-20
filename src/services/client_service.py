"""Reglas de negocio para clientes y sus datos de contacto."""

from datetime import date
import re

from sqlalchemy.exc import IntegrityError

from src.core.database import get_session
from src.core.validators import clean_text, display_cuit, normalize_cuit
from src.repositories.budget_repository import BudgetRepository
from src.repositories.client_repository import ClientRepository


def list_clients() -> list[dict]:
    with get_session() as sesion:
        clientes = ClientRepository.list_clients(sesion)
        return [
            {
                "cuit_cliente": cliente.cuit_cliente,
                "cuit_display": display_cuit(cliente.cuit_cliente),
                "nombre": cliente.nombre,
                "apellido": cliente.apellido,
                "nombre_completo": f"{cliente.nombre} {cliente.apellido}",
                "contactos": [
                    {
                        "id_contacto": contacto.id_contacto,
                        "direccion": contacto.direccion,
                        "ciudad": contacto.ciudad.nombre_ciudad,
                        "telefono": contacto.telefono,
                        "fecha_desde": contacto.fecha_desde,
                        "fecha_hasta": contacto.fecha_hasta,
                    }
                    for contacto in cliente.contactos
                ],
            }
            for cliente in clientes
        ]


def create_client(
    cuit: str,
    nombre: str,
    apellido: str,
    direccion: str = "",
    ciudad: str = "",
    telefono: str = "",
) -> dict:
    cuit_normalizado = normalize_cuit(cuit)
    nombre_limpio = clean_text(nombre, "el nombre", 45)
    apellido_limpio = clean_text(apellido, "el apellido", 45)

    tiene_datos_contacto = any((direccion or "").strip() or (ciudad or "").strip() or (telefono or "").strip() for _ in [0])
    direccion_limpia = ""
    ciudad_limpia = ""
    telefono_limpio = ""
    if tiene_datos_contacto:
        direccion_limpia = clean_text(direccion, "la dirección del cliente", 100)
        ciudad_limpia = clean_text(ciudad, "la ciudad del cliente", 100)
        telefono_limpio = clean_text(telefono, "el teléfono del cliente", 20)

    try:
        with get_session() as sesion:
            existentes = ClientRepository.list_clients(sesion)
            if any(re.sub(r"\D", "", cliente.cuit_cliente) == cuit_normalizado for cliente in existentes):
                raise ValueError("Ya existe un cliente con ese CUIT.")
            cliente = ClientRepository.create_client(
                sesion,
                cuit=cuit_normalizado,
                nombre=nombre_limpio,
                apellido=apellido_limpio,
            )
            if tiene_datos_contacto:
                ciudad_orm = BudgetRepository.get_or_create_city(sesion, ciudad_limpia)
                BudgetRepository.create_client_contact(
                    sesion,
                    cuit_cliente=cliente.cuit_cliente,
                    direccion=direccion_limpia,
                    ciudad=ciudad_orm,
                    telefono=telefono_limpio,
                    fecha_inicio=date.today(),
                )
            return {
                "cuit_cliente": cliente.cuit_cliente,
                "cuit_display": display_cuit(cliente.cuit_cliente),
                "nombre": cliente.nombre,
                "apellido": cliente.apellido,
                "nombre_completo": f"{cliente.nombre} {cliente.apellido}",
            }
    except IntegrityError as exc:
        raise ValueError("Ya existe un cliente con ese CUIT.") from exc


def list_client_contacts(cuit: str) -> list[dict]:
    cuit_legacy = (cuit or "").strip()
    try:
        cuit_normalizado = normalize_cuit(cuit)
    except ValueError:
        cuit_normalizado = cuit_legacy
    with get_session() as sesion:
        cliente = ClientRepository.get_by_cuit(sesion, cuit_legacy)
        if cliente is None and cuit_normalizado != cuit_legacy:
            cliente = ClientRepository.get_by_cuit(sesion, cuit_normalizado)
        if cliente is None:
            return []
        contactos = ClientRepository.contacts_for_client(sesion, cliente.cuit_cliente)
        return [
            {
                "id_contacto": contacto.id_contacto,
                "direccion": contacto.direccion,
                "ciudad": contacto.ciudad.nombre_ciudad,
                "telefono": contacto.telefono,
                "fecha_desde": contacto.fecha_desde,
                "fecha_hasta": contacto.fecha_hasta,
            }
            for contacto in contactos
        ]
