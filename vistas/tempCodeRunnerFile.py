from logica.servicio_seguridad import validar_credenciales

def iniciar_sesion():
    intentos = 3
    while intentos > 0 : 
        user_intento = str(input("Ingresa el nombre de usuario: "))
        pass_intento = str(input("Ingresa la contraseña: "))
        if validar_credenciales(user_intento, pass_intento) :
            return validar_credenciales
    else:
        intentos -= 1
        print("Intenta de nuevo")