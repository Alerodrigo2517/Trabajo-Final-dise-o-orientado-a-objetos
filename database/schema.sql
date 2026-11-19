CREATE DATABASE presupuesto_herreria_poo
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE presupuesto_herreria_poo;


CREATE TABLE ciudades (
    id_ciudad INT NOT NULL AUTO_INCREMENT,
    nombre_ciudad VARCHAR(100) NOT NULL,

    CONSTRAINT pk_ciudades
        PRIMARY KEY (id_ciudad),

    -- Agregamos una restricción UNIQUE para evitar que se registre dos veces exactamente la misma ciudad.
    CONSTRAINT uq_ciudades_nombre
        UNIQUE (nombre_ciudad)
);


CREATE TABLE clientes (
    -- Corregimos el nombre "cuilt_cliente" y lo cambiamos por "cuit_cliente".
    -- Acá es una cuestión semántica, más que nada.
    cuit_cliente VARCHAR(13) NOT NULL,
    nombre VARCHAR(45) NOT NULL,
    apellido VARCHAR(45) NOT NULL,

    CONSTRAINT pk_clientes
        PRIMARY KEY (cuit_cliente)
);


CREATE TABLE clientes_contacto (
    id_contacto INT NOT NULL AUTO_INCREMENT,
    fk_cliente VARCHAR(13) NOT NULL,
    direccion VARCHAR(100) NOT NULL,
    fk_ciudad INT NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    fecha_desde DATE NOT NULL,
    fecha_hasta DATE NULL,

    CONSTRAINT pk_clientes_contacto
        PRIMARY KEY (id_contacto),

    CONSTRAINT fk_clientes_contacto_cliente
        FOREIGN KEY (fk_cliente)
        REFERENCES clientes (cuit_cliente)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_clientes_contacto_ciudad
        FOREIGN KEY (fk_ciudad)
        REFERENCES ciudades (id_ciudad)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    -- Agregamos una validación para evitar que la fecha de finalización sea anterior a la fecha de inicio.
    CONSTRAINT chk_clientes_contacto_fechas
        CHECK (
            fecha_hasta IS NULL
            OR fecha_hasta >= fecha_desde
        )
);


CREATE TABLE ubicacion_trabajo (
    id_ubicacion INT NOT NULL AUTO_INCREMENT,
    domicilio VARCHAR(100) NOT NULL,
    fk_ciudad INT NOT NULL,

    CONSTRAINT pk_ubicacion_trabajo
        PRIMARY KEY (id_ubicacion),

    CONSTRAINT fk_ubicacion_trabajo_ciudad
        FOREIGN KEY (fk_ciudad)
        REFERENCES ciudades (id_ciudad)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);


CREATE TABLE tipos_trabajo (
    id_tipo INT NOT NULL AUTO_INCREMENT,
    nombre_tipo VARCHAR(50) NOT NULL,

    CONSTRAINT pk_tipos_trabajo
        PRIMARY KEY (id_tipo),

    CONSTRAINT uq_tipos_trabajo_nombre
        UNIQUE (nombre_tipo)
);


