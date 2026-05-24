from logica.servicio_inventario import obtener_reporte_existencias
import sys
import os

# Configuración de ruta para utilidades
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utilidades import limpiar_pantalla 

def mostrar_inventario():
    limpiar_pantalla() 
    print("\n" + "="*65)
    print("              REPORTE DE INVENTARIO ACTUAL")
    print("="*65)
    
    productos = obtener_reporte_existencias()
    
    if not productos:
        print(" No hay productos registrados o activos.")
        return

    print(f"{'ID':<4} | {'PRODUCTO':<20} | {'TALLA':<6} | {'COLOR':<10} | {'STOCK':<6}")
    print("-" * 65)

    limite_por_pagina = 10
    
    for i, producto in enumerate(productos):
        id_p, nombre, talla, color, precio, stock = producto
        aviso = " ⚠️ BAJO" if stock <= 3 else ""
        
        print(f"{id_p:<4} | {nombre:<20} | {talla:<6} | {color:<10} | {stock:<6} {aviso}")
        
        # --- LÓGICA DE PAGINACIÓN ---
        if (i + 1) % limite_por_pagina == 0 and (i + 1) < len(productos):
            opcion = input("\n 🔽 Presiona [Enter] para ver más o 'q' para salir: ").lower()
            if opcion == 'q':
                break
            # Si presiona Enter, limpiamos y volvemos a poner los encabezados
            limpiar_pantalla()
            print(f"{'ID':<4} | {'PRODUCTO':<20} | {'TALLA':<6} | {'COLOR':<10} | {'STOCK':<6}")
            print("-" * 65)
    
    print("=" * 65)
    input("\nPresiona Enter para volver al menú...")