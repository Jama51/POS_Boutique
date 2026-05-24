import sys
import os

# Aseguramos que Python encuentre las carpetas internas
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from vistas.menu_login import iniciar_sesion
from vistas.menu_admin import mostrar_menu_admin
from vistas.menu_cajero import mostrar_menu_cajero

def menu_principal():
    while True:
        usuario_activo = iniciar_sesion()
        if usuario_activo:
            if usuario_activo.rol == "Administrador":
                mostrar_menu_admin(usuario_activo)
            elif usuario_activo.rol == "Cajero":
                mostrar_menu_cajero(usuario_activo)
        else:
            print("\n🔒 Sistema cerrado. ¡Hasta pronto!\n")
            break

if __name__ == "__main__":
    menu_principal()