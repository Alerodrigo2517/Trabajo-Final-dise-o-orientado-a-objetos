# Sistema de diseño de la interfaz

## Dirección visual

La aplicación utiliza una estética moderna de **ERP / SaaS industrial de alta precisión**: contraste limpio sobre tonos pizarra (`Slate`), barra lateral en azul obsidiana (`#0f172a`) y acentos ámbar/fragua (`#d97706`) combinados con indicadores semánticos en azul cobalto (`#2563eb`) y verde esmeralda (`#059669`).

## Tokens visuales

| Token | Valor | Uso |
| --- | --- | --- |
| Tinta principal (`--ink`) | `#0f172a` | Títulos, métricas y texto principal |
| Texto secundario (`--ink-secondary`) | `#334155` | Etiquetas de formularios y subtítulos |
| Texto atenuado (`--muted`) | `#64748b` | Ayuda contextual, descripciones y metadatos |
| Acento fragua (`--accent`) | `#d97706` | Botones primarios, indicadores activos y foco |
| Acento hover (`--accent-hover`) | `#b45309` | Estado hover de acciones principales |
| Fondo de aplicación (`--bg-app`) | `#f8fafc` | Lienzo general con destello radial cálido sutil |
| Superficie (`--surface`) | `#ffffff` | Tarjetas KPI, contenedores de formularios y tablas |
| Borde (`--line`) | `#e2e8f0` | Bordes de contenedores, divisores y tablas |
| Barra lateral (`--sidebar-bg`) | `#0f172a` | Navegación lateral persistente |

Tipografía: `Inter` (con fallback a la pila del sistema) y números tabulares (`tabular-nums`) para importes, CUIT y métricas operativas.

## Estructura y componentes clave

- **Pantalla de Login (`src/ui/login.py`):** Vista dividida a pantalla completa (oculta la barra lateral mientras no hay sesión iniciada), con tarjeta de presentación industrial a la izquierda y formulario de autenticación seguro a la derecha.
- **Barra lateral (`app.py` + `render_sidebar_user`):** Identidad de marca con emblema iluminado, tarjeta de usuario activo con avatar de iniciales, indicador luminoso de rol (`Administrador`, `Operador`, `Auditor`) y navegación con estado activo destacado.
- **Encabezado de página (`page_header`):** Tarjeta superior con barra lateral ámbar, etiqueta superior tipo cápsula (`eyebrow`), insignia de módulo (`badge`), título principal y descripción operativa.
- **Tarjetas de indicadores (`kpi_card`):** Tarjetas elevadas con ícono temático (`amber`, `blue`, `emerald`, `slate`), cifra destacada y subtítulo explicativo en todas las páginas del sistema.
- **Encabezados de sección (`section_header`):** Cabeceras internas de contenedor con ícono, título, subtítulo y etiqueta de estado.
- **Tablas con barra de herramientas (`records_table`):** Buscador instantáneo integrado con contador de resultados en cápsula y estados vacíos ilustrados (`empty_state`).
