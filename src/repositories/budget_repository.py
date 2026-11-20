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
    def listar_presupuestos(sesion: Session) -> list[PresupuestoORM]:
        sentencia = (
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
        return list(sesion.scalars(sentencia).unique())

    @staticmethod
    def obtener_presupuesto(sesion: Session, id_presupuesto: int) -> PresupuestoORM | None:
        sentencia = (
            select(PresupuestoORM)
            .where(PresupuestoORM.id_presupuesto == id_presupuesto)
            .options(
                joinedload(PresupuestoORM.cliente_contacto).joinedload(ClientesContactoORM.cliente),
                joinedload(PresupuestoORM.ubicacion_trabajo).joinedload(UbicacionTrabajoORM.ciudad),
                joinedload(PresupuestoORM.tipo_trabajo),
                selectinload(PresupuestoORM.detalles).joinedload(DetallePresupuestoORM.material),
                selectinload(PresupuestoORM.pagos),
                joinedload(PresupuestoORM.trabajo),
            )
        )
        return sesion.scalar(sentencia)

    @staticmethod
    def obtener_o_crear_ciudad(sesion: Session, nombre: str) -> CiudadORM:
        ciudad = sesion.scalar(select(CiudadORM).where(func.lower(CiudadORM.nombre_ciudad) == nombre.lower()))
        if ciudad is None:
            ciudad = CiudadORM(nombre_ciudad=nombre)
            sesion.add(ciudad)
            sesion.flush()
        return ciudad

    @staticmethod
    def obtener_o_crear_tipo_trabajo(sesion: Session, nombre: str) -> TipoTrabajoORM:
        tipo_trabajo = sesion.scalar(
            select(TipoTrabajoORM).where(func.lower(TipoTrabajoORM.nombre_tipo) == nombre.lower())
        )
        if tipo_trabajo is None:
            tipo_trabajo = TipoTrabajoORM(nombre_tipo=nombre)
            sesion.add(tipo_trabajo)
            sesion.flush()
        return tipo_trabajo

    @staticmethod
    def obtener_contacto_cliente(sesion: Session, id_contacto: int) -> ClientesContactoORM | None:
        return sesion.get(ClientesContactoORM, id_contacto)

    @staticmethod
    def crear_contacto_cliente(
        sesion: Session,
        *,
        cuit_cliente: str,
        direccion: str,
        ciudad: CiudadORM,
        telefono: str,
        fecha_inicio: date,
    ) -> ClientesContactoORM:
        contacto = ClientesContactoORM(
            fk_cliente=cuit_cliente,
            direccion=direccion,
            ciudad=ciudad,
            telefono=telefono,
            fecha_desde=fecha_inicio,
        )
        sesion.add(contacto)
        sesion.flush()
        return contacto

    @staticmethod
    def crear_ubicacion_trabajo(sesion: Session, *, direccion: str, ciudad: CiudadORM) -> UbicacionTrabajoORM:
        ubicacion = UbicacionTrabajoORM(domicilio=direccion, ciudad=ciudad)
        sesion.add(ubicacion)
        sesion.flush()
        return ubicacion

    @staticmethod
    def listar_materiales(sesion: Session) -> list[MaterialORM]:
        return list(sesion.scalars(select(MaterialORM).order_by(MaterialORM.descripcion)))

    @staticmethod
    def obtener_material(sesion: Session, id_material: int) -> MaterialORM | None:
        return sesion.get(MaterialORM, id_material)

    @staticmethod
    def crear_presupuesto(sesion: Session, presupuesto: PresupuestoORM) -> PresupuestoORM:
        sesion.add(presupuesto)
        sesion.flush()
        return presupuesto

    @staticmethod
    def actualizar_estado(sesion: Session, presupuesto: PresupuestoORM, estado: str) -> None:
        presupuesto.estado = estado
        sesion.flush()

