from logica.servicio_ventas import buscar_producto_por_id, buscar_producto_por_nombre, guardar_venta
from vistas.menu_inventario import mostrar_inventario
from logica.servicio_reportes import registrar_venta_en_excel, generar_ticket_txt, registrar_devolucion_en_excel
from logica.servicio_admin import actualizar_stock_producto 

import sys
import os

# Aseguramos que Python encuentre utilidades.py en la raíz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utilidades import limpiar_pantalla, pausar

def mostrar_menu_cajero(usuario_activo):
    while True:
        limpiar_pantalla() 
        print(f"\n---   MENÚ CAJA | Cajero: {usuario_activo.nombre} ---")
        print("1. Nueva Venta")
        print("2. Consultar Inventario")
        print("3. Devoluciones")
        print("4. Cerrar Sesión")
        
        opcion = input("\n¿Qué acción deseas realizar?: ")
        
        if opcion == "1":
            limpiar_pantalla()
            print(">>>   TERMINAL DE COBRO ABIERTA <<<")
            carrito = []   
            total = 0.0     
            venta_completada = False # Bandera para saber si cobramos o cancelamos

            while True:
                entrada = input("\nProducto (ID/Nombre) o 'cobrar' (o 'cancelar'): ").strip()
                
                if entrada.lower() == 'cancelar':
                    print("\n🚫 Venta cancelada. Carrito vaciado.")
                    break # Salimos del ciclo while de venta
                    
                elif entrada.lower() == 'cobrar':
                    if not carrito:
                        print("\n⚠️ El carrito está vacío. No hay nada que cobrar.")
                    else:
                        venta_completada = True # Marcamos que sí se va a cobrar
                        break # Salimos del ciclo while de venta
                
                else:
                    # Lógica de búsqueda
                    producto = None
                    if entrada.isdigit():
                        producto = buscar_producto_por_id(int(entrada))
                    else:
                        producto = buscar_producto_por_nombre(entrada)
                        
                    if producto:
                        print(f"\n Encontrado: {producto.nombre} (Talla: {producto.talla}, Color: {producto.color}) - ${producto.precio:.2f}")
                        print(f" Stock disponible: {producto.stock}")
                        
                        try:
                            # Calculamos cuántas unidades de ESTE producto ya están en el carrito
                            cantidad_en_carrito = sum(1 for item in carrito if item.id == producto.id)
                            stock_real_disponible = producto.stock - cantidad_en_carrito
                            
                            if stock_real_disponible <= 0:
                                print(f" ⚠️ No puedes agregar más '{producto.nombre}'. Te acabaste el stock disponible ({producto.stock}).")
                                continue
                                
                            cantidad = int(input("¿Cantidad a llevar?: "))
                            
                            if cantidad <= 0:
                                print(" ⚠️ La cantidad debe ser mayor a cero.")
                            elif cantidad > stock_real_disponible:
                                print(f" ⚠️ Stock insuficiente. Solo puedes llevar {stock_real_disponible} unidades más de este artículo.")
                            else:
                                for _ in range(cantidad):
                                    carrito.append(producto)
                                total += (producto.precio * cantidad)
                                print(f" ✅ {cantidad}x {producto.nombre} agregado(s). Total actual: ${total:.2f}")
                        except ValueError:
                            print(" ❌ Error: Ingresa un número válido para la cantidad.")
                    else:
                        print(" ❌ Producto no encontrado o sin stock. Verifica el ID o Nombre.")

            # --- FUERA DEL CICLO WHILE: Procedemos al cobro SOLO si la bandera está activada ---
            if venta_completada and carrito:
                print("\n" + "="*40)
                print(f" TOTAL A COBRAR: ${total:.2f}")
                print("="*40)
                confirmacion = input("¿Confirmar pago? (s/n): ").lower()
                
                if confirmacion == 's':
                    folio_venta = guardar_venta(usuario_activo.id, carrito, total)
                    
                    if folio_venta:
                        print(f"\n ✅ Venta guardada con Folio: {folio_venta}")
                        generar_ticket_txt(folio_venta, total, 0.0, total, usuario_activo.nombre, "Efectivo", total, carrito)
                        registrar_venta_en_excel(folio_venta, total, 0.0, total, usuario_activo.nombre, "Efectivo", carrito)
                    else:
                        print("\n ❌ Error crítico al guardar la venta en la base de datos.")
                else:
                    print("\n 🚫 Pago cancelado.")
            
            pausar()

        elif opcion == "2":
            mostrar_inventario()

        elif opcion == "3":
            limpiar_pantalla()
            print("---   PROCESO DE DEVOLUCIÓN   ---")
            try:
                id_dev = int(input("\nID del producto a devolver: "))
                producto_dev = buscar_producto_por_id(id_dev)
                
                if not producto_dev: # Si no lo encuentra por ID, probamos buscar si el stock era 0 y no salía en la búsqueda normal
                    import sqlite3
                    from modelos.producto import Producto
                    conexion = sqlite3.connect("pos_boutique.db")
                    cursor = conexion.cursor()
                    cursor.execute("SELECT id, nombre, talla, color, precio, stock FROM Productos WHERE id = ?", [id_dev])
                    res = cursor.fetchone()
                    conexion.close()
                    if res:
                        producto_dev = Producto(res[0], res[1], res[2], res[3], res[4], res[5])
                
                if producto_dev:
                    print(f"\n📦 Devolviendo: {producto_dev.nombre}")
                    print(f"💰 Precio a reembolsar: ${producto_dev.precio:.2f}")
                    
                    confirmar = input("\n¿Confirmar devolución y regresar dinero? (s/n): ").lower()
                    
                    if confirmar == 's':
                        exito = actualizar_stock_producto(producto_dev.id, 1)
                        
                        if exito:
                            registrar_devolucion_en_excel(usuario_activo.nombre, producto_dev)
                            print("\n✅ DEVOLUCIÓN EXITOSA.")
                            print(f"💵 Por favor, entrega ${producto_dev.precio:.2f} en efectivo al cliente.")
                            print("📦 El artículo ha sido devuelto al inventario.")
                        else:
                            print("\n❌ Error al actualizar el inventario.")
                    else:
                        print("\n🚫 Devolución cancelada.")
                else:
                    print("\n❌ Producto no encontrado en el sistema.")
            except ValueError:
                print("\n❌ Error: Ingresa un ID numérico válido.")
                
            pausar()

        elif opcion == "4":
            print(f"\n >> ¡Hasta pronto, {usuario_activo.nombre}!")
            break 
            
        else:
            print("\n  Opción no reconocida.")
            pausar()