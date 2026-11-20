"""Reglas de negocio y cálculos usando las tablas actuales del proyecto."""

from datetime import date
from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from src.core.database import obtener_sesion_bd
from src.core.validators import limpiar_texto, normalizar_cuit, validar_decimal_positivo
from src.models.orm import DetallePresupuestoORM, PresupuestoORM
from src.repositories.budget_repository import BudgetRepository
from src.repositories.client_repository import ClientRepository

PRESUPUESTO_ESTADOS = ("BORRADOR", "PENDIENTE", "APROBADO", "RECHAZADO", "VENCIDO", "CANCELADO")
TRANSICIONES_PRESUPUESTO = {
    "BORRADOR": {"PENDIENTE", "CANCELADO"},
    "PENDIENTE": {"APROBADO", "RECHAZADO", "VENCIDO", "CANCELADO"},
    "APROBADO": {"PENDIENTE", "RECHAZADO", "VENCIDO", "CANCELADO"},
    "RECHAZADO": {"PENDIENTE", "CANCELADO"},
    "VENCIDO": {"PENDIENTE", "CANCELADO"},
    "CANCELADO": set(),
}


def totales(presupuesto: PresupuestoORM) -> tuple[Decimal, Decimal, Decimal]:
    materiales = sum(
        (Decimal(linea.cantidad) * Decimal(linea.precio_unitario) for linea in presupuesto.detalles),
        Decimal("0.00"),
    )
    if presupuesto.tipo_calculo == "PORCENTAJE":
        mano_obra = materiales * Decimal(presupuesto.costo_porcentaje) / Decimal("100")
    else:
        mano_obra = Decimal(presupuesto.costo_hora_trabajo) * Decimal(presupuesto.duracion_horas)
    return materiales, mano_obra, materiales + mano_obra


def listar_presupuestos() -> list[dict]:
    with obtener_sesion_bd() as sesion:
        presupuestos = BudgetRepository.listar_presupuestos(sesion)
        resultado = []
        for presupuesto in presupuestos:
            cliente = presupuesto.cliente_contacto.cliente
            total_materiales, total_mano_obra, total_estimado = totales(presupuesto)
            pagado = sum((Decimal(pago.monto) for pago in presupuesto.pagos), Decimal("0.00"))
            resultado.append(
                {
                    "id_presupuesto": presupuesto.id_presupuesto,
                    "fecha": presupuesto.fecha_presupuesto,
                    "vencimiento": presupuesto.fecha_vencimiento,
                    "cliente": f"{cliente.nombre} {cliente.apellido}",
                    "cuit": cliente.cuit_cliente,
                    "descripcion": presupuesto.descripcion or "",
                    "tipo_trabajo": presupuesto.tipo_trabajo.nombre_tipo,
                    "ubicacion": presupuesto.ubicacion_trabajo.domicilio,
                    "ciudad": presupuesto.ubicacion_trabajo.ciudad.nombre_ciudad,
                    "tipo_calculo": presupuesto.tipo_calculo,
                    "estado": presupuesto.estado,
                    "materiales": total_materiales,
                    "mano_obra": total_mano_obra,
                    "total_estimado": total_estimado,
                    "pagado": pagado,
                    "saldo_estimado": max(total_estimado - pagado, Decimal("0.00")),
                    "trabajo_id": presupuesto.trabajo.id_trabajo if presupuesto.trabajo else None,
                    "lineas": [
                        {
                            "material_id": linea.fk_material,
                            "material": linea.material.descripcion,
                            "cantidad": Decimal(linea.cantidad),
                            "precio_unitario": Decimal(linea.precio_unitario),
                        }
                        for linea in presupuesto.detalles
                    ],
                }
            )
        return resultado


