"""Consultas y persistencia en las tablas de materiales y proveedores."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from src.models.orm import MaterialORM, ProveedorORM


class MaterialRepository:
    @staticmethod
    def list_suppliers(sesion: Session) -> list[ProveedorORM]:
        return list(sesion.scalars(select(ProveedorORM).order_by(ProveedorORM.nombre)))

    @staticmethod
    def create_supplier(sesion: Session, *, nombre: str, rubro: str, telefono: str) -> ProveedorORM:
        proveedor = ProveedorORM(nombre=nombre, rubro=rubro, telefono=telefono)
        sesion.add(proveedor)
        sesion.flush()
        return proveedor

    @staticmethod
    def list_materials(sesion: Session) -> list[MaterialORM]:
        sentencia = select(MaterialORM).options(joinedload(MaterialORM.proveedor)).order_by(MaterialORM.descripcion)
        return list(sesion.scalars(sentencia).unique())

    @staticmethod
    def get_material(sesion: Session, id_material: int) -> MaterialORM | None:
        return sesion.get(MaterialORM, id_material)

    @staticmethod
    def create_material(
        sesion: Session, *, descripcion: str, precio_unitario, proveedor: ProveedorORM
    ) -> MaterialORM:
        material = MaterialORM(
            descripcion=descripcion,
            precio_unitario=precio_unitario,
            proveedor=proveedor,
        )
        sesion.add(material)
        sesion.flush()
        return material

    @staticmethod
    def get_supplier(sesion: Session, id_proveedor: int) -> ProveedorORM | None:
        return sesion.get(ProveedorORM, id_proveedor)

