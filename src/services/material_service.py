"""Reglas de negocio para materiales y proveedores."""

from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from src.core.database import get_session
from src.core.validators import clean_text, positive_decimal
from src.repositories.material_repository import MaterialRepository


def list_suppliers() -> list[dict]:
    with get_session() as session:
        suppliers = MaterialRepository.list_suppliers(session)
        return [
            {"id_proveedor": row.id_proveedor, "nombre": row.nombre, "rubro": row.rubro, "telefono": row.telefono}
            for row in suppliers
        ]


def list_materials() -> list[dict]:
    with get_session() as session:
        materials = MaterialRepository.list_materials(session)
        return [
            {
                "id_material": row.id_material,
                "descripcion": row.descripcion,
                "precio_unitario": Decimal(row.precio_unitario),
                "id_proveedor": row.fk_proveedor,
                "proveedor": row.proveedor.nombre,
                "rubro": row.proveedor.rubro,
            }
            for row in materials
        ]


def create_supplier(nombre: str, rubro: str, telefono: str) -> dict:
    cleaned_name = clean_text(nombre, "el nombre del proveedor", 100)
    cleaned_rubro = clean_text(rubro, "el rubro", 100)
    cleaned_phone = clean_text(telefono, "el teléfono", 20)
    with get_session() as session:
        row = MaterialRepository.create_supplier(
            session, nombre=cleaned_name, rubro=cleaned_rubro, telefono=cleaned_phone
        )
        return {"id_proveedor": row.id_proveedor, "nombre": row.nombre, "rubro": row.rubro, "telefono": row.telefono}


def create_material(descripcion: str, precio_unitario, proveedor_id: int) -> dict:
    cleaned_description = clean_text(descripcion, "la descripción", 150)
    price = positive_decimal(precio_unitario, "el precio unitario", allow_zero=True)
    try:
        with get_session() as session:
            supplier = MaterialRepository.get_supplier(session, int(proveedor_id))
            if supplier is None:
                raise ValueError("El proveedor seleccionado ya no existe. Actualizá la pantalla.")
            row = MaterialRepository.create_material(
                session,
                descripcion=cleaned_description,
                precio_unitario=price,
                proveedor=supplier,
            )
            return {
                "id_material": row.id_material,
                "descripcion": row.descripcion,
                "precio_unitario": Decimal(row.precio_unitario),
                "id_proveedor": row.fk_proveedor,
                "proveedor": supplier.nombre,
            }
    except IntegrityError as exc:
        raise ValueError("No se pudo guardar el material con ese proveedor.") from exc