def crear_presupuesto(
    *,
    cuit_cliente: str,
    id_contacto_cliente: int | None,
    direccion_contacto: str,
    ciudad_contacto: str,
    telefono_contacto: str,
    direccion_trabajo: str,
    ciudad_trabajo: str,
    tipo_trabajo: str,
    descripcion: str,
    fecha_presupuesto: date,
    fecha_vencimiento: date | None,
    tipo_calculo: str,
    porcentaje,
    tarifa_hora,
    horas,
    materiales: list[dict],
) -> int:
    cuit_legacy = (cuit_cliente or "").strip()
    cuit_normalizado = cuit_legacy
    try:
        cuit_normalizado = normalizar_cuit(cuit_cliente)
    except ValueError:
        # Se conserva compatibilidad con identificadores históricos que no
        # cumplen el rango actual de alta, para consultar presupuestos previos.
        pass
    direccion_trabajo_limpia = limpiar_texto(direccion_trabajo, "la dirección del trabajo", 100)
    ciudad_trabajo_limpia = limpiar_texto(ciudad_trabajo, "la ciudad del trabajo", 100)
    tipo_limpio = limpiar_texto(tipo_trabajo, "el tipo de trabajo", 50)
    descripcion_limpia = (descripcion or "").strip()
    if len(descripcion_limpia) > 500:
        raise ValueError("La descripción admite hasta 500 caracteres.")
    if fecha_vencimiento is not None and fecha_vencimiento < fecha_presupuesto:
        raise ValueError("La fecha de vencimiento no puede ser anterior al presupuesto.")
    if tipo_calculo not in {"PORCENTAJE", "POR_HORA"}:
        raise ValueError("Elegí una forma de cálculo válida.")

    if tipo_calculo == "PORCENTAJE":
        porcentaje_mano_obra = validar_decimal_positivo(porcentaje, "el porcentaje de mano de obra", permitir_cero=True)
        if porcentaje_mano_obra > 100:
            raise ValueError("El porcentaje de mano de obra no puede superar el 100%.")
        tarifa_mano_obra = None
        duracion = None
    else:
        porcentaje_mano_obra = None
        tarifa_mano_obra = validar_decimal_positivo(tarifa_hora, "el costo por hora", permitir_cero=True)
        duracion = validar_decimal_positivo(horas, "las horas estimadas", permitir_cero=True)

    elementos_combinados: dict[int, Decimal] = {}
    for elemento in materiales:
        id_material = elemento.get("material_id")
        if id_material in (None, "", 0):
            continue
        try:
            id_material = int(id_material)
        except (TypeError, ValueError):
            raise ValueError("Elegí un material válido en cada renglón.") from None
        cantidad = validar_decimal_positivo(elemento.get("cantidad", 0), "la cantidad de material")
        elementos_combinados[id_material] = elementos_combinados.get(id_material, Decimal("0")) + cantidad

    try:
        with obtener_sesion_bd() as sesion:
            cliente = ClientRepository.obtener_por_cuit(sesion, cuit_legacy)
            if cliente is None and cuit_normalizado != cuit_legacy:
                cliente = ClientRepository.obtener_por_cuit(sesion, cuit_normalizado)
            if cliente is None:
                raise ValueError("El cliente seleccionado no existe. Actualizá la lista.")

            if id_contacto_cliente is not None:
                contacto = BudgetRepository.obtener_contacto_cliente(sesion, int(id_contacto_cliente))
                if contacto is None or contacto.fk_cliente != cliente.cuit_cliente:
                    raise ValueError("El contacto seleccionado no pertenece a este cliente.")
                if contacto.fecha_hasta is not None and contacto.fecha_hasta < fecha_presupuesto:
                    raise ValueError("Ese contacto ya no estaba vigente en la fecha del presupuesto.")
            else:
                direccion_contacto_limpia = limpiar_texto(direccion_contacto, "la dirección del cliente", 100)
                ciudad_contacto_limpia = limpiar_texto(ciudad_contacto, "la ciudad del cliente", 100)
                telefono_limpio = limpiar_texto(telefono_contacto, "el teléfono del cliente", 20)
                ciudad_cliente = BudgetRepository.obtener_o_crear_ciudad(sesion, ciudad_contacto_limpia)
                contacto = BudgetRepository.crear_contacto_cliente(
                    sesion,
                    cuit_cliente=cliente.cuit_cliente,
                    direccion=direccion_contacto_limpia,
                    ciudad=ciudad_cliente,
                    telefono=telefono_limpio,
                    fecha_inicio=fecha_presupuesto,
                )

            ciudad_trabajo = BudgetRepository.obtener_o_crear_ciudad(sesion, ciudad_trabajo_limpia)
            ubicacion_trabajo = BudgetRepository.crear_ubicacion_trabajo(
                sesion, direccion=direccion_trabajo_limpia, ciudad=ciudad_trabajo
            )
            fila_tipo = BudgetRepository.obtener_o_crear_tipo_trabajo(sesion, tipo_limpio)
            presupuesto = PresupuestoORM(
                fecha_presupuesto=fecha_presupuesto,
                fecha_vencimiento=fecha_vencimiento,
                fk_cliente=cliente.cuit_cliente,
                cliente_contacto=contacto,
                ubicacion_trabajo=ubicacion_trabajo,
                tipo_trabajo=fila_tipo,
                descripcion=descripcion_limpia or None,
                tipo_calculo=tipo_calculo,
                costo_porcentaje=porcentaje_mano_obra,
                costo_hora_trabajo=tarifa_mano_obra,
                duracion_horas=duracion,
                estado="BORRADOR",
            )
            # Asociar el objeto a la sesión antes de enlazar los detalles con
            # materiales que ya están persistidos evita estados transitorios
            # en las relaciones bidireccionales de SQLAlchemy.
            sesion.add(presupuesto)
            for id_material, cantidad in elementos_combinados.items():
                material = BudgetRepository.obtener_material(sesion, id_material)
                if material is None:
                    raise ValueError("Uno de los materiales ya no existe. Actualizá la pantalla.")
                presupuesto.detalles.append(
                    DetallePresupuestoORM(
                        material=material,
                        cantidad=cantidad,
                        precio_unitario=material.precio_unitario,
                        subtotal=cantidad * Decimal(material.precio_unitario),
                    )
                )
            BudgetRepository.crear_presupuesto(sesion, presupuesto)
            return presupuesto.id_presupuesto
    except IntegrityError as exc:
        raise ValueError("No se pudo guardar el presupuesto por una restricción de datos. Revisá el formulario.") from exc


