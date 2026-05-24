import sqlite3

def obtener_reporte_existencias():
    """Trae la lista completa de productos con su stock actual."""
    conexion = sqlite3.connect("pos_boutique.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT id, nombre, talla, color, precio, stock FROM Productos where activo = 1 order by stock ASC
    """)


    productos = cursor.fetchall()
    conexion.close()
    return productos