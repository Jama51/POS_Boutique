import os
import subprocess
import platform

def limpiar_pantalla():
    """Limpia la terminal según el sistema operativo."""
    os.system('cls' if os.name == 'nt' else 'clear')

def pausar():
    """Realiza una pausa hasta que el usuario presione Enter."""
    input("\nPresiona [Enter] para continuar...")

def abrir_archivo_externo(ruta):
    """Abre un archivo con el programa predeterminado del sistema."""
    if not os.path.exists(ruta):
        print(f"\n  Aviso: El archivo '{ruta}' aún no ha sido generado.")
        print("Asegúrese de realizar al menos una operación que genere este reporte.")
        return

    try:
        if platform.system() == "Windows":
            os.startfile(ruta)
        elif platform.system() == "Darwin": # macOS
            subprocess.call(["open", ruta])
        else: # Linux
            subprocess.call(["xdg-open", ruta])
        print(f" Abriendo {ruta}...")
    except Exception as exception:
        print(f" Error al intentar abrir el archivo: {exception}")