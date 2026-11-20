"""Reglas de negocio para clientes y sus datos de contacto."""

from datetime import date
import re

from sqlalchemy.exc import IntegrityError

from src.core.database import obtener_sesion_bd
from src.core.validators import limpiar_texto, mostrar_cuit, normalizar_cuit
from src.repositories.budget_repository import BudgetRepository
from src.repositories.client_repository import ClientRepository


def listar_clientes() -> list[dict]:
    with obtener_sesion_bd() as sesion:
        clientes = ClientRepository.listar_clientes(sesion)
        return [
            {
                "cuit_cliente": cliente.cuit_cliente,
                "cuit_display": mostrar_cuit(cliente.cuit_cliente),
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


def crear_cliente(
    cuit: str,
    nombre: str,
    apellido: str,
    direccion: str = "",
    ciudad: str = "",
    telefono: str = "",
) -> dict:
    cuit_normalizado = normalizar_cuit(cuit)
    nombre_limpio = limpiar_texto(nombre, "el nombre", 45)
    apellido_limpio = limpiar_texto(apellido, "el apellido", 45)

    tiene_datos_contacto = any((direccion or "").strip() or (ciudad or "").strip() or (telefono or "").strip() for _ in [0])
    direccion_limpia = ""
    ciudad_limpia = ""
    telefono_limpio = ""
    if tiene_datos_contacto:
        direccion_limpia = limpiar_texto(direccion, "la dirección del cliente", 100)
        ciudad_limpia = limpiar_texto(ciudad, "la ciudad del cliente", 100)
        telefono_limpio = limpiar_texto(telefono, "el teléfono del cliente", 20)

    try:
        with obtener_sesion_bd() as sesion:
            existentes = ClientRepository.listar_clientes(sesion)
            if any(re.sub(r"\D", "", cliente.cuit_cliente) == cuit_normalizado for cliente in existentes):
                raise ValueError("Ya existe un cliente con ese CUIT.")
            cliente = ClientRepository.crear_cliente(
                sesion,
                cuit=cuit_normalizado,
                nombre=nombre_limpio,
                apellido=apellido_limpio,
            )
            if tiene_datos_contacto:
                ciudad_orm = BudgetRepository.obtener_o_crear_ciudad(sesion, ciudad_limpia)
                BudgetRepository.crear_contacto_cliente(
                    sesion,
                    cuit_cliente=cliente.cuit_cliente,
                    direccion=direccion_limpia,
                    ciudad=ciudad_orm,
                    telefono=telefono_limpio,
                    fecha_inicio=date.today(),
                )
            return {
                "cuit_cliente": cliente.cuit_cliente,
                "cuit_display": mostrar_cuit(cliente.cuit_cliente),
                "nombre": cliente.nombre,
                "apellido": cliente.apellido,
                "nombre_completo": f"{cliente.nombre} {cliente.apellido}",
            }
    except IntegrityError as exc:
        raise ValueError("Ya existe un cliente con ese CUIT.") from exc


def obtener_contactos_cliente(cuit: str) -> list[dict]:
    cuit_legacy = (cuit or "").strip()
    try:
        cuit_normalizado = normalizar_cuit(cuit)
    except ValueError:
        cuit_normalizado = cuit_legacy
    with obtener_sesion_bd() as sesion:
        cliente = ClientRepository.obtener_por_cuit(sesion, cuit_legacy)
        if cliente is None and cuit_normalizado != cuit_legacy:
            cliente = ClientRepository.obtener_por_cuit(sesion, cuit_normalizado)
        if cliente is None:
            return []
        contactos = ClientRepository.obtener_contactos_cliente(sesion, cliente.cuit_cliente)
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
