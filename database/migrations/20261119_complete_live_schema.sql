-- Migración aditiva de presupuesto_herreria_poo (Antares).
-- Ejecutar una sola vez en Antares. Conserva filas y columnas históricas
-- cuilt_cliente, presupuesto.fk_cliente, detalle_presupuesto.fk_materiales y subtotal.
USE presupuesto_herreria_poo;

CREATE TABLE tipos_trabajo (
    id_tipo INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre_tipo VARCHAR(50) NOT NULL,
    CONSTRAINT uq_tipos_trabajo_nombre UNIQUE (nombre_tipo)
);
INSERT INTO tipos_trabajo (nombre_tipo) VALUES ('Sin especificar');

ALTER TABLE presupuesto
    ADD COLUMN fecha_vencimiento DATE NULL AFTER fecha_presupuesto,
    ADD COLUMN fk_tipo_trabajo INT NULL AFTER fk_cliente_contacto,
    ADD COLUMN descripcion VARCHAR(500) NULL,
    ADD COLUMN estado ENUM('BORRADOR','PENDIENTE','APROBADO','RECHAZADO','VENCIDO','CANCELADO') NOT NULL DEFAULT 'BORRADOR';
UPDATE presupuesto SET fk_tipo_trabajo = 1 WHERE fk_tipo_trabajo IS NULL;
UPDATE presupuesto p JOIN trabajos t ON t.fk_presupuesto = p.id_presupuesto SET p.estado = 'APROBADO';
ALTER TABLE presupuesto
    MODIFY COLUMN fk_tipo_trabajo INT NOT NULL,
    ADD CONSTRAINT fk_presupuesto_tipo_trabajo FOREIGN KEY (fk_tipo_trabajo) REFERENCES tipos_trabajo(id_tipo),
    ADD CONSTRAINT chk_presupuesto_porcentaje CHECK (costo_porcentaje IS NULL OR costo_porcentaje >= 0),
    ADD CONSTRAINT chk_presupuesto_costo_hora CHECK (costo_hora_trabajo IS NULL OR costo_hora_trabajo >= 0),
    ADD CONSTRAINT chk_presupuesto_duracion CHECK (duracion_horas IS NULL OR duracion_horas >= 0),
    ADD CONSTRAINT chk_presupuesto_fechas CHECK (fecha_vencimiento IS NULL OR fecha_vencimiento >= fecha_presupuesto);

ALTER TABLE ciudades
    MODIFY COLUMN nombre_ciudad VARCHAR(100) NOT NULL,
    ADD CONSTRAINT uq_ciudades_nombre UNIQUE (nombre_ciudad);
ALTER TABLE clientes_contacto
    MODIFY COLUMN direccion VARCHAR(100) NOT NULL,
    ADD CONSTRAINT chk_clientes_contacto_fechas CHECK (fecha_hasta IS NULL OR fecha_hasta >= fecha_desde);
ALTER TABLE ubicacion_trabajo MODIFY COLUMN domicilio VARCHAR(100) NOT NULL;

ALTER TABLE detalle_presupuesto
    MODIFY COLUMN cantidad DECIMAL(10,2) NOT NULL,
    MODIFY COLUMN precio_unitario DECIMAL(12,2) NOT NULL,
    ADD CONSTRAINT uq_detalle_presupuesto_material UNIQUE (fk_presupuesto, fk_materiales),
    ADD CONSTRAINT chk_detalle_presupuesto_cantidad CHECK (cantidad > 0),
    ADD CONSTRAINT chk_detalle_presupuesto_precio CHECK (precio_unitario >= 0);
ALTER TABLE materiales
    MODIFY COLUMN precio_unitario DECIMAL(12,2) NOT NULL,
    ADD CONSTRAINT chk_materiales_precio CHECK (precio_unitario >= 0);

ALTER TABLE pagos
    ADD COLUMN referencia VARCHAR(100) NULL,
    MODIFY COLUMN monto DECIMAL(12,2) NOT NULL,
    MODIFY COLUMN metodo_pago VARCHAR(30) NOT NULL,
    ADD CONSTRAINT chk_pagos_monto CHECK (monto > 0);

ALTER TABLE trabajos MODIFY COLUMN estado VARCHAR(30) NULL;
UPDATE trabajos SET estado = CASE LOWER(estado)
    WHEN 'pendiente' THEN 'PENDIENTE'
    WHEN 'en proceso' THEN 'EN_PROCESO'
    WHEN 'finalizado' THEN 'FINALIZADO'
    WHEN 'cancelado' THEN 'CANCELADO'
    ELSE 'PENDIENTE'
END;
ALTER TABLE trabajos
    MODIFY COLUMN estado ENUM('PENDIENTE','EN_PROCESO','FINALIZADO','CANCELADO') NOT NULL DEFAULT 'PENDIENTE',
    ADD COLUMN observaciones VARCHAR(500) NULL,
    ADD CONSTRAINT uq_trabajos_presupuesto UNIQUE (fk_presupuesto),
    ADD CONSTRAINT chk_trabajos_fechas CHECK (fecha_fin IS NULL OR fecha_inicio IS NULL OR fecha_fin >= fecha_inicio);

ALTER TABLE usuarios ADD CONSTRAINT uq_usuarios_usuario UNIQUE (usuario);

