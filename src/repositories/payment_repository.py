"""Consultas y persistencia de pagos existentes."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from src.models.orm import ClientesContactoORM, PagoORM, PresupuestoORM


class PaymentRepository:
    @staticmethod
    def list_payments(sesion: Session) -> list[PagoORM]:
        sentencia = (
            select(PagoORM)
            .options(
                joinedload(PagoORM.presupuesto)
                .joinedload(PresupuestoORM.cliente_contacto)
                .joinedload(ClientesContactoORM.cliente)
            )
            .order_by(PagoORM.fecha_pago.desc(), PagoORM.id_pago.desc())
        )
        return list(sesion.scalars(sentencia).unique())

    @staticmethod
    def create_payment(sesion: Session, pago: PagoORM) -> PagoORM:
        sesion.add(pago)
        sesion.flush()
        return pago

