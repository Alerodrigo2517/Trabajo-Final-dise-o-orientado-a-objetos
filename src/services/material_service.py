"""Reglas de negocio para materiales y proveedores."""

from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from src.core.database import get_session
from src.core.validators import clean_text, positive_decimal
from src.repositories.material_repository import MaterialRepository


def list_suppliers() -> list[dict]:
    with get_session() as sesion:
        proveedores = MaterialRepository.list_suppliers(sesion)
        return [
            {"id_proveedor": fila.id_proveedor, "nombre": fila.nombre, "rubro": fila.rubro, "telefono": fila.telefono}
            for fila in proveedores
        ]


def list_materials() -> list[dict]:
    with get_session() as sesion:
        materiales = MaterialRepository.list_materials(sesion)
        return [
            {
                "id_material": fila.id_material,
                "descripcion": fila.descripcion,
                "precio_unitario": Decimal(fila.precio_unitario),
                "id_proveedor": fila.fk_proveedor,
                "proveedor": fila.proveedor.nombre,
                "rubro": fila.proveedor.rubro,
            }
            for fila in materiales
        ]


def create_supplier(nombre: str, rubro: str, telefono: str) -> dict:
    nombre_limpio = clean_text(nombre, "el nombre del proveedor", 100)
    rubro_limpio = clean_text(rubro, "el rubro", 100)
    telefono_limpio = clean_text(telefono, "el teléfono", 20)
    with get_session() as sesion:
        fila = MaterialRepository.create_supplier(
            sesion, nombre=nombre_limpio, rubro=rubro_limpio, telefono=telefono_limpio
        )
        return {"id_proveedor": fila.id_proveedor, "nombre": fila.nombre, "rubro": fila.rubro, "telefono": fila.telefono}


def create_material(descripcion: str, precio_unitario, proveedor_id: int) -> dict:
    descripcion_limpia = clean_text(descripcion, "la descripción", 150)
    precio = positive_decimal(precio_unitario, "el precio unitario", permitir_cero=True)
    try:
        with get_session() as sesion:
            proveedor = MaterialRepository.get_supplier(sesion, int(proveedor_id))
            if proveedor is None:
                raise ValueError("El proveedor seleccionado ya no existe. Actualizá la pantalla.")
            fila = MaterialRepository.create_material(
                sesion,
                descripcion=descripcion_limpia,
                precio_unitario=precio,
                proveedor=proveedor,
            )
            return {
                "id_material": fila.id_material,
                "descripcion": fila.descripcion,
                "precio_unitario": Decimal(fila.precio_unitario),
                "id_proveedor": fila.fk_proveedor,
                "proveedor": proveedor.nombre,
            }
    except IntegrityError as exc:
        raise ValueError("No se pudo guardar el material con ese proveedor.") from exc