CREATE TABLE presupuesto (
    id_presupuesto INT NOT NULL AUTO_INCREMENT,
    fecha_presupuesto DATE NOT NULL,

    -- Agregamos una fecha de vencimiento para poder controlar hasta cuándo tiene validez el presupuesto.
    fecha_vencimiento DATE NULL,

    fk_ubicacion_trabajo INT NOT NULL,
    fk_cliente_contacto INT NOT NULL,
    fk_tipo_trabajo INT NOT NULL,

    -- Agregamos una descripción general para guardar detalles sobre el trabajo que se está presupuestando.
    descripcion VARCHAR(500) NULL,

    tipo_calculo ENUM(
        'PORCENTAJE',
        'POR_HORA'
    ) NOT NULL,

    costo_porcentaje DECIMAL(5, 2) NULL,
    costo_hora_trabajo DECIMAL(10, 2) NULL,
    duracion_horas DECIMAL(8, 2) NULL,

    -- Agregamos un estado para poder conocer en qué situación se encuentra cada presupuesto.
    estado ENUM(
        'BORRADOR',
        'PENDIENTE',
        'APROBADO',
        'RECHAZADO',
        'VENCIDO',
        'CANCELADO'
    ) NOT NULL DEFAULT 'BORRADOR',

    CONSTRAINT pk_presupuesto
        PRIMARY KEY (id_presupuesto),

    CONSTRAINT fk_presupuesto_ubicacion
        FOREIGN KEY (fk_ubicacion_trabajo)
        REFERENCES ubicacion_trabajo (id_ubicacion)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_presupuesto_cliente_contacto
        FOREIGN KEY (fk_cliente_contacto)
        REFERENCES clientes_contacto (id_contacto)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_presupuesto_tipo_trabajo
        FOREIGN KEY (fk_tipo_trabajo)
        REFERENCES tipos_trabajo (id_tipo)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    -- Evitamos que se puedan guardar porcentajes negativos.
    CONSTRAINT chk_presupuesto_porcentaje
        CHECK (
            costo_porcentaje IS NULL
            OR costo_porcentaje >= 0
        ),

    -- Evitamos que se pueda ingresar un costo por hora negativo.
    CONSTRAINT chk_presupuesto_costo_hora
        CHECK (
            costo_hora_trabajo IS NULL
            OR costo_hora_trabajo >= 0
        ),

    -- Evitamos que la duración estimada tenga un valor negativo.
    CONSTRAINT chk_presupuesto_duracion
        CHECK (
            duracion_horas IS NULL
            OR duracion_horas >= 0
        ),

    -- Agregamos una validación para que la fecha de vencimiento no pueda ser anterior a la fecha del presupuesto.
    CONSTRAINT chk_presupuesto_fechas
        CHECK (
            fecha_vencimiento IS NULL
            OR fecha_vencimiento >= fecha_presupuesto
        ),

    -- Agregamos una validación para que se utilicen solamente los campos correspondientes al tipo de cálculo elegido.
    
    -- A esto te lo explico la clase de hoy. Pero básicamente es para que el usuario no se mande una macana cuando genera los presupuestos.
    -- Si calculamos por porcentaje, usamos costo_porcentaje.
    -- Si calculamos por hora, usamos costo_hora_trabajo y duracion_horas.
    CONSTRAINT chk_presupuesto_tipo_calculo
        CHECK (
            (
                tipo_calculo = 'PORCENTAJE'
                AND costo_porcentaje IS NOT NULL
                AND costo_hora_trabajo IS NULL
                AND duracion_horas IS NULL
            )
            OR
            (
                tipo_calculo = 'POR_HORA'
                AND costo_porcentaje IS NULL
                AND costo_hora_trabajo IS NOT NULL
                AND duracion_horas IS NOT NULL
            )
        )
);


CREATE TABLE proveedores (
    id_proveedor INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    rubro VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,

    CONSTRAINT pk_proveedores
        PRIMARY KEY (id_proveedor)
);


CREATE TABLE materiales (
    id_material INT NOT NULL AUTO_INCREMENT,

    -- Ampliamos la descripción para poder guardar nombres y características más detalladas de los materiales.
    descripcion VARCHAR(150) NOT NULL,

    precio_unitario DECIMAL(12, 2) NOT NULL,
    fk_proveedor INT NOT NULL,

    CONSTRAINT pk_materiales
        PRIMARY KEY (id_material),

    CONSTRAINT fk_materiales_proveedor
        FOREIGN KEY (fk_proveedor)
        REFERENCES proveedores (id_proveedor)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    -- Evitamos que un material pueda tener un precio negativo.
    CONSTRAINT chk_materiales_precio
        CHECK (precio_unitario >= 0)
);


CREATE TABLE detalle_presupuesto (
    id_detalle INT NOT NULL AUTO_INCREMENT,
    fk_presupuesto INT NOT NULL,

    -- Cambiamos "fk_materiales" por "fk_material" porque cada registro hace referencia a un solo material.
    -- Esto es más semántico.
    fk_material INT NOT NULL,

    -- Cambiamos la cantidad de INT a DECIMAL porque algunos materiales pueden medirse en metros, kilos o superficies.
    -- Por ejemplo, podemos utilizar 2.50 metros de caño (Igual fijate en eso, porque yo no manejo mucho cómo es el laburo de herrería).
    cantidad DECIMAL(10, 2) NOT NULL,

    -- Mantenemos el precio unitario dentro del detalle porque representa el precio utilizado al momento de realizar
    -- el presupuesto, aunque después cambiemos el precio del material. A esta modificación me olvidé de hacerla en otros esquemas.
    precio_unitario DECIMAL(12, 2) NOT NULL,

    CONSTRAINT pk_detalle_presupuesto
        PRIMARY KEY (id_detalle),

    CONSTRAINT fk_detalle_presupuesto_presupuesto
        FOREIGN KEY (fk_presupuesto)
        REFERENCES presupuesto (id_presupuesto)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_detalle_presupuesto_material
        FOREIGN KEY (fk_material)
        REFERENCES materiales (id_material)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    -- Evitamos guardar cantidades iguales o menores que cero.
    CONSTRAINT chk_detalle_presupuesto_cantidad
        CHECK (cantidad > 0),

    -- Hacemos el check para no guardar precios negativos.
    CONSTRAINT chk_detalle_presupuesto_precio
        CHECK (precio_unitario >= 0),

    -- Evitamos cargar varias veces el mismo material dentro de un mismo presupuesto.
    -- Para eso, creamos una clave unica con las claves foráneas del presupuesto y del material.
    CONSTRAINT uq_detalle_presupuesto_material
        UNIQUE (fk_presupuesto, fk_material)
);


