# 🛍️ POS Boutique — Sistema de Punto de Venta

## Descripción

**POS Boutique** es un sistema de punto de venta completo desarrollado en Python, diseñado específicamente para pequeñas tiendas de moda y boutiques. El sistema permite gestionar el ciclo completo de ventas, inventario, personal y reportes financieros a través de dos interfaces: una **interfaz de consola (CLI)** para operaciones rápidas en terminal y una **interfaz gráfica moderna (GUI)** construida con `customtkinter`, que ofrece un dashboard visual con gráficas, catálogo de productos con tarjetas y un punto de venta intuitivo con carrito de compras.

El sistema utiliza **SQLite** como motor de base de datos embebida y genera reportes automáticos en **Excel (.xlsx)** y **tickets de venta en texto plano (.txt)** listos para impresión térmica.

---

## Características Técnicas

| Característica | Detalle |
|---|---|
| **Lenguaje** | Python 3.10+ |
| **Base de datos** | SQLite 3 (embebida, archivo `pos_boutique.db`) |
| **GUI** | `customtkinter` con soporte de modo oscuro/claro |
| **Gráficas** | `matplotlib` integrado con `TkAgg` backend |
| **Imágenes** | `Pillow (PIL)` para carga y redimensionamiento de fotos de producto |
| **Reportes Excel** | `openpyxl` para generación y lectura de archivos `.xlsx` |
| **Tickets** | Archivos `.txt` con formato de recibo para impresión térmica |
| **Arquitectura** | Capas separadas: Presentación → Lógica → Datos → Modelos |
| **Compatibilidad** | Windows, macOS, Linux (apertura de archivos multiplataforma) |

---

## Arquitectura del Sistema

El proyecto sigue una arquitectura de **4 capas** que separa responsabilidades:

```
┌─────────────────────────────────────────────────────────┐
│                  CAPA DE PRESENTACIÓN                   │
│                                                         │
│   vistas/          (CLI - Menús en terminal)            │
│   vistas_gui/      (GUI - Interfaz customtkinter)       │
├─────────────────────────────────────────────────────────┤
│                  CAPA DE LÓGICA DE NEGOCIO              │
│                                                         │
│   logica/          (Servicios: ventas, inventario,      │
│                     seguridad, administración, reportes) │
├─────────────────────────────────────────────────────────┤
│                  CAPA DE DATOS                          │
│                                                         │
│   datos/           (Conexión SQLite, seeds, migraciones)│
├─────────────────────────────────────────────────────────┤
│                  CAPA DE MODELOS                        │
│                                                         │
│   modelos/         (Clases: Producto, Empleado)         │
└─────────────────────────────────────────────────────────┘
```

### Flujo de dependencias

```
main.py
  ├── vistas/menu_login.py ──► logica/servicio_seguridad.py ──► modelos/empleado.py
  │     │                                                        datos/pos_boutique.db
  │     ├── vistas/menu_admin.py ──► logica/servicio_admin.py
  │     │     │                      logica/servicio_inventario.py
  │     │     └── vistas/menu_cajero.py
  │     │
  │     └── vistas/menu_cajero.py ──► logica/servicio_ventas.py ──► modelos/producto.py
  │                                   logica/servicio_reportes.py    datos/pos_boutique.db
  │
  └── vistas_gui/login_gui.py ──► vistas_gui/main_gui.py (Dashboard, Inventario,
                                    Punto de Venta, Historial, Personal, Reportes)
```

---

## Esquema de Base de Datos

La base de datos `pos_boutique.db` contiene **5 tablas** con las siguientes relaciones:

### Diagrama Entidad-Relación

```
┌──────────────┐       ┌──────────────────┐       ┌────────────────────┐
│     Rol      │       │    Empleados     │       │       Venta        │
├──────────────┤       ├──────────────────┤       ├────────────────────┤
│ id      PK   │◄──FK──│ id          PK   │◄──FK──│ id            PK   │
│ nombre       │       │ usuario   UNIQUE │       │ fecha    DATETIME  │
└──────────────┘       │ password         │       │ total       FLOAT  │
                       │ nombre           │       │ empleado_id    FK  │
                       │ rol_id       FK  │       └────────┬───────────┘
                       │ activo   BOOLEAN │                │
                       └──────────────────┘                │
                                                           │
┌──────────────────┐       ┌─────────────────────┐         │
│   Productos      │       │   Detalle_Venta     │         │
├──────────────────┤       ├─────────────────────┤         │
│ id          PK   │◄──FK──│ id             PK   │         │
│ nombre           │       │ venta_id        FK  │────FK───┘
│ talla VARCHAR(10)│       │ producto_id     FK  │
│ color            │       │ cantidad     INT    │
│ precio     FLOAT │       │ subtotal     FLOAT  │
│ stock       INT  │       └─────────────────────┘
│ activo   BOOLEAN │
└──────────────────┘
```

