"""Reglas de negocio para pagos asociados a presupuestos existentes."""

from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from src.core.database import get_session
from src.core.validators import clean_text, positive_decimal
from src.models.orm import PagoORM
from src.repositories.budget_repository import BudgetRepository
from src.repositories.payment_repository import PaymentRepository


def list_payments() -> list[dict]:
    with get_session() as session:
        rows = PaymentRepository.list_payments(session)
        return [
            {
                "id_pago": row.id_pago,
                "id_presupuesto": row.fk_presupuesto,
                "cliente": f"{row.presupuesto.cliente_contacto.cliente.nombre} {row.presupuesto.cliente_contacto.cliente.apellido}",
                "fecha": row.fecha_pago,
                "monto": Decimal(row.monto),
                "metodo": row.metodo_pago,
                "referencia": row.referencia or "",
            }
            for row in rows
        ]


def create_payment(
    *, budget_id: int, payment_date, amount, method: str, reference: str = ""
) -> int:
    payment_amount = positive_decimal(amount, "el monto")
    cleaned_method = clean_text(method, "el método de pago", 30)
    cleaned_reference = (reference or "").strip()
    if len(cleaned_reference) > 100:
        raise ValueError("La referencia admite hasta 100 caracteres.")
    try:
        with get_session() as session:
            budget = BudgetRepository.get_budget(session, int(budget_id))
            if budget is None:
                raise ValueError("El presupuesto seleccionado ya no existe.")
            payment = PagoORM(
                presupuesto=budget,
                fecha_pago=payment_date,
                monto=payment_amount,
                metodo_pago=cleaned_method,
                referencia=cleaned_reference or None,
            )
            PaymentRepository.create_payment(session, payment)
            return payment.id_pago
    except IntegrityError as exc:
        raise ValueError("No se pudo registrar el pago. Verificá los datos e intentá de nuevo.") from exc

