from dataclasses import dataclass, field

from .orm import (
    CiudadORM as Ciudad,
    ClienteORM as Cliente,
    ClientesContactoORM as ClientesContacto,
    DetallePresupuestoORM as DetallePresupuesto,
    HistorialClienteORM as HistorialCliente,
    MaterialORM as Material,
    PagoORM as Pago,
    PresupuestoORM as Presupuesto,
    ProveedorORM as Proveedor,
    TipoTrabajoORM as TipoTrabajo,
    TrabajoORM as Trabajo,
    UbicacionTrabajoORM as UbicacionTrabajo,
)


@dataclass(frozen=True, slots=True)
class Usuario:
    nombre: str
    usuario: str
    contrasena_hash: str = field(repr=False)
    id_usuario: int | None = None
    rol: str = "OPERADOR"


__all__ = [
    "Ciudad",
    "Cliente",
    "ClientesContacto",
    "DetallePresupuesto",
    "HistorialCliente",
    "Material",
    "Pago",
    "Presupuesto",
    "Proveedor",
    "TipoTrabajo",
    "Trabajo",
    "UbicacionTrabajo",
    "Usuario",
]
