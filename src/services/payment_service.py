"""Reglas de negocio para pagos asociados a presupuestos existentes."""

from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from src.core.database import get_session
from src.core.validators import clean_text, positive_decimal
from src.models.orm import PagoORM
from src.repositories.budget_repository import BudgetRepository
from src.repositories.payment_repository import PaymentRepository


def list_payments() -> list[dict]:
    with get_session() as sesion:
        filas = PaymentRepository.list_payments(sesion)
        return [
            {
                "id_pago": fila.id_pago,
                "id_presupuesto": fila.fk_presupuesto,
                "cliente": f"{fila.presupuesto.cliente_contacto.cliente.nombre} {fila.presupuesto.cliente_contacto.cliente.apellido}",
                "fecha": fila.fecha_pago,
                "monto": Decimal(fila.monto),
                "metodo": fila.metodo_pago,
                "referencia": fila.referencia or "",
            }
            for fila in filas
        ]


def create_payment(
    *, id_presupuesto: int, fecha_pago, monto, metodo: str, referencia: str = ""
) -> int:
    monto_pago = positive_decimal(monto, "el monto")
    metodo_limpio = clean_text(metodo, "el método de pago", 30)
    referencia_limpia = (referencia or "").strip()
    if len(referencia_limpia) > 100:
        raise ValueError("La referencia admite hasta 100 caracteres.")
    try:
        with get_session() as sesion:
            presupuesto = BudgetRepository.get_budget(sesion, int(id_presupuesto))
            if presupuesto is None:
                raise ValueError("El presupuesto seleccionado ya no existe.")
            pago = PagoORM(
                presupuesto=presupuesto,
                fecha_pago=fecha_pago,
                monto=monto_pago,
                metodo_pago=metodo_limpio,
                referencia=referencia_limpia or None,
            )
            PaymentRepository.create_payment(sesion, pago)
            return pago.id_pago
    except IntegrityError as exc:
        raise ValueError("No se pudo registrar el pago. Verificá los datos e intentá de nuevo.") from exc

