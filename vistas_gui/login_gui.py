import customtkinter as ctk
from tkinter import messagebox
import sys
import os

# Importamos la ventana principal que definimos en main_gui.py
from main_gui import VentanaPrincipal

# Aseguramos que Python encuentre tus módulos lógicos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logica.servicio_seguridad import validar_credenciales

def iniciar_app():
    # 1. Configuración base
    ctk.set_appearance_mode("dark")  
    ctk.set_default_color_theme("dark-blue")  

    app = ctk.CTk()
    app.geometry("450x600")
    app.title("POS Boutique - Ingreso Seguro")
    app.resizable(False, False) 
    
    # Centramos todo el contenido usando grid weights
    app.grid_columnconfigure(0, weight=1)
    app.grid_rowconfigure(0, weight=1)

    # 2. Tarjeta principal (Card UI)
    card_frame = ctk.CTkFrame(app, corner_radius=20, fg_color=("gray90", "#2b2b2b"))
    card_frame.grid(row=0, column=0, padx=40, pady=60, sticky="nsew")

    # Cabecera de la tarjeta
    label_titulo = ctk.CTkLabel(card_frame, text="BOUTIQUE\nZAMORA", font=ctk.CTkFont(family="Roboto", size=32, weight="bold"))
    label_titulo.pack(pady=(40, 10))

    label_subtitulo = ctk.CTkLabel(card_frame, text="Inicia sesión para continuar", font=("Roboto", 14), text_color="gray")
    label_subtitulo.pack(pady=(0, 30))

    # Cajas de texto estilizadas
    entry_usuario = ctk.CTkEntry(card_frame, placeholder_text="👤  Usuario", width=280, height=45, corner_radius=10)
    entry_usuario.pack(pady=10)

    entry_password = ctk.CTkEntry(card_frame, placeholder_text="🔒  Contraseña", show="*", width=280, height=45, corner_radius=10)
    entry_password.pack(pady=15)

    # 3. Lógica del Botón
    def evento_login(event=None): # Aceptamos event para poder usar "Enter"
        user = entry_usuario.get().strip()
        pwd = entry_password.get().strip()

        if not user or not pwd:
            messagebox.showwarning("Campos vacíos", "Por favor, llena ambos campos.", parent=app)
            return

        # Validación con el backend
        usuario_activo = validar_credenciales(user, pwd)

        if usuario_activo:
            app.withdraw()
            dashboard = VentanaPrincipal(usuario_activo, login_window=app)
            dashboard.protocol("WM_DELETE_WINDOW", sys.exit)
            dashboard.mainloop()
        else:   
            messagebox.showerror("Acceso Denegado", "Usuario o contraseña incorrectos.\nVerifica tus datos.", parent=app)

    # Permitir login con la tecla Enter
    app.bind('<Return>', evento_login)

    # Botón principal
    btn_login = ctk.CTkButton(card_frame, text="Ingresar al Sistema", command=evento_login, width=300, height=50,
                              corner_radius=16, font=("Roboto", 16, "bold"), fg_color=("#1f538d", "#17427f"), hover_color=("#14375e", "#0f2a55"), text_color="white")
    btn_login.pack(pady=(20, 20))

    # Pequeño separador visual
    separator = ctk.CTkFrame(card_frame, width=250, height=2, fg_color=("gray80", "#3b3b3b"))
    separator.pack(pady=10)

    # 4. Funcionalidad Extra: Interruptor de Tema
    def cambiar_tema(valor):
        nuevo_modo = "light" if valor == "Modo Claro" else "dark"
        ctk.set_appearance_mode(nuevo_modo)

    tema_switch = ctk.CTkSegmentedButton(card_frame, values=["Modo Oscuro", "Modo Claro"], command=cambiar_tema)
    tema_switch.set("Modo Oscuro")
    tema_switch.pack(pady=(15, 30))

    # 5. Bucle principal
    app.mainloop()

if __name__ == "__main__":
    iniciar_app()