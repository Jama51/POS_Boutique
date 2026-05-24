# Importamos lo que ya construimos para no repetir código
from vistas.menu_cajero import mostrar_menu_cajero
from vistas.menu_inventario import mostrar_inventario
from logica.servicio_admin import obtener_total_ventas_dia, actualizar_stock_producto, eliminar_producto_db, registrar_nuevo_producto
from logica.servicio_inventario import obtener_reporte_existencias # <-- NUEVO IMPORT para buscar el nombre
import sys, os

# Aseguramos rutas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utilidades import limpiar_pantalla, pausar, abrir_archivo_externo 

def mostrar_menu_admin(usuario_activo):     
    while True:
        limpiar_pantalla()
        print(f"\n---  PANEL DE ADMINISTRACIÓN | Usuario: {usuario_activo.nombre} ---")
        print("1. Ir a Terminal de Ventas")
        print("2. Gestión de Inventario")
        print("3. Ver Corte de Caja (Rápido)") 
        print("4. Abrir Reporte Detallado (Excel)")
        print("5. Cerrar Sesión")
        
        opcion = input("\n¿Qué desea realizar?: ")
        
        if opcion == "1":
            mostrar_menu_cajero(usuario_activo)
            
        elif opcion == "2":
            limpiar_pantalla()
            mostrar_inventario() 
            
            print("\n---  GESTIÓN DE EXISTENCIAS ---")
            print("1. Agregar Stock (Surtir)")
            print("2. Eliminar Producto permanentemente")
            print("3. Registrar Producto NUEVO") 
            print("4. Volver al menú principal")
            
            sub_opcion = input("\nSelecciona una opción: ")
            
            if sub_opcion == "1":
                try:
                    id_p = int(input("ID del producto a surtir: "))
                    cantidad = int(input("¿Cuántas unidades llegaron?: "))
                    if cantidad > 0:
                        exito = actualizar_stock_producto(id_p, cantidad)
                        if exito:
                            print(f"\n ✅ Stock actualizado con éxito.")
                        else:
                            print("\n ❌ ID no encontrado.")
                    else:
                        print("\n ⚠️ Cantidad inválida.")
                    pausar() 
                except ValueError:
                    print("\n ❌ Error: Ingresa solo números enteros.")
                    pausar()

            elif sub_opcion == "2":
                try:
                    id_p = int(input("\nID del producto a ELIMINAR: "))
                    
                    # --- MEJORA: Buscamos el nombre antes de borrar ---
                    productos_actuales = obtener_reporte_existencias()
                    nombre_producto = None
                    for p in productos_actuales:
                        if p[0] == id_p: # p[0] es el ID, p[1] es el nombre
                            nombre_producto = p[1]
                            break
                            
                    if nombre_producto:
                        confirmar = input(f" ⚠️ ¿Seguro que deseas eliminar '{nombre_producto}' (ID: {id_p})? (s/n): ").lower()
                        if confirmar == 's':
                            exito, nombre_p = eliminar_producto_db(id_p)
                            if exito:
                                print(f"\n ✅ Producto '{nombre_p}' eliminado correctamente.")
                            else:
                                print("\n ❌ No se pudo eliminar de la base de datos.")
                        else:
                            print("\n 🚫 Operación cancelada.")
                    else:
                        print(f"\n ❌ No se encontró ningún producto con el ID {id_p}.")
                    pausar()
                    
                except ValueError:
                    print("\n ❌ Error: Ingresa un ID numérico válido.")
                    pausar()

            elif sub_opcion == "3":
                # --- MEJORA: Tallas permitidas y validación estricta ---
                tallas_permitidas = ['XS', 'S', 'M', 'L', 'XL', 'XXL', '28', '30', '32', '34', '36', '38', '40', 'UNITALLA']
                
                while True:
                    limpiar_pantalla()
                    print("---  REGISTRO DE NUEVO PRODUCTO ---")
                    try:
                        # 1. Limpieza y formateo de texto
                        nombre_crudo = input("Nombre del producto: ").strip()
                        nombre = " ".join(palabra.capitalize() for palabra in nombre_crudo.split())
                        
                        print(f" Tallas válidas: {', '.join(tallas_permitidas[:6])} ... o números (28-40)")
                        talla = input("Talla: ").strip().upper()
                        color = input("Color: ").strip().capitalize()
                        
                        precio = float(input("Precio de venta: "))
                        stock_inicial = int(input("Stock inicial: "))

                        # 2. Reglas de validación
                        if len(nombre) < 3:
                            print("\n ⚠️ El nombre del producto es demasiado corto. Ingresa un nombre válido.")
                        elif not talla or not color:
                            print("\n ⚠️ La talla y el color no pueden estar vacíos.")
                        elif talla not in tallas_permitidas:
                            print(f"\n ⚠️ Talla '{talla}' no reconocida. Por favor use una talla válida.")
                        elif precio < 0 or stock_inicial < 0:
                            print("\n ⚠️ El precio y el stock no pueden ser negativos.")
                        else:
                            exito = registrar_nuevo_producto(nombre, talla, color, precio, stock_inicial)
                            if exito:
                                print(f"\n ✅ '{nombre}' (Talla: {talla}, Color: {color}) registrado con éxito.")
                            else:
                                print("\n ❌ Error al guardar en la base de datos.")
                        
                        # Preguntamos si quiere seguir registrando
                        continuar = input("\n¿Deseas registrar otro producto? (s/n): ").lower()
                        if continuar != 's':
                            break # Rompe el ciclo y vuelve al submenú de gestión
                            
                    except ValueError:
                        print("\n ❌ Error: El precio y stock deben ser números.")
                        pausar()

        elif opcion == "3": 
            limpiar_pantalla()
            total = obtener_total_ventas_dia()
            print("\n" + "="*45)
            print(f" RESUMEN DE VENTAS DEL DÍA: ${total:,.2f}")
            print("="*45)
            print("Este monto refleja el total guardado en la base de datos.")
            pausar() 
            
        elif opcion == "4":
            print("\n Intentando abrir el reporte en Excel...")
            abrir_archivo_externo("Reporte_Ventas_Boutique.xlsx")
            pausar()

        elif opcion == "5":
            print(f"\nSaliendo del panel... ¡Buen día, {usuario_activo.nombre}!")
            break  
            
        else:
            print("\n Opción no válida. Intente de nuevo.")
            pausar()