# Sistema de Herrería

## Flujo solicitado en las clases

MySQL (tabla usuarios) → Usuario (dataclass) → Login → Sesión de Streamlit

- La cuenta se consulta en MySQL.
- La fila se representa con la entidad inmutable Usuario, separada del modelo ORM.
- El autenticar_usuario comprueba el hash de contraseña con bcrypt.
- La sesión de Streamlit recuerda el usuario, su identificador y su rol; nunca guarda el hash.
- Los permisos se aplican según el rol almacenado en MySQL: Administrador, Operador o Auditor.

## Roles

- Administrador: puede operar el sistema y administrar cuentas y roles.
- Operador: puede crear y actualizar los datos de operación.
- Auditor: puede consultar los datos, sin formularios de escritura.

La tabla usuarios ya existía en el esquema. La única modificación autorizada es agregarle la columna rol con valor inicial OPERADOR. La migración está en database/migrations/20261119_add_usuario_rol.sql. Debe aplicarse una vez cuando MySQL esté disponible. La app no ejecuta cambios de esquema por sí sola.

Las cuentas existentes quedan como OPERADOR al aplicar la migración. Para habilitar el panel Usuarios, hace falta asignar ADMINISTRADOR a una cuenta existente. El administrador puede cambiar roles desde el panel y no puede degradar al último administrador ni quitarse su rol desde su propia sesión.

## Cuenta técnica de MySQL

La cuenta técnica en DB_USER es diferente de los usuarios de la aplicación. database/create_app_user.sql documenta permisos SQL mínimos para la base presupuesto_herreria_poo; es un ejemplo manual y no se ejecuta automáticamente.

## Capas

- app.py: muestra el autenticar_usuario antes de la navegación.
- src/core/: configuración, sesiones, autorización y seguridad.
- src/models/: dataclass de dominio y modelos ORM separados.
- src/repositories/: consultas de persistencia.
- src/services/: autenticación, roles y reglas de negocio.
- src/ui/: interfaz compartida y autenticar_usuario.
- src/pages/: pantallas de gestión y administración de usuarios.
