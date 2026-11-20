"""Reglas de negocio para pagos asociados a presupuestos existentes."""

from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from src.core.database import obtener_sesion_bd
from src.core.validators import limpiar_texto, validar_decimal_positivo
from src.models.orm import PagoORM
from src.repositories.budget_repository import BudgetRepository
from src.repositories.payment_repository import PaymentRepository
from src.services.budget_service import totales


def listar_pagos() -> list[dict]:
    with obtener_sesion_bd() as sesion:
        filas = PaymentRepository.listar_pagos(sesion)
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


def crear_pago(
    *, id_presupuesto: int, fecha_pago, monto, metodo: str, referencia: str = ""
) -> int:
    monto_pago = validar_decimal_positivo(monto, "el monto")
    metodo_limpio = limpiar_texto(metodo, "el método de pago", 30)
    referencia_limpia = (referencia or "").strip()
    if len(referencia_limpia) > 100:
        raise ValueError("La referencia admite hasta 100 caracteres.")
    try:
        with obtener_sesion_bd() as sesion:
            presupuesto = BudgetRepository.obtener_presupuesto(sesion, int(id_presupuesto))
            if presupuesto is None:
                raise ValueError("El presupuesto seleccionado ya no existe.")
            if presupuesto.estado != "APROBADO":
                raise ValueError("Solo se pueden registrar pagos para presupuestos aprobados.")
            total_presupuesto = totales(presupuesto)[2]
            total_pagado = sum(
                (Decimal(pago.monto) for pago in presupuesto.pagos), Decimal("0.00")
            )
            saldo_pendiente = total_presupuesto - total_pagado
            if saldo_pendiente <= 0:
                raise ValueError("El presupuesto ya no tiene saldo pendiente.")
            if monto_pago > saldo_pendiente:
                raise ValueError(
                    f"El pago supera el saldo pendiente de {saldo_pendiente:.2f}."
                )
            pago = PagoORM(
                presupuesto=presupuesto,
                fecha_pago=fecha_pago,
                monto=monto_pago,
                metodo_pago=metodo_limpio,
                referencia=referencia_limpia or None,
            )
            PaymentRepository.crear_pago(sesion, pago)
            return pago.id_pago
    except IntegrityError as exc:
        raise ValueError("No se pudo registrar el pago. Verificá los datos e intentá de nuevo.") from exc

