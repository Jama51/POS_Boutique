import sqlite3
from modelos.empleado import Empleado # <-- Importamos el modelo

def validar_credenciales(usuario_ingresado, password_ingresada):
    conexion = sqlite3.connect("pos_boutique.db")
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT Empleados.id, Empleados.usuario, Empleados.nombre, Rol.nombre 
        FROM Empleados 
        JOIN Rol ON Empleados.rol_id = Rol.id
        WHERE Empleados.usuario = ? AND Empleados.password = ? AND Empleados.activo = 1
    """, (usuario_ingresado, password_ingresada))

    resultado = cursor.fetchone() 
    conexion.close()

    if resultado:
        # Retornamos un Objeto Empleado
        return Empleado( id = resultado[0], usuario = resultado[1], nombre = resultado[2], rol=resultado[3])
    
    return None