"""Validaciones de entrada para mantener consistencia con el esquema existente."""

import re
from decimal import Decimal, InvalidOperation


def clean_text(value: str, field_name: str, max_length: int) -> str:
    cleaned = " ".join((value or "").strip().split())
    if not cleaned:
        raise ValueError(f"Completá {field_name}.")
    if len(cleaned) > max_length:
        raise ValueError(f"{field_name.capitalize()} admite hasta {max_length} caracteres.")
    return cleaned


def normalize_cuit(value: str) -> str:
    digits = re.sub(r"\D", "", value or "")
    if len(digits) != 11:
        raise ValueError("El CUIT debe contener 11 dígitos.")
    return digits


def display_cuit(value: str) -> str:
    digits = normalize_cuit(value)
    return f"{digits[:2]}-{digits[2:10]}-{digits[10]}"


def positive_decimal(value: Decimal | int | float | str, field_name: str, *, allow_zero: bool = False) -> Decimal:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{field_name.capitalize()} debe ser un número válido.") from None
    if not amount.is_finite() or amount < 0 or (amount == 0 and not allow_zero):
        comparator = "no puede ser negativo" if allow_zero else "debe ser mayor que cero"
        raise ValueError(f"{field_name.capitalize()} {comparator}.")
    return amount

