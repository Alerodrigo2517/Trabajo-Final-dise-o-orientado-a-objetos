"""Reglas de negocio para materiales y proveedores."""

from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from src.core.database import obtener_sesion_bd
from src.core.validators import limpiar_texto, validar_decimal_positivo
from src.repositories.material_repository import MaterialRepository


def listar_proveedores() -> list[dict]:
    with obtener_sesion_bd() as sesion:
        proveedores = MaterialRepository.listar_proveedores(sesion)
        return [
            {"id_proveedor": fila.id_proveedor, "nombre": fila.nombre, "rubro": fila.rubro, "telefono": fila.telefono}
            for fila in proveedores
        ]


def listar_materiales() -> list[dict]:
    with obtener_sesion_bd() as sesion:
        materiales = MaterialRepository.listar_materiales(sesion)
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


def crear_proveedor(nombre: str, rubro: str, telefono: str) -> dict:
    nombre_limpio = limpiar_texto(nombre, "el nombre del proveedor", 100)
    rubro_limpio = limpiar_texto(rubro, "el rubro", 100)
    telefono_limpio = limpiar_texto(telefono, "el teléfono", 20)
    with obtener_sesion_bd() as sesion:
        fila = MaterialRepository.crear_proveedor(
            sesion, nombre=nombre_limpio, rubro=rubro_limpio, telefono=telefono_limpio
        )
        return {"id_proveedor": fila.id_proveedor, "nombre": fila.nombre, "rubro": fila.rubro, "telefono": fila.telefono}


def crear_material(descripcion: str, precio_unitario, proveedor_id: int) -> dict:
    descripcion_limpia = limpiar_texto(descripcion, "la descripción", 150)
    precio = validar_decimal_positivo(precio_unitario, "el precio unitario", permitir_cero=True)
    try:
        with obtener_sesion_bd() as sesion:
            proveedor = MaterialRepository.obtener_proveedor(sesion, int(proveedor_id))
            if proveedor is None:
                raise ValueError("El proveedor seleccionado ya no existe. Actualizá la pantalla.")
            fila = MaterialRepository.crear_material(
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

