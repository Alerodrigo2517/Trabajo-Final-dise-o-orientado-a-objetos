"""Consultas y persistencia en las tablas de materiales y proveedores."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from src.models.orm import MaterialORM, ProveedorORM


class MaterialRepository:
    @staticmethod
    def list_suppliers(session: Session) -> list[ProveedorORM]:
        return list(session.scalars(select(ProveedorORM).order_by(ProveedorORM.nombre)))

    @staticmethod
    def create_supplier(session: Session, *, nombre: str, rubro: str, telefono: str) -> ProveedorORM:
        supplier = ProveedorORM(nombre=nombre, rubro=rubro, telefono=telefono)
        session.add(supplier)
        session.flush()
        return supplier

    @staticmethod
    def list_materials(session: Session) -> list[MaterialORM]:
        statement = select(MaterialORM).options(joinedload(MaterialORM.proveedor)).order_by(MaterialORM.descripcion)
        return list(session.scalars(statement).unique())

    @staticmethod
    def get_material(session: Session, material_id: int) -> MaterialORM | None:
        return session.get(MaterialORM, material_id)

    @staticmethod
    def create_material(
        session: Session, *, descripcion: str, precio_unitario, proveedor: ProveedorORM
    ) -> MaterialORM:
        material = MaterialORM(
            descripcion=descripcion,
            precio_unitario=precio_unitario,
            proveedor=proveedor,
        )
        session.add(material)
        session.flush()
        return material

    @staticmethod
    def get_supplier(session: Session, supplier_id: int) -> ProveedorORM | None:
        return session.get(ProveedorORM, supplier_id)

