"""Reglas de negocio y cálculos usando las tablas actuales del proyecto."""

from datetime import date
from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from src.core.database import get_session
from src.core.validators import clean_text, normalize_cuit, positive_decimal
from src.models.orm import DetallePresupuestoORM, PresupuestoORM
from src.repositories.budget_repository import BudgetRepository
from src.repositories.client_repository import ClientRepository

PRESUPUESTO_ESTADOS = ("BORRADOR", "PENDIENTE", "APROBADO", "RECHAZADO", "VENCIDO", "CANCELADO")


def _totals(budget: PresupuestoORM) -> tuple[Decimal, Decimal, Decimal]:
    materials = sum(
        (Decimal(line.cantidad) * Decimal(line.precio_unitario) for line in budget.detalles),
        Decimal("0.00"),
    )
    if budget.tipo_calculo == "PORCENTAJE":
        labor = materials * Decimal(budget.costo_porcentaje) / Decimal("100")
    else:
        labor = Decimal(budget.costo_hora_trabajo) * Decimal(budget.duracion_horas)
    return materials, labor, materials + labor


def list_budgets() -> list[dict]:
    with get_session() as session:
        budgets = BudgetRepository.list_budgets(session)
        result = []
        for budget in budgets:
            client = budget.cliente_contacto.cliente
            material_total, labor_total, estimated_total = _totals(budget)
            paid = sum((Decimal(payment.monto) for payment in budget.pagos), Decimal("0.00"))
            result.append(
                {
                    "id_presupuesto": budget.id_presupuesto,
                    "fecha": budget.fecha_presupuesto,
                    "vencimiento": budget.fecha_vencimiento,
                    "cliente": f"{client.nombre} {client.apellido}",
                    "cuit": client.cuit_cliente,
                    "descripcion": budget.descripcion or "",
                    "tipo_trabajo": budget.tipo_trabajo.nombre_tipo,
                    "ubicacion": budget.ubicacion_trabajo.domicilio,
                    "ciudad": budget.ubicacion_trabajo.ciudad.nombre_ciudad,
                    "tipo_calculo": budget.tipo_calculo,
                    "estado": budget.estado,
                    "materiales": material_total,
                    "mano_obra": labor_total,
                    "total_estimado": estimated_total,
                    "pagado": paid,
                    "saldo_estimado": max(estimated_total - paid, Decimal("0.00")),
                    "trabajo_id": budget.trabajo.id_trabajo if budget.trabajo else None,
                    "lineas": [
                        {
                            "material_id": line.fk_material,
                            "material": line.material.descripcion,
                            "cantidad": Decimal(line.cantidad),
                            "precio_unitario": Decimal(line.precio_unitario),
                        }
                        for line in budget.detalles
                    ],
                }
            )
        return result


