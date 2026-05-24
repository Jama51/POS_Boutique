import sqlite3

def obtener_total_ventas_dia():
    try:
        conexion = sqlite3.connect("pos_boutique.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT SUM(total) FROM Venta WHERE date(fecha) = date('now', 'localtime')")
        resultado = cursor.fetchone()[0]
        conexion.close()

        return resultado if resultado else 0.0
    except Exception as e:
        print(f"Error al obtener total de ventas: {e}")
        return 0.0

def actualizar_stock_producto(id_producto, cantidad_agregar):
    try:
        conexion = sqlite3.connect("pos_boutique.db")
        cursor = conexion.cursor()
        
        # Primero verificamos que el producto exista
        cursor.execute("SELECT stock FROM Productos WHERE id = ?", (id_producto,))
        resultado = cursor.fetchone()
        
        if resultado:
            nuevo_stock = resultado[0] + cantidad_agregar
            cursor.execute("UPDATE Productos SET stock = ? WHERE id = ?", (nuevo_stock, id_producto))
            conexion.commit()
            exito = True
        else:
            exito = False
            
        conexion.close()
        return exito
    except Exception as e:
        print(f"Error al actualizar stock: {e}")
        return False

def eliminar_producto_db(id_producto):
    try:
        conexion = sqlite3.connect("pos_boutique.db")
        cursor = conexion.cursor()
        
        # Primero sacamos el nombre para poder avisarle al usuario qué borró
        cursor.execute("SELECT nombre FROM Productos WHERE id = ?", (id_producto,))
        resultado = cursor.fetchone()
        
        if resultado:
            nombre_borrado = resultado[0]
            cursor.execute("DELETE FROM Productos WHERE id = ?", (id_producto,))
            conexion.commit()
            exito = True
        else:
            nombre_borrado = None
            exito = False
            
        conexion.close()
        return exito, nombre_borrado
    except Exception as e:
        print(f"Error al eliminar producto: {e}")
        return False, None

def registrar_nuevo_producto(nombre, talla, color, precio, stock):
    try:
        conexion = sqlite3.connect("pos_boutique.db")
        cursor = conexion.cursor()
        
        cursor.execute('''
            INSERT INTO Productos (nombre, talla, color, precio, stock)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre, talla, color, precio, stock))
        
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print(f"Error al registrar producto: {e}")
        return False
    
    
def modificar_producto_db(id_prod, nombre, talla, color, precio):
    try:
        conexion = sqlite3.connect("pos_boutique.db")
        cursor = conexion.cursor()
        
        cursor.execute('''
            UPDATE Productos 
            SET nombre = ?, talla = ?, color = ?, precio = ?
            WHERE id = ?
        ''', (nombre, talla, color, precio, id_prod))
        
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print(f"Error al modificar producto: {e}")
        return False  
def obtener_empleados():
    try:
        conexion = sqlite3.connect("pos_boutique.db")
        cursor = conexion.cursor()
        # No traemos el password por seguridad, solo lo necesario para la tabla
        cursor.execute("SELECT id, usuario, nombre, rol_id FROM Empleados")
        datos = cursor.fetchall()
        conexion.close()
        return datos
    except Exception as e:
        print(f"Error al obtener empleados: {e}")
        return []

def registrar_empleado(usuario, password, nombre, rol_id):
    try:
        conexion = sqlite3.connect("pos_boutique.db")
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO Empleados (usuario, password, nombre, rol_id, activo)
            VALUES (?, ?, ?, ?, 1)
        """, (usuario, password, nombre, rol_id))
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print(f"Error al registrar empleado (quizá el usuario ya existe): {e}")
        return False

def modificar_empleado(id_emp, usuario, password, nombre, rol_id):
    try:
        conexion = sqlite3.connect("pos_boutique.db")
        cursor = conexion.cursor()
        
        # Si el password viene vacío, significa que no lo quiere cambiar
        if password.strip() == "":
            cursor.execute("""
                UPDATE Empleados SET usuario = ?, nombre = ?, rol_id = ? WHERE id = ?
            """, (usuario, nombre, rol_id, id_emp))
        else:
            cursor.execute("""
                UPDATE Empleados SET usuario = ?, password = ?, nombre = ?, rol_id = ? WHERE id = ?
            """, (usuario, password, nombre, rol_id, id_emp))
            
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print(f"Error al modificar empleado: {e}")
        return False

def eliminar_empleado(id_emp):
    try:
        conexion = sqlite3.connect("pos_boutique.db")
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM Empleados WHERE id = ?", (id_emp,))
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print(f"Error al eliminar empleado: {e}")
        return False
    
def obtener_historial_ventas():
    try:
        conexion = sqlite3.connect("pos_boutique.db")
        cursor = conexion.cursor()
        # Traemos ID, Fecha, Total y el Nombre del Empleado
        cursor.execute("""
            SELECT V.id, V.fecha, V.total, E.nombre 
            FROM Venta V
            JOIN Empleados E ON V.empleado_id = E.id
            ORDER BY V.fecha DESC
        """)
        datos = cursor.fetchall()
        conexion.close()
        return datos
    except Exception as e:
        print(f"Error al obtener historial: {e}")
        return []