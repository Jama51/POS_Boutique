import openpyxl
from datetime import datetime
import os

def registrar_venta_en_excel(folio, total, nombre_cajero, carrito):
    ruta = "Reporte_Ventas_Boutique.xlsx"
    
    try:
        if not os.path.exists(ruta):
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Registro de Ventas"
            ws.append(["Folio", "Fecha y Hora", "Cajero", "Total ($)", "Detalle de Productos"])
        else:
            wb = openpyxl.load_workbook(ruta)
            ws = wb.active

        # Creamos un resumen de los productos para el Excel (ej: "2x Camisa, 1x Pantalón")
        # Primero agrupamos por nombre
        resumen_dict = {}
        for item in carrito:
            resumen_dict[item.nombre] = resumen_dict.get(item.nombre, 0) + 1
        
        # Lo convertimos a texto: "2x Camisa Polo, 1x Jeans"
        detalle_texto = ", ".join([f"{cant}x {nombre}" for nombre, cant in resumen_dict.items()])

        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        ws.append([folio, fecha, nombre_cajero, total, detalle_texto])
        
        wb.save(ruta)
        print(" 📊 Registro en Excel actualizado.")
        
        # --- AÑADIDO: Avisamos a la GUI que todo salió bien ---
        return True 

    except PermissionError:
        print("\n ⚠️ ¡ERROR DE PERMISO!")
        print(" No se pudo actualizar el Excel porque el archivo está ABIERTO.")
        print(" Por favor, ciérrelo para que las próximas ventas se registren correctamente.")
        
        # --- AÑADIDO: Avisamos a la GUI que falló por permiso ---
        return False 
        
    except Exception as e:
        print(f" ❌ Error inesperado en Excel: {e}")
        return False


def generar_ticket_txt(folio, total, nombre_cajero, carrito):
    if not os.path.exists("facturas"):
        os.makedirs("facturas")
        
    ruta_ticket = f"facturas/ticket_{folio}.txt"
    
    # Agrupamos productos para que el ticket no sea una lista infinita
    resumen_dict = {}
    for item in carrito:
        if item.id not in resumen_dict:
            resumen_dict[item.id] = {"nombre": item.nombre, "precio": item.precio, "cant": 0}
        resumen_dict[item.id]["cant"] += 1

    try:
        with open(ruta_ticket, "w", encoding="utf-8") as f:
            f.write("==============================\n")
            f.write("       POS BOUTIQUE ZAMORA    \n")
            f.write("==============================\n")
            f.write(f"Folio: #{folio}\n")
            f.write(f"Cajero: {nombre_cajero}\n")
            f.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write("------------------------------\n")
            
            for id_p, info in resumen_dict.items():
                subtotal_item = info['cant'] * info['precio']
                linea = f"{info['cant']}x {info['nombre'][:15]}"
                f.write(f"{linea:<20} ${subtotal_item:>8.2f}\n")
                
            f.write("------------------------------\n")
            f.write(f"TOTAL:              ${total:>8.2f}\n")
            f.write("==============================\n")
            f.write("   ¡Gracias por su compra!    \n")
        print(f" 🧾 Ticket generado: {ruta_ticket}")
    except Exception as e:
        print(f" ❌ Error al generar ticket TXT: {e}")


def registrar_devolucion_en_excel(nombre_cajero, producto):
    ruta = "Reporte_Ventas_Boutique.xlsx"
    if not os.path.exists(ruta):
        return False # Si no hay archivo, no hacemos nada
        
    try:
        wb = openpyxl.load_workbook(ruta)
        ws = wb.active
        
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        # Registramos como DEV, monto negativo, y el detalle
        ws.append(["DEV", fecha, nombre_cajero, -producto.precio, f"DEVOLUCIÓN: 1x {producto.nombre}"])
        
        wb.save(ruta)
        return True
    except PermissionError:
        print("\n ⚠️ No se pudo registrar la devolución en Excel (Archivo abierto).")
        return False
    except Exception as e:
        print(f"\n ❌ Error en Excel: {e}")
        return False    