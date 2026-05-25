# POS Boutique

## Descripción
POS Boutique es un software de punto de venta para pequeñas tiendas de moda y boutiques. Está diseñado para gestionar ventas, inventario, productos, empleados y reportes desde una interfaz moderna basada en `customtkinter`, con mejoras visuales hechas para un flujo de trabajo más intuitivo.

## Características principales
- Dashboard moderno y responsivo con gráfica de ventas de los últimos 5 días.
- Catálogo visual de inventario con tarjetas de producto en lugar de tablas clásicas.
- Búsqueda y filtrado dinámico del inventario por nombre, ID o talla.
- Vista de ventas con diseño de panel dividido: carrito a la izquierda y resumen de pago a la derecha.
- Generación de tickets de venta y reporte de ventas en Excel.
- Gestión de personal con roles de administrador y cajero.
- Gestión de fotos de producto y stock en tiempo real.
- Modo oscuro compatible con `customtkinter`.

## Estructura del proyecto
- `main.py` — punto de entrada principal.
- `vistas_gui/` — interfaz gráfica principal usando `customtkinter`.
- `vistas/` — menús adicionales y componentes de la aplicación.
- `logica/` — lógica de negocio y funciones de acceso a datos.
- `datos/` — conexión a la base de datos SQLite, limpieza de datos y semillas.
- `modelos/` — definiciones de modelos de datos (productos, empleados).
- `facturas/` — tickets de venta generados.
- `imagenes_productos/` — imágenes de productos usadas en el catálogo.

## Requisitos
- Python 3.10+ (o compatible)
- `customtkinter`
- `Pillow`
- `matplotlib`

## Instalación
1. Clona el repositorio o copia los archivos en un directorio local.
2. Crea y activa un entorno virtual (recomendado):
   - Windows PowerShell:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - Windows CMD:
     ```cmd
     python -m venv .venv
     .\.venv\Scripts\activate
     ```
3. Instala las dependencias necesarias:
   ```powershell
   pip install customtkinter pillow matplotlib
   ```

## Uso básico
1. Asegúrate de tener el entorno virtual activado.
2. Ejecuta la aplicación principal:
   ```powershell
   python main.py
   ```
3. Inicia sesión como administrador o cajero.
4. Navega entre Dashboard, Inventario, Punto de Venta e Historial.

## Notas adicionales
- La base de datos SQLite se conecta a `pos_boutique.db`.
- Las imágenes de producto se almacenan en `imagenes_productos/` con nombres como `prod_<id>.png`.
- Los tickets de ventas se generan en `facturas/`.

## Mejoras incluidas
- Interfaz más visual y moderna usando `customtkinter`.
- Reemplazo de tablas clásicas por tarjeta de productos (`CTkScrollableFrame`).
- Gráfica de barras en el dashboard con diseño oscuro.
- Carrito de ventas limpio y sin bordes, con botón `Pagar` y resumen profesional.
- Ajuste responsive de tarjetas de inventario según el ancho de la ventana.
