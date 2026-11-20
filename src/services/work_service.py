"""Reglas de negocio para órdenes de trabajo según el enum existente."""

from datetime import date

from sqlalchemy.exc import IntegrityError

from src.core.database import obtener_sesion_bd
from src.core.validators import limpiar_texto
from src.models.orm import TrabajoORM
from src.repositories.budget_repository import BudgetRepository
from src.repositories.work_repository import WorkRepository

ESTADOS_TRABAJO = ("PENDIENTE", "EN_PROCESO", "FINALIZADO", "CANCELADO")


def listar_trabajos() -> list[dict]:
    with obtener_sesion_bd() as sesion:
        filas = WorkRepository.listar_trabajos(sesion)
        return [
            {
                "id_trabajo": fila.id_trabajo,
                "id_presupuesto": fila.fk_presupuesto,
                "cliente": f"{fila.presupuesto.cliente_contacto.cliente.nombre} {fila.presupuesto.cliente_contacto.cliente.apellido}",
                "trabajo": fila.presupuesto.tipo_trabajo.nombre_tipo,
                "ubicacion": fila.presupuesto.ubicacion_trabajo.domicilio,
                "ciudad": fila.presupuesto.ubicacion_trabajo.ciudad.nombre_ciudad,
                "fecha_inicio": fila.fecha_inicio,
                "fecha_fin": fila.fecha_fin,
                "estado": fila.estado,
                "observaciones": fila.observaciones or "",
            }
            for fila in filas
        ]


def crear_trabajo(*, id_presupuesto: int, fecha_inicio: date | None, observaciones: str = "") -> int:
    observaciones_limpias = (observaciones or "").strip()
    if len(observaciones_limpias) > 500:
        raise ValueError("Las observaciones admiten hasta 500 caracteres.")
    try:
        with obtener_sesion_bd() as sesion:
            presupuesto = BudgetRepository.obtener_presupuesto(sesion, int(id_presupuesto))
            if presupuesto is None:
                raise ValueError("El presupuesto seleccionado ya no existe.")
            if presupuesto.estado != "APROBADO":
                raise ValueError("Solo podés iniciar un trabajo con un presupuesto aprobado.")
            if WorkRepository.obtener_trabajo_por_presupuesto(sesion, int(id_presupuesto)) is not None:
                raise ValueError("Ese presupuesto ya tiene una orden de trabajo.")
            trabajo = TrabajoORM(
                presupuesto=presupuesto,
                fecha_inicio=fecha_inicio,
                estado="PENDIENTE",
                observaciones=observaciones_limpias or None,
            )
            WorkRepository.crear_trabajo(sesion, trabajo)
            return trabajo.id_trabajo
    except IntegrityError as exc:
        raise ValueError("Ese presupuesto ya tiene una orden de trabajo.") from exc


def actualizar_trabajo(
    *, id_trabajo: int, estado: str, fecha_inicio: date | None, fecha_fin: date | None, observaciones: str = ""
) -> None:
    if estado not in ESTADOS_TRABAJO:
        raise ValueError("El estado elegido no es válido para un trabajo.")
    if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
        raise ValueError("La fecha de finalización no puede ser anterior a la fecha de inicio.")
    if estado == "FINALIZADO" and fecha_fin is None:
        raise ValueError("Indicá la fecha de finalización para cerrar el trabajo.")
    if estado != "FINALIZADO" and fecha_fin is not None:
        raise ValueError("Solo una orden finalizada puede tener fecha de finalización.")
    observaciones_limpias = (observaciones or "").strip()
    if len(observaciones_limpias) > 500:
        raise ValueError("Las observaciones admiten hasta 500 caracteres.")
    with obtener_sesion_bd() as sesion:
        trabajo = WorkRepository.obtener_trabajo(sesion, int(id_trabajo))
        if trabajo is None:
            raise ValueError("La orden de trabajo ya no existe.")
        WorkRepository.actualizar_trabajo(
            sesion,
            trabajo,
            estado=estado,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            observaciones=observaciones_limpias or None,
        )

