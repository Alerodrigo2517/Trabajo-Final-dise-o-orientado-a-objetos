# Sistema de Herrería

- `app.py`: inicio y menú para navegar por la aplicación.
- `database/schema.sql`: tablas de la base de datos.
- `database/migrations/`: cambios futuros en las tablas.
- `src/core/`: conexión a la base de datos y funciones comunes.
- `src/models/`: clases que representan los datos del sistema.
- `src/repositories/`: consultas para guardar y buscar información.
- `src/services/`: reglas y cálculos del sistema.
- `src/pages/`: pantallas de Streamlit.

La pantalla de clientes guarda los datos solo mientras la aplicación está abierta. Todavía falta conectarla con MySQL.