### Detalle de Tablas

#### `Rol`
| Columna | Tipo | Restricción | Descripción |
|---------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador único |
| `nombre` | VARCHAR(30) | UNIQUE NOT NULL | Nombre del rol (`Administrador`, `Cajero`) |

#### `Empleados`
| Columna | Tipo | Restricción | Descripción |
|---------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador único |
| `usuario` | VARCHAR(20) | UNIQUE NOT NULL | Nombre de usuario para login |
| `password` | VARCHAR(15) | NOT NULL | Contraseña de acceso |
| `nombre` | VARCHAR(20) | NOT NULL | Nombre real del empleado |
| `rol_id` | INTEGER | FOREIGN KEY → Rol(id) | Rol asignado |
| `activo` | BOOLEAN | DEFAULT 1 | Soft-delete (1 = activo, 0 = inactivo) |

#### `Productos`
| Columna | Tipo | Restricción | Descripción |
|---------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador único |
| `nombre` | VARCHAR(30) | NOT NULL | Nombre del producto |
| `talla` | VARCHAR(10) | — | Talla (XS, S, M, L, XL, XXL, 28-40, UNITALLA) |
| `color` | VARCHAR(15) | — | Color del producto |
| `precio` | FLOAT | NOT NULL | Precio de venta |
| `stock` | INTEGER | NOT NULL | Unidades disponibles |
| `activo` | BOOLEAN | DEFAULT 1 | Soft-delete (1 = activo, 0 = inactivo) |

#### `Venta`
| Columna | Tipo | Restricción | Descripción |
|---------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Folio de venta (secuencial) |
| `fecha` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Fecha y hora de la transacción |
| `total` | FLOAT | NOT NULL | Monto total de la venta |
| `empleado_id` | INTEGER | FOREIGN KEY → Empleados(id) | Cajero que realizó la venta |

#### `Detalle_Venta`
| Columna | Tipo | Restricción | Descripción |
|---------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador del detalle |
| `venta_id` | INTEGER | FOREIGN KEY → Venta(id) | Venta a la que pertenece |
| `producto_id` | INTEGER | FOREIGN KEY → Productos(id) | Producto vendido |
| `cantidad` | INTEGER | NOT NULL | Cantidad vendida |
| `subtotal` | FLOAT | NOT NULL | Subtotal (cantidad × precio) |

---

## Estructura del Proyecto

```
POS_Boutique/
│
├── main.py                          # Punto de entrada (CLI): login → menú según rol
├── utilidades.py                    # Helpers: limpiar_pantalla(), pausar(), abrir_archivo_externo()
├── pos_boutique.db                  # Base de datos SQLite (se genera automáticamente)
├── Reporte_Ventas_Boutique.xlsx     # Reporte de ventas generado en Excel
│
├── datos/                           # Capa de Datos
│   ├── __init__.py
│   ├── conexion_sqlite.py           # Inicialización de BD: crea las 5 tablas si no existen
│   ├── seed.py                      # Datos semilla: roles, productos y empleados de ejemplo
│   └── limpiar.py                   # Migración: cambia talla de CHAR(1) a VARCHAR(10)
│
├── modelos/                         # Capa de Modelos (POO)
│   ├── __init__.py
│   ├── empleado.py                  # Clase Empleado(id, usuario, nombre, rol)
│   └── producto.py                  # Clase Producto(id, nombre, talla, color, precio, stock)
│
├── logica/                          # Capa de Lógica de Negocio
│   ├── __init__.py
│   ├── servicio_seguridad.py        # Validación de credenciales con JOIN Rol
│   ├── servicio_ventas.py           # Búsqueda de productos, guardado de ventas con descuento de stock
│   ├── servicio_inventario.py       # Consulta de existencias activas ordenadas por stock
│   ├── servicio_admin.py            # Dashboard, CRUD de productos, CRUD de empleados, historial
│   └── servicio_reportes.py         # Generación de tickets TXT y registros en Excel
│
├── vistas/                          # Capa de Presentación (CLI)
│   ├── __init__.py
│   ├── menu_login.py                # Login por consola con 3 intentos
│   ├── menu_admin.py                # Panel admin: ventas, inventario, corte de caja, reportes
│   ├── menu_cajero.py               # Panel cajero: nueva venta, inventario, devoluciones
│   └── menu_inventario.py           # Tabla de inventario paginada en terminal
│
├── vistas_gui/                      # Capa de Presentación (GUI - customtkinter)
│   ├── login_gui.py                 # Ventana de login con diseño de tarjeta y switch de tema
│   └── main_gui.py                  # Ventana principal: Dashboard, Inventario, POS, Historial, Personal
│
├── facturas/                        # Tickets de venta generados (ticket_<folio>.txt)
│
└── imagenes_productos/              # Fotos de productos (prod_<id>.png)
```

