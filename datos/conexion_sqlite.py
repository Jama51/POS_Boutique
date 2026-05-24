import sqlite3

def inicializar_base_datos():
    conexion = sqlite3.connect("pos_boutique.db")
    cursor = conexion.cursor()

    print("Construcción de base de datos ...")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Rol(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre VARCHAR(30) UNIQUE NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Productos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre VARCHAR(30) NOT NULL,
        talla CHAR(1),
        color VARCHAR(15),
        precio FLOAT NOT NULL,
        stock INTEGER NOT NULL,
        activo BOOLEAN DEFAULT 1
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Empleados(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario VARCHAR(20) UNIQUE NOT NULL,    
        password VARCHAR(15) NOT NULL,
        nombre VARCHAR(20) NOT NULL,
        rol_id INTEGER NOT NULL,
        activo BOOLEAN DEFAULT 1,
        FOREIGN KEY (rol_id) REFERENCES Rol(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Venta(
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
        total FLOAT NOT NULL,
        empleado_id INTEGER NOT NULL,
        FOREIGN KEY (empleado_id) REFERENCES Empleados(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Detalle_Venta(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venta_id INTEGER NOT NULL,
        producto_id INTEGER NOT NULL,
        cantidad INTEGER NOT NULL, 
        subtotal FLOAT NOT NULL,
        FOREIGN KEY (venta_id) REFERENCES Venta(id), 
        FOREIGN KEY (producto_id) REFERENCES Productos(id)
    );
    """)

    conexion.commit()
    conexion.close()
    print("Base de datos construida con éxito.")

if __name__ == "__main__":
    inicializar_base_datos()