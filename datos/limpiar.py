import sqlite3

def migrar_talla():
    conexion = sqlite3.connect("pos_boutique.db")
    cursor = conexion.cursor()

    try:
        print("Iniciando migración de columna talla...")
        
        # 1. Creamos una tabla temporal con el formato correcto
        cursor.execute("""
            CREATE TABLE Productos_Temporal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(30) NOT NULL,
                talla VARCHAR(10),
                color VARCHAR(15),
                precio FLOAT NOT NULL,
                stock INTEGER NOT NULL,
                activo BOOLEAN DEFAULT 1
            )
        """)

        # 2. Copiamos los datos de la tabla vieja a la nueva
        cursor.execute("""
            INSERT INTO Productos_Temporal (id, nombre, talla, color, precio, stock, activo)
            SELECT id, nombre, talla, color, precio, stock, activo FROM Productos
        """)

        # 3. Borramos la tabla vieja
        cursor.execute("DROP TABLE Productos")

        # 4. Renombramos la temporal a la original
        cursor.execute("ALTER TABLE Productos_Temporal RENAME TO Productos")

        conexion.commit()
        print("✅ ¡Éxito! Ahora puedes guardar tallas como 'XL', 'XXL' o 'UNITALLA'.")
    
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        conexion.rollback()
    finally:
        conexion.close()

if __name__ == "__main__":
    migrar_talla()