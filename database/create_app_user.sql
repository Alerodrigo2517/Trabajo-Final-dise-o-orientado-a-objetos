-- Cuenta técnica de la aplicación, separada del usuario que inicia sesión en Streamlit.
-- Reemplazá la contraseña de ejemplo antes de ejecutar este archivo en MySQL.
-- Ejecutar manualmente con una cuenta administradora si decidís crear el usuario.
-- El host 127.0.0.1 debe coincidir con DB_HOST en .env.

CREATE USER IF NOT EXISTS 'herreria_app'@'127.0.0.1'
    IDENTIFIED BY 'REEMPLAZAR_POR_UNA_CLAVE_SEGURA';

GRANT SELECT, INSERT, UPDATE, DELETE
    ON presupuesto_herreria_poo.*
    TO 'herreria_app'@'127.0.0.1';
