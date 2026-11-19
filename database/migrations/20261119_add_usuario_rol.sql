-- Agrega únicamente roles a la tabla usuarios existente de presupuesto_herreria_poo.
-- Las cuentas existentes quedan como OPERADOR por defecto.
ALTER TABLE presupuesto_herreria_poo.usuarios
    ADD COLUMN rol ENUM('ADMINISTRADOR', 'OPERADOR', 'AUDITOR')
        NOT NULL DEFAULT 'OPERADOR'
        AFTER `contraseña`;

-- Después de revisar las cuentas, se puede asignar un primer administrador:
-- UPDATE presupuesto_herreria_poo.usuarios
-- SET rol = 'ADMINISTRADOR'
-- WHERE usuario = 'REEMPLAZAR_USUARIO_ADMIN';