### Descripción de Archivos Clave

| Archivo | Responsabilidad |
|---------|----------------|
| `main.py` | Punto de entrada CLI. Ejecuta el ciclo login → menú admin/cajero → cierre de sesión |
| `utilidades.py` | Funciones utilitarias multiplataforma: limpiar terminal (`cls`/`clear`), pausar ejecución y abrir archivos con el programa predeterminado del SO |
| `datos/conexion_sqlite.py` | Crea las tablas `Rol`, `Productos`, `Empleados`, `Venta` y `Detalle_Venta` usando `CREATE TABLE IF NOT EXISTS` |
| `datos/seed.py` | Inserta datos iniciales: 2 roles, 3 productos de ejemplo y 2 empleados (admin/cajero) con `INSERT OR IGNORE` |
| `datos/limpiar.py` | Migración de esquema: recrea la tabla `Productos` cambiando la columna `talla` de `CHAR(1)` a `VARCHAR(10)` para soportar tallas alfanuméricas (XL, XXL, UNITALLA, etc.) |
| `logica/servicio_seguridad.py` | Valida credenciales contra la BD con JOIN a la tabla `Rol`; retorna un objeto `Empleado` o `None` |
| `logica/servicio_ventas.py` | Búsqueda de productos por ID o nombre (con `LIKE`), guardado transaccional de ventas con agrupación de carrito y descuento de stock atómico con rollback |
| `logica/servicio_admin.py` | Consultas de dashboard (ventas del día, producto más vendido, stock bajo, ventas últimos 5 días), CRUD completo de productos y empleados, historial de ventas |
| `logica/servicio_reportes.py` | Genera tickets `.txt` con formato de recibo y registra cada venta/devolución en `Reporte_Ventas_Boutique.xlsx` |
| `logica/servicio_inventario.py` | Consulta de productos activos ordenados por stock ascendente |
| `vistas_gui/login_gui.py` | Ventana de login con `customtkinter`: diseño de tarjeta, campos estilizados, soporte de tecla Enter y switch de modo oscuro/claro |
| `vistas_gui/main_gui.py` | Ventana principal GUI (~1450 líneas): sidebar con navegación, dashboard con tarjetas KPI y gráfica de barras, catálogo visual con tarjetas de producto, punto de venta con carrito, historial de ventas y gestión de personal (solo admin) |

---

## Requisitos

- **Python** 3.10 o superior
- **customtkinter** — Framework de interfaz gráfica moderna basada en Tkinter
- **Pillow** — Manejo de imágenes de productos
- **matplotlib** — Gráficas de ventas en el dashboard
- **openpyxl** — Lectura y escritura de archivos Excel (.xlsx)

> **Nota:** `sqlite3`, `tkinter`, `os`, `sys`, `subprocess`, `platform` y `datetime` son módulos de la biblioteca estándar de Python y no requieren instalación adicional.

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Jama51/POS_Boutique.git
cd POS_Boutique
```

### 2. Crear y activar un entorno virtual (recomendado)

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv .venv
.\.venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install customtkinter pillow matplotlib openpyxl
```

### 4. Inicializar la base de datos (primera vez)

```bash
python datos/conexion_sqlite.py
python datos/seed.py
```

Esto creará el archivo `pos_boutique.db` con las tablas necesarias y los datos iniciales de ejemplo.

### 5. (Opcional) Migrar columna de tallas

Si la base de datos fue creada con una versión anterior donde `talla` era `CHAR(1)`:

```bash
python datos/limpiar.py
```

---

## Uso

### Interfaz de Consola (CLI)

```bash
python main.py
```

### Interfaz Gráfica (GUI)

```bash
cd vistas_gui
python login_gui.py
```

### Credenciales de prueba

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| `admin` | `123` | Administrador |
| `caja1` | `abc` | Cajero |

---

## Flujo de Trabajo del Sistema

```
                        ┌──────────────┐
                        │    LOGIN     │
                        │  (3 intentos)│
                        └──────┬───────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
             ┌──────▼──────┐       ┌──────▼──────┐
             │   ADMIN     │       │   CAJERO    │
             │   PANEL     │       │    PANEL    │
             └──────┬──────┘       └──────┬──────┘
                    │                     │
       ┌────────────┼────────────┐        ├── Nueva Venta
       │            │            │        │     ├── Buscar producto (ID/Nombre)
       │            │            │        │     ├── Agregar al carrito
  ┌────▼────┐ ┌─────▼─────┐ ┌───▼───┐    │     ├── Cobrar → Guardar venta
  │Terminal │ │ Gestión   │ │Corte  │    │     ├── Generar ticket .txt
  │de Ventas│ │Inventario │ │ Caja  │    │     └── Registrar en Excel
  │(=Cajero)│ │           │ │       │    │
  └─────────┘ ├── Surtir  │ └───────┘    ├── Consultar Inventario
              ├── Eliminar│              │
              ├── Registrar│              ├── Devoluciones
              │   Nuevo    │              │     ├── Devolver stock
              └────────────┘              │     └── Registrar en Excel
                    │                     │
              ┌─────▼─────┐              └── Cerrar Sesión
              │ Reporte   │
              │ Excel     │
              └───────────┘
```

