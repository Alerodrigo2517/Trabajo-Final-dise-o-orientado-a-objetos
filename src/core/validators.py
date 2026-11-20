"""Validaciones de entrada para mantener consistencia con el esquema existente."""

import re
from decimal import Decimal, InvalidOperation


def limpiar_texto(valor: str, nombre_campo: str, longitud_maxima: int) -> str:
    limpio = " ".join((valor or "").strip().split())
    if not limpio:
        raise ValueError(f"Completá {nombre_campo}.")
    if len(limpio) > longitud_maxima:
        raise ValueError(f"{nombre_campo.capitalize()} admite hasta {longitud_maxima} caracteres.")
    return limpio


def normalizar_cuit(valor: str) -> str:
    digitos = re.sub(r"\D", "", valor or "")
    if not 8 <= len(digitos) <= 11:
        raise ValueError("El CUIT/CUIL debe contener entre 8 y 11 dígitos.")
    return digitos


def mostrar_cuit(valor: str) -> str:
    digitos = normalizar_cuit(valor)
    if len(digitos) < 11:
        return digitos
    return f"{digitos[:2]}-{digitos[2:10]}-{digitos[10]}"


def validar_decimal_positivo(valor: Decimal | int | float | str, nombre_campo: str, *, permitir_cero: bool = False) -> Decimal:
    try:
        monto = Decimal(str(valor))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{nombre_campo.capitalize()} debe ser un número válido.") from None
    if not monto.is_finite() or monto < 0 or (monto == 0 and not permitir_cero):
        comparador = "no puede ser negativo" if permitir_cero else "debe ser mayor que cero"
        raise ValueError(f"{nombre_campo.capitalize()} {comparador}.")
    return monto

