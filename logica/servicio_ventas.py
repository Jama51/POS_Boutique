import sqlite3
from modelos.producto import Producto

def buscar_producto_por_id(id_producto):
    conexion = sqlite3.connect("pos_boutique.db")
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT id, nombre, talla, color, precio, stock 
        FROM Productos 
        WHERE id = ? AND stock >= 1
    """, [id_producto])
    
    resultado = cursor.fetchone()
    conexion.close()
    
    if resultado:
        return Producto(resultado[0], resultado[1], resultado[2], resultado[3], resultado[4], resultado[5])
    return None

def buscar_producto_por_nombre(nombre_producto):
    conexion = sqlite3.connect("pos_boutique.db")
    cursor = conexion.cursor()
    termino_busqueda = f"%{nombre_producto}%"
    
    cursor.execute("""
        SELECT id, nombre, talla, color, precio, stock 
        FROM Productos 
        WHERE nombre LIKE ? AND stock >= 1
    """, [termino_busqueda])
    
    resultado = cursor.fetchone()
    conexion.close()
    
    if resultado:
        return Producto(resultado[0], resultado[1], resultado[2], resultado[3], resultado[4], resultado[5])
    return None

def guardar_venta(empleado_id, carrito, total):
    conexion = sqlite3.connect("pos_boutique.db")
    cursor = conexion.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    try:
        # 1. Creamos la Venta general
        cursor.execute("""
            INSERT INTO Venta (total, empleado_id)
            VALUES (?, ?)
        """, [total, empleado_id])
        venta_id = cursor.lastrowid
    
        # 2. Agrupamos el carrito antes de insertar (MEJORA CRÍTICA)
        resumen_carrito = {}
        for item in carrito:
            if item.id not in resumen_carrito:
                resumen_carrito[item.id] = {'precio': item.precio, 'cant': 0}
            resumen_carrito[item.id]['cant'] += 1

        # 3. Guardamos detalles y descontamos stock de forma agrupada
        for id_p, info in resumen_carrito.items():
            subtotal_item = info['cant'] * info['precio']
            
            # Guardar el detalle agrupado
            cursor.execute("""
                INSERT INTO Detalle_Venta (venta_id, producto_id, cantidad, subtotal)
                VALUES (?, ?, ?, ?)
            """, [venta_id, id_p, info['cant'], subtotal_item])
            
            # Descontar el stock de golpe
            cursor.execute("""
                UPDATE Productos 
                SET stock = stock - ? 
                WHERE id = ?
            """, [info['cant'], id_p])

        conexion.commit()
        return venta_id
        
    except Exception as e:
        print(f"Error guardando venta: {e}")
        conexion.rollback() # <- Super importante: si falla algo, deshace todo para no dejar datos corruptos
        return None
    finally:
        conexion.close()