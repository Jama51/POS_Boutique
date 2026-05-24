from logica.servicio_seguridad import validar_credenciales
import sys
import os

# Configuración de ruta para utilidades
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utilidades import limpiar_pantalla, pausar

def iniciar_sesion():
    intentos = 3
    while intentos > 0:
        limpiar_pantalla() # <-- Empieza con la pantalla vacía
        print("="*40)
        print("      SISTEMA POS-BOUTIQUE")
        print("="*40)
        
        user_intento = input("\n Usuario: ")
        pass_intento = input(" Contraseña: ")
        
        usuario_encontrado = validar_credenciales(user_intento, pass_intento)
        
        if usuario_encontrado:
            limpiar_pantalla() # <-- Limpia para dar la bienvenida
            print(f"\n ¡Bienvenido a POS-Boutique, {usuario_encontrado.nombre}!")
            print(f"Rol detectado: {usuario_encontrado.rol}")
            pausar() 
            return usuario_encontrado
        else:
            intentos -= 1
            print("\n ERROR: Usuario o contraseña incorrectos.")
            print(f"Te quedan {intentos} intentos.")
            pausar() # <-- Pausa para que el usuario lea el error antes de limpiar
            
    limpiar_pantalla()
    print("🔒 Has excedido el límite de intentos. El sistema se cerrará.")
    return None