def create_budget(
    *,
    client_cuit: str,
    client_contact_id: int | None,
    contact_address: str,
    contact_city: str,
    contact_phone: str,
    work_address: str,
    work_city: str,
    work_type: str,
    description: str,
    budget_date: date,
    expiration_date: date | None,
    calculation_type: str,
    percentage,
    hourly_rate,
    hours,
    materials: list[dict],
) -> int:
    normalized_cuit = normalize_cuit(client_cuit)
    cleaned_work_address = clean_text(work_address, "la dirección del trabajo", 100)
    cleaned_work_city = clean_text(work_city, "la ciudad del trabajo", 100)
    cleaned_type = clean_text(work_type, "el tipo de trabajo", 50)
    cleaned_description = (description or "").strip()
    if len(cleaned_description) > 500:
        raise ValueError("La descripción admite hasta 500 caracteres.")
    if expiration_date is not None and expiration_date < budget_date:
        raise ValueError("La fecha de vencimiento no puede ser anterior al presupuesto.")
    if calculation_type not in {"PORCENTAJE", "POR_HORA"}:
        raise ValueError("Elegí una forma de cálculo válida.")

    if calculation_type == "PORCENTAJE":
        labor_percentage = positive_decimal(percentage, "el porcentaje de mano de obra", allow_zero=True)
        if labor_percentage > 100:
            raise ValueError("El porcentaje de mano de obra no puede superar el 100%.")
        labor_rate = None
        duration = None
    else:
        labor_percentage = None
        labor_rate = positive_decimal(hourly_rate, "el costo por hora", allow_zero=True)
        duration = positive_decimal(hours, "las horas estimadas", allow_zero=True)

    merged_items: dict[int, Decimal] = {}
    for item in materials:
        material_id = item.get("material_id")
        if material_id in (None, "", 0):
            continue
        try:
            material_id = int(material_id)
        except (TypeError, ValueError):
            raise ValueError("Elegí un material válido en cada renglón.") from None
        quantity = positive_decimal(item.get("cantidad", 0), "la cantidad de material")
        merged_items[material_id] = merged_items.get(material_id, Decimal("0")) + quantity

    try:
        with get_session() as session:
            client = ClientRepository.get_by_cuit(session, normalized_cuit)
            if client is None:
                raise ValueError("El cliente seleccionado no existe. Actualizá la lista.")

            if client_contact_id is not None:
                contact = BudgetRepository.get_client_contact(session, int(client_contact_id))
                if contact is None or contact.fk_cliente != client.cuit_cliente:
                    raise ValueError("El contacto seleccionado no pertenece a este cliente.")
                if contact.fecha_hasta is not None and contact.fecha_hasta < budget_date:
                    raise ValueError("Ese contacto ya no estaba vigente en la fecha del presupuesto.")
            else:
                cleaned_contact_address = clean_text(contact_address, "la dirección del cliente", 100)
                cleaned_contact_city = clean_text(contact_city, "la ciudad del cliente", 100)
                cleaned_phone = clean_text(contact_phone, "el teléfono del cliente", 20)
                client_city = BudgetRepository.get_or_create_city(session, cleaned_contact_city)
                contact = BudgetRepository.create_client_contact(
                    session,
                    client_cuit=client.cuit_cliente,
                    address=cleaned_contact_address,
                    city=client_city,
                    phone=cleaned_phone,
                    start_date=budget_date,
                )

            job_city = BudgetRepository.get_or_create_city(session, cleaned_work_city)
            work_location = BudgetRepository.create_work_location(
                session, address=cleaned_work_address, city=job_city
            )
            type_row = BudgetRepository.get_or_create_work_type(session, cleaned_type)
            budget = PresupuestoORM(
                fecha_presupuesto=budget_date,
                fecha_vencimiento=expiration_date,
                cliente_contacto=contact,
                ubicacion_trabajo=work_location,
                tipo_trabajo=type_row,
                descripcion=cleaned_description or None,
                tipo_calculo=calculation_type,
                costo_porcentaje=labor_percentage,
                costo_hora_trabajo=labor_rate,
                duracion_horas=duration,
                estado="BORRADOR",
            )
            for material_id, quantity in merged_items.items():
                material = BudgetRepository.get_material(session, material_id)
                if material is None:
                    raise ValueError("Uno de los materiales ya no existe. Actualizá la pantalla.")
                budget.detalles.append(
                    DetallePresupuestoORM(
                        material=material,
                        cantidad=quantity,
                        precio_unitario=material.precio_unitario,
                    )
                )
            BudgetRepository.create_budget(session, budget)
            return budget.id_presupuesto
    except IntegrityError as exc:
        raise ValueError("No se pudo guardar el presupuesto por una restricción de datos. Revisá el formulario.") from exc


def update_budget_status(budget_id: int, status: str) -> None:
    if status not in PRESUPUESTO_ESTADOS:
        raise ValueError("El estado elegido no es válido para un presupuesto.")
    with get_session() as session:
        budget = BudgetRepository.get_budget(session, int(budget_id))
        if budget is None:
            raise ValueError("El presupuesto ya no existe.")
        BudgetRepository.update_status(session, budget, status)


def materials_for_budget() -> list[dict]:
    from src.repositories.material_repository import MaterialRepository

    with get_session() as session:
        rows = MaterialRepository.list_materials(session)
        return [
            {"id_material": row.id_material, "descripcion": row.descripcion, "precio_unitario": Decimal(row.precio_unitario)}
            for row in rows
        ]

