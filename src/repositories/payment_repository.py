"""Consultas y persistencia de pagos existentes."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from src.models.orm import ClientesContactoORM, PagoORM, PresupuestoORM


class PaymentRepository:
    @staticmethod
    def list_payments(session: Session) -> list[PagoORM]:
        statement = (
            select(PagoORM)
            .options(
                joinedload(PagoORM.presupuesto)
                .joinedload(PresupuestoORM.cliente_contacto)
                .joinedload(ClientesContactoORM.cliente)
            )
            .order_by(PagoORM.fecha_pago.desc(), PagoORM.id_pago.desc())
        )
        return list(session.scalars(statement).unique())

    @staticmethod
    def create_payment(session: Session, payment: PagoORM) -> PagoORM:
        session.add(payment)
        session.flush()
        return payment