def actualizar_estado_presupuesto(id_presupuesto: int, estado: str) -> None:
    if estado not in PRESUPUESTO_ESTADOS:
        raise ValueError("El estado elegido no es válido para un presupuesto.")
    with obtener_sesion_bd() as sesion:
        presupuesto = BudgetRepository.obtener_presupuesto(sesion, int(id_presupuesto))
        if presupuesto is None:
            raise ValueError("El presupuesto ya no existe.")
        if estado == presupuesto.estado:
            return
        if estado not in TRANSICIONES_PRESUPUESTO[presupuesto.estado]:
            raise ValueError(
                f"No se puede cambiar un presupuesto de {presupuesto.estado.replace('_', ' ').lower()} "
                f"a {estado.replace('_', ' ').lower()}."
            )
        if estado != "APROBADO" and (presupuesto.pagos or presupuesto.trabajo is not None):
            raise ValueError(
                "Un presupuesto con pagos u orden de trabajo debe permanecer aprobado."
            )
        BudgetRepository.actualizar_estado(sesion, presupuesto, estado)


def obtener_materiales_para_presupuesto() -> list[dict]:
    from src.repositories.material_repository import MaterialRepository

    with obtener_sesion_bd() as sesion:
        filas = MaterialRepository.listar_materiales(sesion)
        return [
            {"id_material": fila.id_material, "descripcion": fila.descripcion, "precio_unitario": Decimal(fila.precio_unitario)}
            for fila in filas
        ]