---

## Funcionalidades por Rol

### 👨‍💼 Administrador

| Función | Descripción |
|---------|-------------|
| **Terminal de Ventas** | Acceso completo al módulo de caja (igual que el cajero) |
| **Gestión de Inventario** | Surtir stock, eliminar productos permanentemente, registrar productos nuevos con validación de tallas |
| **Corte de Caja** | Consulta rápida del total de ventas del día desde la BD |
| **Reporte Excel** | Abrir el archivo `Reporte_Ventas_Boutique.xlsx` con el programa predeterminado del SO |
| **Dashboard (GUI)** | Tarjetas KPI (ventas del día, producto más vendido, artículos con stock bajo) y gráfica de barras de ventas de los últimos 5 días |
| **Gestión de Personal (GUI)** | CRUD completo de empleados: registrar, modificar (usuario, contraseña, nombre, rol), eliminar |
| **Historial de Ventas (GUI)** | Tabla con todas las ventas realizadas (folio, fecha, total, cajero) |

### 🧑‍💻 Cajero

| Función | Descripción |
|---------|-------------|
| **Nueva Venta** | Buscar productos por ID o nombre, agregar al carrito con validación de stock en tiempo real, cobrar con confirmación |
| **Consultar Inventario** | Ver tabla paginada de productos activos con alerta de stock bajo (≤ 3 unidades) |
| **Devoluciones** | Devolver producto por ID, reintegrar stock y registrar la devolución en Excel con monto negativo |
| **Dashboard (GUI)** | Vista limitada sin opciones de administración |

---

## Notas Técnicas

### Base de Datos
- La conexión a SQLite se realiza de forma directa en cada función de servicio (sin ORM ni pool de conexiones).
- Las ventas se guardan de forma **transaccional**: si falla algún paso (insertar venta, detalles o descontar stock), se ejecuta `rollback()` para evitar inconsistencias.
- Se utiliza `PRAGMA foreign_keys = ON` en el servicio de ventas para garantizar la integridad referencial.
- Los productos y empleados implementan **soft-delete** mediante el campo `activo` (BOOLEAN).

### Reportes
- El archivo Excel `Reporte_Ventas_Boutique.xlsx` se crea automáticamente con la primera venta si no existe.
- Cada venta agrega una fila con: Folio, Fecha, Cajero, Método de Pago, Subtotal, Descuento, Total y Detalle de productos.
- Las devoluciones se registran como filas con folio `DEV` y monto negativo.
- Los tickets `.txt` se generan en `facturas/ticket_<folio>.txt` con formato listo para impresión térmica (32 columnas).

### Interfaz Gráfica (GUI)
- Construida con `customtkinter` con diseño de panel lateral (sidebar) para navegación.
- Soporte completo de **modo oscuro y claro** con switch en tiempo real.
- El catálogo de inventario usa **tarjetas de producto** (`CTkScrollableFrame`) en lugar de tablas, con ajuste responsive según el ancho de la ventana.
- Las gráficas de ventas utilizan `matplotlib` con backend `TkAgg` y estilo oscuro personalizado.
- Las fotos de productos se cargan desde `imagenes_productos/prod_<id>.png` usando `Pillow`.

### Seguridad
- Autenticación por usuario y contraseña contra la tabla `Empleados` con JOIN al `Rol`.
- Login limitado a **3 intentos** (CLI) antes de bloquear el acceso.
- Las contraseñas se almacenan en texto plano en la BD (adecuado para entornos educativos/demostrativos).

---

## Mejoras Incluidas

- Interfaz gráfica moderna con `customtkinter` y diseño responsive.
- Catálogo visual con tarjetas de producto en lugar de tablas clásicas.
- Dashboard con tarjetas KPI y gráfica de barras de ventas recientes.
- Carrito de ventas con diseño limpio, botón de pago y resumen profesional.
- Validación estricta de tallas permitidas al registrar productos.
- Paginación en la vista de inventario por terminal.
- Proceso de devoluciones con reintegro de stock y registro en Excel.
- Generación automática de tickets con formato de recibo para impresión térmica.

---

## Licencia

Este proyecto es de uso educativo y demostrativo.
