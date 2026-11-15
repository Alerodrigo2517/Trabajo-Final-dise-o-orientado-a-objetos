from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class CiudadORM(Base):
    __tablename__ = "ciudades"
    __table_args__ = (
        UniqueConstraint("nombre_ciudad", name="uq_ciudades_nombre"),
    )

    id_ciudad: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_ciudad: Mapped[str] = mapped_column(String(100), nullable=False)

    contactos: Mapped[list[ClientesContactoORM]] = relationship(back_populates="ciudad")
    ubicaciones_trabajo: Mapped[list[UbicacionTrabajoORM]] = relationship(back_populates="ciudad")


class ClienteORM(Base):
    __tablename__ = "clientes"

    cuit_cliente: Mapped[str] = mapped_column(String(13), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(45), nullable=False)
    apellido: Mapped[str] = mapped_column(String(45), nullable=False)

    contactos: Mapped[list[ClientesContactoORM]] = relationship(back_populates="cliente")
    historial: Mapped[list[HistorialClienteORM]] = relationship(back_populates="cliente")


class ClientesContactoORM(Base):
    __tablename__ = "clientes_contacto"
    __table_args__ = (
        CheckConstraint(
            "fecha_hasta IS NULL OR fecha_hasta >= fecha_desde",
            name="chk_clientes_contacto_fechas",
        ),
    )

    id_contacto: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fk_cliente: Mapped[str] = mapped_column(
        String(13),
        ForeignKey(
            "clientes.cuit_cliente",
            name="fk_clientes_contacto_cliente",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    direccion: Mapped[str] = mapped_column(String(100), nullable=False)
    fk_ciudad: Mapped[int] = mapped_column(
        ForeignKey(
            "ciudades.id_ciudad",
            name="fk_clientes_contacto_ciudad",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    telefono: Mapped[str] = mapped_column(String(20), nullable=False)
    fecha_desde: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_hasta: Mapped[date | None] = mapped_column(Date, nullable=True)

    cliente: Mapped[ClienteORM] = relationship(back_populates="contactos")
    ciudad: Mapped[CiudadORM] = relationship(back_populates="contactos")
    presupuestos: Mapped[list[PresupuestoORM]] = relationship(back_populates="cliente_contacto")


class UbicacionTrabajoORM(Base):
    __tablename__ = "ubicacion_trabajo"

    id_ubicacion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    domicilio: Mapped[str] = mapped_column(String(100), nullable=False)
    fk_ciudad: Mapped[int] = mapped_column(
        ForeignKey(
            "ciudades.id_ciudad",
            name="fk_ubicacion_trabajo_ciudad",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        nullable=False,
    )

    ciudad: Mapped[CiudadORM] = relationship(back_populates="ubicaciones_trabajo")
    presupuestos: Mapped[list[PresupuestoORM]] = relationship(back_populates="ubicacion_trabajo")


class TipoTrabajoORM(Base):
    __tablename__ = "tipos_trabajo"
    __table_args__ = (
        UniqueConstraint("nombre_tipo", name="uq_tipos_trabajo_nombre"),
    )

    id_tipo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_tipo: Mapped[str] = mapped_column(String(50), nullable=False)

    presupuestos: Mapped[list[PresupuestoORM]] = relationship(back_populates="tipo_trabajo")


class PresupuestoORM(Base):
    __tablename__ = "presupuesto"
    __table_args__ = (
        CheckConstraint(
            "costo_porcentaje IS NULL OR costo_porcentaje >= 0",
            name="chk_presupuesto_porcentaje",
        ),
        CheckConstraint(
            "costo_hora_trabajo IS NULL OR costo_hora_trabajo >= 0",
            name="chk_presupuesto_costo_hora",
        ),
        CheckConstraint(
            "duracion_horas IS NULL OR duracion_horas >= 0",
            name="chk_presupuesto_duracion",
        ),
        CheckConstraint(
            "fecha_vencimiento IS NULL OR fecha_vencimiento >= fecha_presupuesto",
            name="chk_presupuesto_fechas",
        ),
        CheckConstraint(
            "(tipo_calculo = 'PORCENTAJE' AND costo_porcentaje IS NOT NULL "
            "AND costo_hora_trabajo IS NULL AND duracion_horas IS NULL) OR "
            "(tipo_calculo = 'POR_HORA' AND costo_porcentaje IS NULL "
            "AND costo_hora_trabajo IS NOT NULL AND duracion_horas IS NOT NULL)",
            name="chk_presupuesto_tipo_calculo",
        ),
    )

    id_presupuesto: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha_presupuesto: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_vencimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    fk_ubicacion_trabajo: Mapped[int] = mapped_column(
        ForeignKey(
            "ubicacion_trabajo.id_ubicacion",
            name="fk_presupuesto_ubicacion",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    fk_cliente_contacto: Mapped[int] = mapped_column(
        ForeignKey(
            "clientes_contacto.id_contacto",
            name="fk_presupuesto_cliente_contacto",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    fk_tipo_trabajo: Mapped[int] = mapped_column(
        ForeignKey(
            "tipos_trabajo.id_tipo",
            name="fk_presupuesto_tipo_trabajo",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    descripcion: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tipo_calculo: Mapped[str] = mapped_column(
        SqlEnum("PORCENTAJE", "POR_HORA", name="tipo_calculo"), nullable=False
    )
    costo_porcentaje: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    costo_hora_trabajo: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    duracion_horas: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    estado: Mapped[str] = mapped_column(
        SqlEnum(
            "BORRADOR",
            "PENDIENTE",
            "APROBADO",
            "RECHAZADO",
            "VENCIDO",
            "CANCELADO",
            name="estado_presupuesto",
        ),
        nullable=False,
        default="BORRADOR",
    )

    ubicacion_trabajo: Mapped[UbicacionTrabajoORM] = relationship(back_populates="presupuestos")
    cliente_contacto: Mapped[ClientesContactoORM] = relationship(back_populates="presupuestos")
    tipo_trabajo: Mapped[TipoTrabajoORM] = relationship(back_populates="presupuestos")
    detalles: Mapped[list[DetallePresupuestoORM]] = relationship(
        back_populates="presupuesto", cascade="all, delete-orphan"
    )
    pagos: Mapped[list[PagoORM]] = relationship(back_populates="presupuesto")
    trabajo: Mapped[TrabajoORM | None] = relationship(back_populates="presupuesto", uselist=False)


class ProveedorORM(Base):
    __tablename__ = "proveedores"

    id_proveedor: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    rubro: Mapped[str] = mapped_column(String(100), nullable=False)
    telefono: Mapped[str] = mapped_column(String(20), nullable=False)

    materiales: Mapped[list[MaterialORM]] = relationship(back_populates="proveedor")


class MaterialORM(Base):
    __tablename__ = "materiales"
    __table_args__ = (
        CheckConstraint("precio_unitario >= 0", name="chk_materiales_precio"),
    )

    id_material: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    descripcion: Mapped[str] = mapped_column(String(150), nullable=False)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    fk_proveedor: Mapped[int] = mapped_column(
        ForeignKey(
            "proveedores.id_proveedor",
            name="fk_materiales_proveedor",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        nullable=False,
    )

    proveedor: Mapped[ProveedorORM] = relationship(back_populates="materiales")
    detalles_presupuesto: Mapped[list[DetallePresupuestoORM]] = relationship(back_populates="material")


class DetallePresupuestoORM(Base):
    __tablename__ = "detalle_presupuesto"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="chk_detalle_presupuesto_cantidad"),
        CheckConstraint("precio_unitario >= 0", name="chk_detalle_presupuesto_precio"),
        UniqueConstraint("fk_presupuesto", "fk_material", name="uq_detalle_presupuesto_material"),
    )

    id_detalle: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fk_presupuesto: Mapped[int] = mapped_column(
        ForeignKey(
            "presupuesto.id_presupuesto",
            name="fk_detalle_presupuesto_presupuesto",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    fk_material: Mapped[int] = mapped_column(
        ForeignKey(
            "materiales.id_material",
            name="fk_detalle_presupuesto_material",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    cantidad: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    presupuesto: Mapped[PresupuestoORM] = relationship(back_populates="detalles")
    material: Mapped[MaterialORM] = relationship(back_populates="detalles_presupuesto")


class HistorialClienteORM(Base):
    __tablename__ = "historial_cliente"

    id_historial: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fk_cliente: Mapped[str] = mapped_column(
        String(13),
        ForeignKey(
            "clientes.cuit_cliente",
            name="fk_historial_cliente_cliente",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    fecha: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)

    cliente: Mapped[ClienteORM] = relationship(back_populates="historial")


class PagoORM(Base):
    __tablename__ = "pagos"
    __table_args__ = (
        CheckConstraint("monto > 0", name="chk_pagos_monto"),
    )

    id_pago: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fk_presupuesto: Mapped[int] = mapped_column(
        ForeignKey(
            "presupuesto.id_presupuesto",
            name="fk_pagos_presupuesto",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    fecha_pago: Mapped[date] = mapped_column(Date, nullable=False)
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    metodo_pago: Mapped[str] = mapped_column(String(30), nullable=False)
    referencia: Mapped[str | None] = mapped_column(String(100), nullable=True)

    presupuesto: Mapped[PresupuestoORM] = relationship(back_populates="pagos")


class TrabajoORM(Base):
    __tablename__ = "trabajos"
    __table_args__ = (
        UniqueConstraint("fk_presupuesto", name="uq_trabajos_presupuesto"),
        CheckConstraint(
            "fecha_fin IS NULL OR fecha_inicio IS NULL OR fecha_fin >= fecha_inicio",
            name="chk_trabajos_fechas",
        ),
    )

    id_trabajo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fk_presupuesto: Mapped[int] = mapped_column(
        ForeignKey(
            "presupuesto.id_presupuesto",
            name="fk_trabajos_presupuesto",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    fecha_inicio: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_fin: Mapped[date | None] = mapped_column(Date, nullable=True)
    estado: Mapped[str] = mapped_column(
        SqlEnum("PENDIENTE", "EN_PROCESO", "FINALIZADO", "CANCELADO", name="estado_trabajo"),
        nullable=False,
        default="PENDIENTE",
    )
    observaciones: Mapped[str | None] = mapped_column(String(500), nullable=True)

    presupuesto: Mapped[PresupuestoORM] = relationship(back_populates="trabajo")


class UsuarioORM(Base):
    __tablename__ = "usuarios"
    __table_args__ = (
        UniqueConstraint("usuario", name="uq_usuarios_usuario"),
    )

    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    usuario: Mapped[str] = mapped_column(String(45), nullable=False)
    contrasena_hash: Mapped[str] = mapped_column(String(255), nullable=False)

