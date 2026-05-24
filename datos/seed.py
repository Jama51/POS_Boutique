#
import sqlite3

def sembrar_datos():
    conexion = sqlite3.connect("pos_boutique.db")
    cursor = conexion.cursor()

    print("Plantando datos semilla...")

    # 1. Insertar Roles 
    cursor.execute("INSERT OR IGNORE INTO Rol (id, nombre) VALUES (1, 'Administrador')")
    cursor.execute("INSERT OR IGNORE INTO Rol (id, nombre) VALUES (2, 'Cajero')")


    lista_productos = [
        ("Camisa Polo", "M", "Azul", 450.0, 10),
        ("Jeans Slim", "32", "Negro", 750.0, 5),
        ("Chaqueta Cuero", "L", "Café", 1200.0, 2)
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO Productos (nombre, talla, color, precio, stock) 
        VALUES (?, ?, ?, ?, ?)
    """, lista_productos)

 

    lista_empleados = [
        ("admin", "123", "Roberto", 1),
        ("caja1", "abc", "Ana", 2)
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO Empleados (usuario, password, nombre, rol_id) 
        VALUES (?, ?, ?, ?)
    """, lista_empleados)


    # Guardamos y cerramos
    conexion.commit()
    conexion.close()
    print("Datos plantados con éxito. ¡La tienda tiene inventario!")

if __name__ == "__main__":
    sembrar_datos()