CREATE TABLE historial_cliente (
    id_historial INT NOT NULL AUTO_INCREMENT,
    fk_cliente VARCHAR(13) NOT NULL,

    -- Cambiamos DATE por DATETIME para poder guardar también la hora exacta en la que se registra cada movimiento.
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Ampliamos la descripción para disponer de más espacio al registrar información en el historial.
    descripcion VARCHAR(500) NOT NULL,

    CONSTRAINT pk_historial_cliente
        PRIMARY KEY (id_historial),

    CONSTRAINT fk_historial_cliente_cliente
        FOREIGN KEY (fk_cliente)
        REFERENCES clientes (cuit_cliente)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);


CREATE TABLE pagos (
    id_pago INT NOT NULL AUTO_INCREMENT,
    fk_presupuesto INT NOT NULL,
    fecha_pago DATE NOT NULL,
    monto DECIMAL(12, 2) NOT NULL,

    -- Hacemos obligatorio el método de pago para no registrar pagos sin conocer cómo fueron realizados.
    metodo_pago VARCHAR(30) NOT NULL,

    -- Agregamos una referencia opcional para guardar un número de operación, comprobante o transferencia.
    -- No es obligatorio, pero sirve para trackear los pagos (principalmente si nos transfirieron por app).
    referencia VARCHAR(100) NULL,

    CONSTRAINT pk_pagos
        PRIMARY KEY (id_pago),

    CONSTRAINT fk_pagos_presupuesto
        FOREIGN KEY (fk_presupuesto)
        REFERENCES presupuesto (id_presupuesto)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    -- Evitamos registrar pagos con valores iguales o menores que cero.
    CONSTRAINT chk_pagos_monto
        CHECK (monto > 0)
);


CREATE TABLE trabajos (
    id_trabajo INT NOT NULL AUTO_INCREMENT,
    fk_presupuesto INT NOT NULL,
    fecha_inicio DATE NULL,
    fecha_fin DATE NULL,

    -- Hacemos obligatorio el estado y dejamos "PENDIENTE" como valor por defecto.
    estado ENUM(
        'PENDIENTE',
        'EN_PROCESO',
        'FINALIZADO',
        'CANCELADO'
    ) NOT NULL DEFAULT 'PENDIENTE',

    -- Agregamos un espacio para guardar observaciones relacionadas con la realización del trabajo.
    -- No es obligatorio, pero es recomendable.
    observaciones VARCHAR(500) NULL,

    CONSTRAINT pk_trabajos
        PRIMARY KEY (id_trabajo),

    CONSTRAINT fk_trabajos_presupuesto
        FOREIGN KEY (fk_presupuesto)
        REFERENCES presupuesto (id_presupuesto)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    -- Evitamos que un mismo presupuesto genere más de un trabajo.
    CONSTRAINT uq_trabajos_presupuesto
        UNIQUE (fk_presupuesto),

    -- Hacemos el check para evitar que la fecha de finalización sea anterior a la fecha de inicio.
    CONSTRAINT chk_trabajos_fechas
        CHECK (
            fecha_fin IS NULL
            OR fecha_inicio IS NULL
            OR fecha_fin >= fecha_inicio
        )
);


CREATE TABLE usuarios (
    id_usuario INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(45) NOT NULL,
    usuario VARCHAR(45) NOT NULL,

    -- La columna existente conserva su nombre físico; Python la expone como contrasena_hash.
    `contraseña` VARCHAR(255) NOT NULL,
    rol ENUM('ADMINISTRADOR', 'OPERADOR', 'AUDITOR')
        NOT NULL DEFAULT 'OPERADOR',

    CONSTRAINT pk_usuarios
        PRIMARY KEY (id_usuario),

    -- Acá tenemos que evitar que existan dos cuentas con el mismo nombre de usuario.
    CONSTRAINT uq_usuarios_usuario
        UNIQUE (usuario)
);

