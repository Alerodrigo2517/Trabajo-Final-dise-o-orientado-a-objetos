"""Consultas y persistencia sobre presupuestos y sus tablas relacionadas."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from src.models.orm import (
    CiudadORM,
    ClientesContactoORM,
    DetallePresupuestoORM,
    MaterialORM,
    PresupuestoORM,
    TipoTrabajoORM,
    UbicacionTrabajoORM,
)


class BudgetRepository:
    @staticmethod
    def list_budgets(session: Session) -> list[PresupuestoORM]:
        statement = (
            select(PresupuestoORM)
            .options(
                joinedload(PresupuestoORM.cliente_contacto).joinedload(ClientesContactoORM.cliente),
                joinedload(PresupuestoORM.cliente_contacto).joinedload(ClientesContactoORM.ciudad),
                joinedload(PresupuestoORM.ubicacion_trabajo).joinedload(UbicacionTrabajoORM.ciudad),
                joinedload(PresupuestoORM.tipo_trabajo),
                selectinload(PresupuestoORM.detalles).joinedload(DetallePresupuestoORM.material),
                selectinload(PresupuestoORM.pagos),
                joinedload(PresupuestoORM.trabajo),
            )
            .order_by(PresupuestoORM.fecha_presupuesto.desc(), PresupuestoORM.id_presupuesto.desc())
        )
        return list(session.scalars(statement).unique())

    @staticmethod
    def get_budget(session: Session, budget_id: int) -> PresupuestoORM | None:
        statement = (
            select(PresupuestoORM)
            .where(PresupuestoORM.id_presupuesto == budget_id)
            .options(
                joinedload(PresupuestoORM.cliente_contacto).joinedload(ClientesContactoORM.cliente),
                joinedload(PresupuestoORM.ubicacion_trabajo).joinedload(UbicacionTrabajoORM.ciudad),
                joinedload(PresupuestoORM.tipo_trabajo),
                selectinload(PresupuestoORM.detalles).joinedload(DetallePresupuestoORM.material),
                selectinload(PresupuestoORM.pagos),
                joinedload(PresupuestoORM.trabajo),
            )
        )
        return session.scalar(statement)

    @staticmethod
    def get_or_create_city(session: Session, name: str) -> CiudadORM:
        city = session.scalar(select(CiudadORM).where(func.lower(CiudadORM.nombre_ciudad) == name.lower()))
        if city is None:
            city = CiudadORM(nombre_ciudad=name)
            session.add(city)
            session.flush()
        return city

    @staticmethod
    def get_or_create_work_type(session: Session, name: str) -> TipoTrabajoORM:
        work_type = session.scalar(
            select(TipoTrabajoORM).where(func.lower(TipoTrabajoORM.nombre_tipo) == name.lower())
        )
        if work_type is None:
            work_type = TipoTrabajoORM(nombre_tipo=name)
            session.add(work_type)
            session.flush()
        return work_type

    @staticmethod
    def get_client_contact(session: Session, contact_id: int) -> ClientesContactoORM | None:
        return session.get(ClientesContactoORM, contact_id)

    @staticmethod
    def create_client_contact(
        session: Session,
        *,
        client_cuit: str,
        address: str,
        city: CiudadORM,
        phone: str,
        start_date: date,
    ) -> ClientesContactoORM:
        contact = ClientesContactoORM(
            fk_cliente=client_cuit,
            direccion=address,
            ciudad=city,
            telefono=phone,
            fecha_desde=start_date,
        )
        session.add(contact)
        session.flush()
        return contact

    @staticmethod
    def create_work_location(session: Session, *, address: str, city: CiudadORM) -> UbicacionTrabajoORM:
        location = UbicacionTrabajoORM(domicilio=address, ciudad=city)
        session.add(location)
        session.flush()
        return location

    @staticmethod
    def list_materials(session: Session) -> list[MaterialORM]:
        return list(session.scalars(select(MaterialORM).order_by(MaterialORM.descripcion)))

    @staticmethod
    def get_material(session: Session, material_id: int) -> MaterialORM | None:
        return session.get(MaterialORM, material_id)

    @staticmethod
    def create_budget(session: Session, budget: PresupuestoORM) -> PresupuestoORM:
        session.add(budget)
        session.flush()
        return budget

    @staticmethod
    def update_status(session: Session, budget: PresupuestoORM, status: str) -> None:
        budget.estado = status
        session.flush()

