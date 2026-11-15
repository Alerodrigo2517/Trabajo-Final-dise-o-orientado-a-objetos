from dataclasses import dataclass

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


@dataclass
class Usuario:
    nombre: str
    usuario: str
    contrasena_hash: str
    id_usuario: int | None = None


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
