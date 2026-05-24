import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from PIL import Image
import sys
import os

# Aseguramos que Python encuentre la lógica
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logica.servicio_inventario import obtener_reporte_existencias
from logica.servicio_ventas import buscar_producto_por_id, buscar_producto_por_nombre, guardar_venta
from logica.servicio_reportes import registrar_venta_en_excel, generar_ticket_txt, registrar_devolucion_en_excel
from logica.servicio_admin import *


class VentanaPrincipal(ctk.CTkToplevel): 
    def __init__(self, usuario):
        super().__init__()

        self.usuario = usuario
        self.title(f"Boutique Zamora - Panel de {usuario.nombre} (Rol: {usuario.rol})")
        self.geometry("1100x680") 

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.carrito = []
        self.total_venta = 0.0
        self.productos_completos = []
        
        # Carpeta donde se guardan las fotos
        self.carpeta_imagenes = "imagenes_productos"
        
        # Variable para almacenar el ID del producto seleccionado en el catálogo de cartas
        self.producto_seleccionado_id = None 
        self.carta_seleccionada = None

        # --- 1. SIDEBAR MODERNO ---
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1) # Empuja el perfil hacia abajo
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="🛍️ BOUTIQUE", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 30))

        # Botones con iconos y alineados a la izquierda (anchor="w")
        self.btn_inicio = ctk.CTkButton(self.sidebar_frame, text="📊  Dashboard", command=self.mostrar_frame_bienvenida, anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.btn_inicio.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        self.btn_inventario = ctk.CTkButton(self.sidebar_frame, text="📦  Inventario", command=self.mostrar_frame_inventario, anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.btn_inventario.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.btn_ventas = ctk.CTkButton(self.sidebar_frame, text="🛒  Punto de Venta", command=self.mostrar_frame_ventas, anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.btn_ventas.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        
        self.btn_historial = ctk.CTkButton(self.sidebar_frame, text="📜  Historial", command=self.mostrar_frame_historial, anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.btn_historial.grid(row=4, column=0, padx=20, pady=5, sticky="ew")

        # --- SECCIÓN ADMINISTRATIVA ---
        if str(self.usuario.rol).lower() in ["1", "administrador", "admin"]:
            ctk.CTkLabel(self.sidebar_frame, text="ADMINISTRACIÓN", font=("Roboto", 11, "bold"), text_color="gray").grid(row=5, column=0, padx=20, pady=(20, 5), sticky="w")

            self.btn_empleados = ctk.CTkButton(self.sidebar_frame, text="👥  Personal", command=self.mostrar_frame_empleados, anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
            self.btn_empleados.grid(row=6, column=0, padx=20, pady=5, sticky="ew")

            self.btn_reportes = ctk.CTkButton(self.sidebar_frame, text="📈  Reportes Excel", command=self.mostrar_frame_reportes, anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
            self.btn_reportes.grid(row=7, column=0, padx=20, pady=5, sticky="ew")

        # Selector de Tema
        self.menu_tema = ctk.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light"], command=self.cambiar_tema)
        self.menu_tema.grid(row=9, column=0, padx=20, pady=(10, 10), sticky="s")

        # --- TARJETA DE PERFIL ---
        self.profile_frame = ctk.CTkFrame(self.sidebar_frame, fg_color=("#e0e0e0", "#2b2b2b"), corner_radius=10)
        self.profile_frame.grid(row=10, column=0, padx=15, pady=20, sticky="ew")
        self.profile_frame.grid_columnconfigure(1, weight=1)

        lbl_avatar = ctk.CTkLabel(self.profile_frame, text="👨‍💼", font=("Roboto", 30))
        lbl_avatar.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

        lbl_nombre = ctk.CTkLabel(self.profile_frame, text=self.usuario.nombre, font=("Roboto", 13, "bold"))
        lbl_nombre.grid(row=0, column=1, sticky="w", pady=(10, 0))

        rol_txt = "Admin" if str(self.usuario.rol).lower() in ["1", "admin", "administrador"] else "Cajero"
        lbl_rol = ctk.CTkLabel(self.profile_frame, text=rol_txt, font=("Roboto", 11), text_color="gray")
        lbl_rol.grid(row=1, column=1, sticky="w", pady=(0, 10))

        btn_salir = ctk.CTkButton(self.profile_frame, text="🚪", width=30, fg_color="transparent", hover_color="#b22222", command=self.cerrar_sesion)
        btn_salir.grid(row=0, column=2, rowspan=2, padx=(0, 10))

        # --- 2. CONTENEDOR PRINCIPAL ---
        self.main_container = ctk.CTkFrame(self, corner_radius=10)
        self.main_container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        # Inicializar todos los frames visuales
        self.crear_frame_bienvenida()
        self.crear_frame_inventario()
        self.crear_frame_ventas()
        self.crear_frame_historial()
        
        if str(self.usuario.rol).lower() in ["1", "administrador", "admin"]:
            self.crear_frame_empleados()

        self.frame_bienvenida.grid(row=0, column=0, sticky="nsew")

    # ==========================================
    # VISTA: DASHBOARD DE BIENVENIDA MODERNO
    # ==========================================
    def crear_frame_bienvenida(self):
        self.frame_bienvenida = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.frame_bienvenida.grid_columnconfigure((0, 1, 2), weight=1)

        header_frame = ctk.CTkFrame(self.frame_bienvenida, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(20, 20))
        
        lbl_titulo = ctk.CTkLabel(header_frame, text=f"Resumen General", font=("Roboto", 24, "bold"))
        lbl_titulo.pack(side="left", padx=20)
        
        def crear_tarjeta(parent, row, col, color, icono, titulo, valor_inicial):
            card = ctk.CTkFrame(parent, fg_color=color, corner_radius=15, height=110)
            card.grid(row=row, column=col, padx=15, pady=10, sticky="nsew")
            card.grid_propagate(False)
            card.pack_propagate(False)
            
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(expand=True, fill="both", padx=20, pady=20)
            
            lbl_icono = ctk.CTkLabel(inner, text=icono, font=("Roboto", 45))
            lbl_icono.pack(side="left", padx=(0, 15))
            
            text_frame = ctk.CTkFrame(inner, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True)
            
            ctk.CTkLabel(text_frame, text=titulo, font=("Roboto", 14), text_color="#e0e0e0").pack(anchor="w")
            lbl_valor = ctk.CTkLabel(text_frame, text=valor_inicial, font=("Roboto", 28, "bold"), text_color="white")
            lbl_valor.pack(anchor="w")
            
            return lbl_valor

        self.lbl_ventas_hoy = crear_tarjeta(self.frame_bienvenida, 1, 0, "#1f538d", "💰", "Ingresos Hoy", "$0.00")
        self.lbl_total_prods = crear_tarjeta(self.frame_bienvenida, 1, 1, "#2e8b57", "📦", "Productos", "0")
        self.lbl_stock_bajo = crear_tarjeta(self.frame_bienvenida, 1, 2, "#b22222", "⚠️", "Stock Bajo", "0")

        chart_frame = ctk.CTkFrame(self.frame_bienvenida, corner_radius=15)
        chart_frame.grid(row=2, column=0, columnspan=3, padx=15, pady=20, sticky="nsew")
        self.frame_bienvenida.grid_rowconfigure(2, weight=1) 
        
        ctk.CTkLabel(chart_frame, text="Actividad Reciente", font=("Roboto", 16, "bold")).pack(anchor="w", padx=20, pady=15)
        ctk.CTkLabel(chart_frame, text="📊 Panel reservado para gráfica de ventas", text_color="gray").pack(expand=True)
        
        self.actualizar_dashboard()

    # ==========================================
    # VISTA: INVENTARIO (CATÁLOGO DE CARTAS)
    # ==========================================
    def crear_frame_inventario(self):
        self.frame_inventario = ctk.CTkFrame(self.main_container, fg_color="transparent")
        
        # --- Barra de Herramientas Superior ---
        frame_herramientas = ctk.CTkFrame(self.frame_inventario, fg_color="transparent")
        frame_herramientas.pack(side="top", fill="x", padx=20, pady=(10, 15))
        
        # Filtro de búsqueda minimalista
        self.entry_filtro = ctk.CTkEntry(frame_herramientas, placeholder_text="🔍 Buscar por nombre, ID o talla...", width=350, height=35)
        self.entry_filtro.pack(side="left", padx=(0, 10))
        self.entry_filtro.bind("<KeyRelease>", self.filtrar_inventario_cartas)

        # Segmented button para filtros rápidos
        self.segment_filtro = ctk.CTkSegmentedButton(frame_herramientas, values=["Todo", "Camisas", "Pantalones"], command=self.filtrar_inventario_cartas)
        self.segment_filtro.set("Todo")
        self.segment_filtro.pack(side="left")

        # --- Controles de Acción (Abajo del filtro) ---
        frame_controles = ctk.CTkFrame(self.frame_inventario, fg_color="transparent")
        frame_controles.pack(side="top", fill="x", padx=20, pady=(0, 10)) 

        btn_actualizar = ctk.CTkButton(frame_controles, text="🔄 Refrescar", command=self.cargar_datos_inventario, width=120)
        btn_actualizar.pack(side="left", padx=5)

        # --- BOTÓN DE FOTOS ADAPTADO ---
        btn_foto = ctk.CTkButton(frame_controles, text="🖼️ Ver/Subir Foto", command=self.ventana_foto_producto_carta, width=120, fg_color="#8b6508", hover_color="#b8860b")
        btn_foto.pack(side="left", padx=5)

        if str(self.usuario.rol).lower() in ["1", "administrador", "admin"]:
            btn_nuevo = ctk.CTkButton(frame_controles, text="➕ Nuevo", command=self.ventana_nuevo_producto, width=100, fg_color="#2e8b57", hover_color="#236b43")
            btn_nuevo.pack(side="left", padx=5)

            btn_editar = ctk.CTkButton(frame_controles, text="📝 Editar", command=self.ventana_editar_producto_carta, width=100, fg_color="#1f538d")
            btn_editar.pack(side="left", padx=5)

            btn_surtir = ctk.CTkButton(frame_controles, text="📦 Surtir", command=self.surtir_producto_carta, width=100)
            btn_surtir.pack(side="left", padx=5)

            btn_eliminar = ctk.CTkButton(frame_controles, text="🗑️ Eliminar", command=self.eliminar_producto_carta, width=100, fg_color="#b22222", hover_color="#8b1a1a")
            btn_eliminar.pack(side="right", padx=5)

        # --- CONTENEDOR DE CARTAS (Grid) ---
        self.contenedor_cartas = ctk.CTkScrollableFrame(self.frame_inventario, fg_color="transparent")
        self.contenedor_cartas.pack(side="top", fill="both", expand=True, padx=15, pady=5)
        
        # Configuramos las columnas del grid (ejemplo: 4 cartas por fila)
        self.contenedor_cartas.grid_columnconfigure((0, 1, 2, 3), weight=1, pad=15)

    def cargar_datos_inventario(self):
        # 1. Limpiar cartas anteriores de forma SEGURA
        if hasattr(self, 'lista_cartas'):
            for carta in self.lista_cartas:
                carta.destroy()
        self.lista_cartas = [] # Creamos nuestra lista segura
        
        self.producto_seleccionado_id = None
        self.carta_seleccionada = None

        # 2. Obtener los productos reales
        self.productos_completos = obtener_reporte_existencias() 
        
        if not self.productos_completos:
            lbl_vacio = ctk.CTkLabel(self.contenedor_cartas, text="El inventario está vacío.", font=("Roboto", 16))
            lbl_vacio.grid(row=0, column=0, columnspan=4, pady=50)
            self.lista_cartas.append(lbl_vacio) # Lo guardamos para poder limpiarlo después
            return

        # 3. Generar las cartas en el Grid
        columna = 0
        fila = 0
        for p in self.productos_completos:
            self.crear_carta_producto(p, fila, columna)
            
            columna += 1
            if columna > 3: # 4 cartas por fila
                columna = 0
                fila += 1

    def crear_carta_producto(self, datos_producto, fila, columna):
        id_p, nombre_p, talla_p, color_p, precio_p, stock_p = datos_producto
        
        color_fondo = self.frame_inventario._apply_appearance_mode(("#f2f2f2", "#2b2b2b"))
        color_borde = self.frame_inventario._apply_appearance_mode(("#d4d4d4", "#3d3d3d"))
        
        carta = ctk.CTkFrame(self.contenedor_cartas, corner_radius=12, fg_color=color_fondo, border_width=2, border_color=color_borde)
        carta.grid(row=fila, column=columna, padx=10, pady=10, sticky="nsew")
        
        def seleccionar(event, frame=carta, prod_id=id_p):
            if self.carta_seleccionada:
                self.carta_seleccionada.configure(border_color=color_borde) 
            
            self.carta_seleccionada = frame
            self.producto_seleccionado_id = prod_id
            frame.configure(border_color="#1f538d") 
            
        carta.bind("<Button-1>", seleccionar)

        ruta_img = f"{self.carpeta_imagenes}/prod_{id_p}.png"
        lbl_img = ctk.CTkLabel(carta, text="")
        lbl_img.pack(pady=(15, 5))
        lbl_img.bind("<Button-1>", seleccionar)
        
        if os.path.exists(ruta_img):
            try:
                img_pil = Image.open(ruta_img)
                img_pil.thumbnail((200, 200)) 
                img_ctk = ctk.CTkImage(light_image=img_pil, size=(160, 160))
                lbl_img.configure(image=img_ctk)
            except:
                lbl_img.configure(text="📷\nError", font=("Roboto", 16), text_color="gray", width=160, height=160)
        else:
            lbl_img.configure(text="📷\nSin Imagen", font=("Roboto", 16), text_color="gray", width=160, height=160)
        
        lbl_nom = ctk.CTkLabel(carta, text=str(nombre_p), font=("Roboto", 13, "bold"), wraplength=170)
        lbl_nom.pack(pady=2)
        lbl_nom.bind("<Button-1>", seleccionar)
        
        lbl_desc = ctk.CTkLabel(carta, text=f"ID: {id_p} | {talla_p}", font=("Roboto", 11), text_color="gray")
        lbl_desc.pack()
        lbl_desc.bind("<Button-1>", seleccionar)
        
        lbl_pre = ctk.CTkLabel(carta, text=f"${precio_p:.2f}", font=("Roboto", 18, "bold"), text_color=("#1f538d", "#82b2e8"))
        lbl_pre.pack(pady=5)
        lbl_pre.bind("<Button-1>", seleccionar)
        
        color_stock = "#b22222" if stock_p <= 5 else ("#404040", "#e0e0e0")
        lbl_stk = ctk.CTkLabel(carta, text=f"Stock: {stock_p}", font=("Roboto", 12, "bold"), text_color=color_stock)
        lbl_stk.pack(pady=(0, 15))
        lbl_stk.bind("<Button-1>", seleccionar)
        
        # --- NUEVO: Agregamos la carta a nuestra lista segura ---
        self.lista_cartas.append(carta)
    def filtrar_inventario_cartas(self, event=None):
        query = self.entry_filtro.get().lower().strip()
        cat_rapida = self.segment_filtro.get()
        
        if not hasattr(self, 'lista_cartas'): return
        
        # Ocultamos TODAS las cartas de la pantalla (limpiamos el tablero)
        for carta in self.lista_cartas:
            carta.grid_forget() # grid_forget() borra la posición, a diferencia de grid_remove()
            
        # Variables para reorganizar las cartas visibles desde el principio
        columna = 0
        fila = 0
        
        for i, p in enumerate(self.productos_completos):
            if i >= len(self.lista_cartas): break 
            
            id_p, nombre_p, talla_p, color_p, _, _ = p
            nombre_l, talla_l = str(nombre_p).lower(), str(talla_p).lower()
            
            # Buscador por texto
            coincide_busqueda = not query or (query in nombre_l or query in str(id_p) or query in talla_l)
            
            # Filtro Inteligente de Categorías
            palabras_camisas = ["camisa", "playera", "t-shirt", "polo", "blusa"]
            palabras_pantalones = ["pantalon", "pantalón", "jeans", "short", "bermuda"]
            
            coincide_cat = False
            if cat_rapida == "Todo":
                coincide_cat = True
            elif cat_rapida == "Camisas":
                coincide_cat = any(palabra in nombre_l for palabra in palabras_camisas)
            elif cat_rapida == "Pantalones":
                coincide_cat = any(palabra in nombre_l for palabra in palabras_pantalones)
            
            # Si pasa el filtro, LA VOLVEMOS A ACOMODAR en el siguiente espacio disponible
            if coincide_busqueda and coincide_cat:
                self.lista_cartas[i].grid(row=fila, column=columna, padx=10, pady=10, sticky="nsew")
                
                # Avanzamos a la siguiente celda
                columna += 1
                if columna > 3: # 4 cartas por fila como máximo
                    columna = 0
                    fila += 1

    # --- Adaptación de botones para el sistema de cartas ---
    def _obtener_producto_por_id_local(self, id_buscar):
        for p in self.productos_completos:
            if p[0] == id_buscar: return p
        return None

    def ventana_editar_producto_carta(self):
        if not self.producto_seleccionado_id:
            messagebox.showwarning("Atención", "Haz clic en una carta de producto para seleccionarla.", parent=self)
            return
        datos = self._obtener_producto_por_id_local(self.producto_seleccionado_id)
        if datos: self._ventana_form_producto("Editar Producto", datos)

    def ventana_foto_producto_carta(self):
        if not self.producto_seleccionado_id:
            messagebox.showwarning("Atención", "Haz clic en una carta de producto para seleccionarla.", parent=self)
            return
        datos = self._obtener_producto_por_id_local(self.producto_seleccionado_id)
        if datos: self.ventana_foto_producto_base(datos)

    def surtir_producto_carta(self):
        if not self.producto_seleccionado_id:
            messagebox.showwarning("Atención", "Haz clic en una carta para seleccionarla.", parent=self)
            return
        cant = ctk.CTkInputDialog(text="Cantidad a sumar:", title="Surtir").get_input()
        if cant and cant.isdigit():
            if actualizar_stock_producto(self.producto_seleccionado_id, int(cant)): self.cargar_datos_inventario()

    def eliminar_producto_carta(self):
        if not self.producto_seleccionado_id:
            messagebox.showwarning("Atención", "Haz clic en una carta para seleccionarla.", parent=self)
            return
        if messagebox.askyesno("Confirmar", "¿Eliminar producto permanentemente?", parent=self):
            if eliminar_producto_db(self.producto_seleccionado_id): self.cargar_datos_inventario()


    # ==========================================
    # VISTA: VENTAS (DISEÑO ULTRA CLEAN)
    # ==========================================
    def crear_frame_ventas(self):
        self.frame_ventas = ctk.CTkFrame(self.main_container, fg_color="transparent")
        
        # Grid layout: 70% Izquierda (Lista), 30% Derecha (Cobro)
        self.frame_ventas.grid_columnconfigure(0, weight=7)
        self.frame_ventas.grid_columnconfigure(1, weight=3)
        self.frame_ventas.grid_rowconfigure(0, weight=1)

        # ---------------------------------------------------------
        # PANEL IZQUIERDO: Búsqueda y Lista "Clean"
        # ---------------------------------------------------------
        panel_izquierdo = ctk.CTkFrame(self.frame_ventas, fg_color="transparent")
        panel_izquierdo.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        panel_izquierdo.grid_rowconfigure(2, weight=1) 
        
        # Título súper limpio
        ctk.CTkLabel(panel_izquierdo, text="Current Order", font=("Roboto", 28, "bold")).grid(row=0, column=0, sticky="w", pady=(10, 20))

        # Buscador Minimalista
        frame_busqueda = ctk.CTkFrame(panel_izquierdo, fg_color="transparent")
        frame_busqueda.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        
        # Hacemos que el input parezca solo una línea o muy sutil
        self.entry_busqueda = ctk.CTkEntry(frame_busqueda, placeholder_text="Buscar producto por ID o Nombre...", height=40, font=("Roboto", 14), corner_radius=8, border_width=1)
        self.entry_busqueda.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.entry_cantidad = ctk.CTkEntry(frame_busqueda, placeholder_text="1", width=50, height=40, font=("Roboto", 14), justify="center", corner_radius=8, border_width=1)
        self.entry_cantidad.insert(0, "1")
        self.entry_cantidad.pack(side="left", padx=(0, 10))
        
        btn_agregar = ctk.CTkButton(frame_busqueda, text="+ Add", command=self.agregar_al_carrito, height=40, width=80, font=("Roboto", 13, "bold"), fg_color=("#e0e0e0", "#333333"), text_color=("black", "white"), hover_color=("#d0d0d0", "#444444"))
        btn_agregar.pack(side="left")

        # Tabla del carrito (Configurada para parecerse a una lista sin bordes)
        frame_tabla = ctk.CTkFrame(panel_izquierdo, fg_color="transparent")
        frame_tabla.grid(row=2, column=0, sticky="nsew")

        # Ajustamos el estilo de la tabla para quitar los bordes grises feos
        style = ttk.Style()
        style.configure("Clean.Treeview", background=self.frame_ventas._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"]), 
                        foreground=self.frame_ventas._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"]),
                        rowheight=40, borderwidth=0, font=("Roboto", 12))
        style.configure("Clean.Treeview.Heading", background=self.frame_ventas._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"]), 
                        foreground="gray", font=("Roboto", 11, "bold"), borderwidth=0)
        style.layout("Clean.Treeview", [('Clean.Treeview.treearea', {'sticky': 'nswe'})]) # Quita bordes
        
        self.tabla_carrito = ttk.Treeview(frame_tabla, columns=("Cantidad", "Producto", "Precio Unit.", "Subtotal"), show="headings", style="Clean.Treeview")
        
        self.tabla_carrito.heading("Cantidad", text="QTY", anchor="w")
        self.tabla_carrito.column("Cantidad", width=50, anchor="w")
        self.tabla_carrito.heading("Producto", text="ITEM", anchor="w")
        self.tabla_carrito.column("Producto", width=250, anchor="w")
        self.tabla_carrito.heading("Precio Unit.", text="PRICE", anchor="e")
        self.tabla_carrito.column("Precio Unit.", width=80, anchor="e")
        self.tabla_carrito.heading("Subtotal", text="TOTAL", anchor="e")
        self.tabla_carrito.column("Subtotal", width=80, anchor="e")
            
        scrollbar_carrito = ctk.CTkScrollbar(frame_tabla, command=self.tabla_carrito.yview)
        self.tabla_carrito.configure(yscrollcommand=scrollbar_carrito.set)
        
        self.tabla_carrito.pack(side="left", fill="both", expand=True)
        scrollbar_carrito.pack(side="right", fill="y")

        # ---------------------------------------------------------
        # PANEL DERECHO: Cobro Integrado
        # ---------------------------------------------------------
        panel_derecho = ctk.CTkFrame(self.frame_ventas, corner_radius=15, fg_color=("#f9f9f9", "#1e1e1e")) 
        panel_derecho.grid(row=0, column=1, sticky="nsew", pady=10)
        
        ctk.CTkLabel(panel_derecho, text="Payment Details", font=("Roboto", 18, "bold")).pack(anchor="w", padx=25, pady=(25, 20))

        # Subtotal (Visual)
        sub_frame = ctk.CTkFrame(panel_derecho, fg_color="transparent")
        sub_frame.pack(fill="x", padx=25, pady=5)
        ctk.CTkLabel(sub_frame, text="Subtotal", text_color="gray").pack(side="left")
        self.lbl_sub = ctk.CTkLabel(sub_frame, text="$0.00")
        self.lbl_sub.pack(side="right")

        # Impuestos (Simulado visualmente para el diseño)
        tax_frame = ctk.CTkFrame(panel_derecho, fg_color="transparent")
        tax_frame.pack(fill="x", padx=25, pady=5)
        ctk.CTkLabel(tax_frame, text="Taxes (0%)", text_color="gray").pack(side="left")
        ctk.CTkLabel(tax_frame, text="$0.00").pack(side="right")

        ctk.CTkFrame(panel_derecho, height=1, fg_color=("gray85", "#333333")).pack(fill="x", padx=25, pady=15)

        # TOTAL GIGANTE
        tot_frame = ctk.CTkFrame(panel_derecho, fg_color="transparent")
        tot_frame.pack(fill="x", padx=25, pady=(0, 20))
        ctk.CTkLabel(tot_frame, text="Total", font=("Roboto", 20, "bold")).pack(side="left")
        self.label_total = ctk.CTkLabel(tot_frame, text="$0.00", font=("Roboto", 32, "bold"))
        self.label_total.pack(side="right")

        # Botón de Cobro tipo "Pay Now"
        btn_cobrar = ctk.CTkButton(panel_derecho, text="Pay Now", command=self.cobrar_venta, 
                                   height=55, font=("Roboto", 16, "bold"), fg_color="#1a1a1a", text_color="white", hover_color="#333333")
        btn_cobrar.pack(fill="x", padx=25, pady=(10, 10))
        
        # Botones secundarios sutiles
        btn_frame = ctk.CTkFrame(panel_derecho, fg_color="transparent")
        btn_frame.pack(fill="x", padx=25, pady=10)
        
        btn_cancelar = ctk.CTkButton(btn_frame, text="Clear", command=self.cancelar_venta, 
                                     height=40, font=("Roboto", 13), fg_color=("#ffe6e6", "#4a1c1c"), text_color="#b22222", hover_color=("#ffcccc", "#5c2323"))
        btn_cancelar.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        btn_devolucion = ctk.CTkButton(btn_frame, text="Refund", command=self.procesar_devolucion, 
                                       height=40, font=("Roboto", 13), fg_color=("#e6f2ff", "#1a365d"), text_color="#1f538d", hover_color=("#cce5ff", "#23487c"))
        btn_devolucion.pack(side="right", fill="x", expand=True, padx=(5, 0))

    # ==========================================
    # VISTA: HISTORIAL DE VENTAS
    # ==========================================
    def crear_frame_historial(self):
        self.frame_historial = ctk.CTkFrame(self.main_container, fg_color="transparent")
        
        ctk.CTkLabel(self.frame_historial, text="Historial de Ventas", font=("Roboto", 20, "bold")).pack(pady=20)

        frame_botones = ctk.CTkFrame(self.frame_historial, fg_color="transparent")
        frame_botones.pack(pady=10)
        ctk.CTkButton(frame_botones, text="🔄 Actualizar Lista", command=self.cargar_datos_historial).pack(side="left", padx=10)
        ctk.CTkButton(frame_botones, text="📄 Ver Ticket", command=self.abrir_ticket_historial, fg_color="#1f538d").pack(side="left", padx=10)

        # --- MEJORA VISUAL: TABLA DE HISTORIAL CON SCROLLBAR ---
        frame_tabla = ctk.CTkFrame(self.frame_historial)
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

        columnas = ("Folio", "Fecha y Hora", "Total", "Cajero")
        self.tabla_historial = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
        
        anchos = {"Folio": 80, "Fecha y Hora": 200, "Total": 100, "Cajero": 200}
        for col in columnas:
            self.tabla_historial.heading(col, text=col)
            self.tabla_historial.column(col, width=anchos[col], anchor="center")

        scrollbar = ctk.CTkScrollbar(frame_tabla, command=self.tabla_historial.yview)
        self.tabla_historial.configure(yscrollcommand=scrollbar.set)

        self.tabla_historial.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def cargar_datos_historial(self):
        for i in self.tabla_historial.get_children():
            self.tabla_historial.delete(i)
        
        try:
            ventas = obtener_historial_ventas()
            for v in ventas:
                self.tabla_historial.insert("", "end", values=(v[0], v[1], f"${v[2]:.2f}", v[3]))
        except NameError:
            pass 

    def abrir_ticket_historial(self):
        sel = self.tabla_historial.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona una venta de la tabla para ver su ticket.", parent=self)
            return
            
        folio = self.tabla_historial.item(sel[0])['values'][0]
        
        if os.path.exists(f"facturas/ticket_{folio}.txt"): 
            os.startfile(os.path.abspath(f"facturas/ticket_{folio}.txt"))
        else: 
            messagebox.showerror("Error", f"No se encontró el archivo del ticket para el Folio {folio}.", parent=self)

    # ==========================================
    # VISTA: PERSONAL / EMPLEADOS
    # ==========================================
    def crear_frame_empleados(self):
        self.frame_empleados = ctk.CTkFrame(self.main_container, fg_color="transparent")
        
        ctk.CTkLabel(self.frame_empleados, text="Gestión de Personal", font=("Roboto", 20, "bold")).pack(pady=(10, 20))

        frame_controles = ctk.CTkFrame(self.frame_empleados, fg_color="transparent")
        frame_controles.pack(side="bottom", fill="x", padx=20, pady=10) 

        ctk.CTkButton(frame_controles, text="🔄 Refrescar", command=self.cargar_datos_empleados, width=100).pack(side="left", padx=5)
        ctk.CTkButton(frame_controles, text="➕ Nuevo Cajero", command=self.ventana_nuevo_empleado, width=120, fg_color="#2e8b57").pack(side="left", padx=5)
        ctk.CTkButton(frame_controles, text="📝 Editar Acceso", command=self.ventana_editar_empleado, width=120, fg_color="#1f538d").pack(side="left", padx=5)
        ctk.CTkButton(frame_controles, text="🗑️ Dar de Baja", command=self.eliminar_empleado_gui, width=120, fg_color="#b22222").pack(side="right", padx=5)

        # --- MEJORA VISUAL: TABLA DE EMPLEADOS CON SCROLLBAR ---
        frame_tabla = ctk.CTkFrame(self.frame_empleados)
        frame_tabla.pack(side="top", fill="both", expand=True, padx=20, pady=5)

        columnas = ("ID", "Usuario", "Nombre Completo", "Rol")
        self.tabla_empleados = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
        
        anchos = {"ID": 50, "Usuario": 150, "Nombre Completo": 250, "Rol": 100}
        for col in columnas:
            self.tabla_empleados.heading(col, text=col)
            self.tabla_empleados.column(col, width=anchos[col], anchor="center")

        scrollbar = ctk.CTkScrollbar(frame_tabla, command=self.tabla_empleados.yview)
        self.tabla_empleados.configure(yscrollcommand=scrollbar.set)

        self.tabla_empleados.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def cargar_datos_empleados(self):
        for i in self.tabla_empleados.get_children(): self.tabla_empleados.delete(i)
        try:
            empleados = obtener_empleados() 
            for emp in empleados:
                rol_str = "Admin" if str(emp[3]) == "1" else "Cajero"
                self.tabla_empleados.insert("", "end", values=(emp[0], emp[1], emp[2], rol_str))
        except Exception as e:
            print("Error cargando empleados:", e)

    def ventana_nuevo_empleado(self): 
        self._ventana_form_empleado("Registrar Empleado")
    
    def ventana_editar_empleado(self):
        sel = self.tabla_empleados.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un empleado de la tabla.", parent=self)
            return
        datos = self.tabla_empleados.item(sel[0])['values']
        self._ventana_form_empleado("Editar Empleado", datos)

    def _ventana_form_empleado(self, titulo, datos_previ=None):
        ventana = ctk.CTkToplevel(self)
        ventana.title(titulo); ventana.geometry("350x450"); ventana.grab_set()
        ctk.CTkLabel(ventana, text=titulo, font=("Roboto", 20, "bold")).pack(pady=20)

        e_user = ctk.CTkEntry(ventana, placeholder_text="Usuario (Ej. juan_perez)", width=250); e_user.pack(pady=10)
        e_nom = ctk.CTkEntry(ventana, placeholder_text="Nombre Completo", width=250); e_nom.pack(pady=10)
        
        placeholder_pass = "Nueva Contraseña" if datos_previ else "Contraseña"
        e_pass = ctk.CTkEntry(ventana, placeholder_text=placeholder_pass, width=250, show="*"); e_pass.pack(pady=10)
        
        c_rol = ctk.CTkComboBox(ventana, values=["Cajero", "Admin"], width=250, state="readonly"); c_rol.pack(pady=10)

        if datos_previ:
            e_user.insert(0, datos_previ[1])
            e_nom.insert(0, datos_previ[2])
            c_rol.set(datos_previ[3])
        else:
            c_rol.set("Cajero")

        def guardar():
            usuario = e_user.get().strip()
            nombre = e_nom.get().strip()
            password = e_pass.get().strip()
            rol_id = 1 if c_rol.get() == "Admin" else 2

            if not usuario or not nombre:
                messagebox.showerror("Error", "Usuario y Nombre son obligatorios.", parent=ventana)
                return

            if datos_previ:
                if modificar_empleado(datos_previ[0], usuario, password, nombre, rol_id):
                    messagebox.showinfo("Éxito", "Personal actualizado.", parent=ventana)
                    ventana.destroy(); self.cargar_datos_empleados()
            else:
                if not password:
                    messagebox.showerror("Error", "La contraseña es obligatoria para nuevos registros.", parent=ventana)
                    return
                if registrar_empleado(usuario, password, nombre, rol_id):
                    messagebox.showinfo("Éxito", "Personal registrado.", parent=ventana)
                    ventana.destroy(); self.cargar_datos_empleados()

        ctk.CTkButton(ventana, text="Guardar", command=guardar, fg_color="#2e8b57").pack(pady=20)

    def eliminar_empleado_gui(self):
        sel = self.tabla_empleados.selection()
        if not sel: return
        id_emp = self.tabla_empleados.item(sel[0])['values'][0]
        
        if str(id_emp) == str(self.usuario.id):
            messagebox.showerror("Error", "No puedes eliminar tu propio usuario mientras estás en sesión.", parent=self)
            return

        if messagebox.askyesno("Confirmar", "¿Dar de baja a este empleado de forma permanente?", parent=self):
            if eliminar_empleado(id_emp): 
                self.cargar_datos_empleados()

    # ==========================================
    # FUNCIONES DE FOTOS Y OTROS
    # ==========================================
    def ventana_foto_producto_base(self, datos_producto):
        id_p, nombre_p, talla_p, color_p, precio_p, stock_p = datos_producto
        
        win_foto = ctk.CTkToplevel(self)
        win_foto.title(f"Detalles: {nombre_p}")
        win_foto.geometry("450x650")
        win_foto.grab_set()
        
        ctk.CTkLabel(win_foto, text=nombre_p, font=("Roboto", 24, "bold")).pack(pady=(20, 10))
        
        marco_img = ctk.CTkFrame(win_foto, width=280, height=280, corner_radius=15, fg_color=("#d4d4d4", "#1a1a1a"))
        marco_img.pack(pady=10)
        marco_img.pack_propagate(False) 
        
        lbl_img = ctk.CTkLabel(marco_img, text="")
        lbl_img.pack(expand=True)
        
        if not os.path.exists(self.carpeta_imagenes):
            os.makedirs(self.carpeta_imagenes)
        ruta_imagen = f"{self.carpeta_imagenes}/prod_{id_p}.png"
        
        def cargar_visualizacion():
            if os.path.exists(ruta_imagen):
                img_pil = Image.open(ruta_imagen)
                img_pil.thumbnail((260, 260)) 
                img = ctk.CTkImage(light_image=img_pil, size=img_pil.size)
                lbl_img.configure(image=img, text="")
            else:
                lbl_img.configure(image=None, text="📷\nSin Imagen", font=("Roboto", 20), text_color="gray")

        cargar_visualizacion()
        
        marco_detalles = ctk.CTkFrame(win_foto, fg_color="transparent")
        marco_detalles.pack(fill="x", padx=60, pady=15)
        
        ctk.CTkLabel(marco_detalles, text="📏 Talla:", font=("Roboto", 14, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        ctk.CTkLabel(marco_detalles, text=talla_p, font=("Roboto", 14)).grid(row=0, column=1, sticky="e", pady=5)

        ctk.CTkLabel(marco_detalles, text="🎨 Color:", font=("Roboto", 14, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        ctk.CTkLabel(marco_detalles, text=color_p, font=("Roboto", 14)).grid(row=1, column=1, sticky="e", pady=5)

        ctk.CTkLabel(marco_detalles, text="💰 Precio:", font=("Roboto", 14, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        ctk.CTkLabel(marco_detalles, text=precio_p, font=("Roboto", 14, "bold"), text_color="#2e8b57").grid(row=2, column=1, sticky="e", pady=5)

        ctk.CTkLabel(marco_detalles, text="📦 Stock:", font=("Roboto", 14, "bold")).grid(row=3, column=0, sticky="w", pady=5)
        color_stock = "#b22222" if int(stock_p) <= 5 else ("black", "white")
        ctk.CTkLabel(marco_detalles, text=f"{stock_p} uds.", font=("Roboto", 14, "bold"), text_color=color_stock).grid(row=3, column=1, sticky="e", pady=5)

        marco_detalles.grid_columnconfigure(1, weight=1) 
        
        def subir_foto():
            ruta_origen = filedialog.askopenfilename(
                title="Seleccionar imagen del producto", 
                filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp")],
                parent=win_foto
            )
            if ruta_origen:
                try:
                    img_temp = Image.open(ruta_origen)
                    if img_temp.mode != 'RGBA':
                        img_temp = img_temp.convert('RGBA')
                    img_temp.thumbnail((500, 500)) 
                    img_temp.save(ruta_imagen, format="PNG")
                    messagebox.showinfo("Éxito", "Imagen guardada correctamente.", parent=win_foto)
                    cargar_visualizacion() 
                    self.cargar_datos_inventario() # Actualizar carta del grid
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo guardar la imagen: {e}", parent=win_foto)

        marco_botones = ctk.CTkFrame(win_foto, fg_color="transparent")
        marco_botones.pack(pady=(10, 20))

        if str(self.usuario.rol).lower() in ["1", "administrador", "admin"]:
            ctk.CTkButton(marco_botones, text="📷 Actualizar Foto", command=subir_foto, fg_color="#1f538d", width=140).pack(side="left", padx=10)
            
        ctk.CTkButton(marco_botones, text="Cerrar", command=win_foto.destroy, fg_color="#b22222", width=100).pack(side="left", padx=10)

    def mostrar_corte_caja(self):
        total = obtener_total_ventas_dia()
        messagebox.showinfo("Corte de Caja", f"📊 Total de ingresos registrados:\n\n${total:.2f} MXN", parent=self)

    def ventana_nuevo_producto(self):
        self._ventana_form_producto("Registrar Nuevo Producto")

    def _ventana_form_producto(self, titulo, datos_previ=None):
        ventana = ctk.CTkToplevel(self)
        ventana.title(titulo)
        ventana.geometry("400x550")
        ventana.grab_set()

        ctk.CTkLabel(ventana, text=titulo, font=("Roboto", 20, "bold")).pack(pady=20)

        entry_nombre = ctk.CTkEntry(ventana, placeholder_text="Nombre del producto", width=250)
        entry_nombre.pack(pady=10)

        tallas = ['XS', 'S', 'M', 'L', 'XL', 'XXL', '28', '30', '32', '34', '36', '38', '40', 'UNITALLA']
        combo_talla = ctk.CTkComboBox(ventana, values=tallas, width=250, state="readonly")
        combo_talla.set("Selecciona Talla")
        combo_talla.pack(pady=10)

        entry_color = ctk.CTkEntry(ventana, placeholder_text="Color", width=250)
        entry_color.pack(pady=10)

        entry_precio = ctk.CTkEntry(ventana, placeholder_text="Precio Venta ($)", width=250)
        entry_precio.pack(pady=10)

        entry_stock = None
        if not datos_previ:
            entry_stock = ctk.CTkEntry(ventana, placeholder_text="Stock Inicial", width=250)
            entry_stock.pack(pady=10)

        if datos_previ:
            entry_nombre.insert(0, datos_previ[1])
            combo_talla.set(datos_previ[2])
            entry_color.insert(0, datos_previ[3])
            entry_precio.insert(0, str(datos_previ[4]).replace('$', ''))

        def guardar():
            nombre = entry_nombre.get().strip()
            talla = combo_talla.get()
            color = entry_color.get().strip()
            try:
                precio = float(entry_precio.get())
                stock = int(entry_stock.get()) if entry_stock else 0
            except:
                messagebox.showerror("Error", "Revisa los valores numéricos.", parent=ventana)
                return

            if datos_previ:
                if modificar_producto_db(datos_previ[0], nombre, talla, color, precio):
                    messagebox.showinfo("Éxito", "Actualizado.", parent=ventana)
                    ventana.destroy()
                    self.cargar_datos_inventario()
            else:
                if registrar_nuevo_producto(nombre, talla, color, precio, stock):
                    messagebox.showinfo("Éxito", "Registrado.", parent=ventana)
                    ventana.destroy()
                    self.cargar_datos_inventario()

        ctk.CTkButton(ventana, text="Confirmar", command=guardar, fg_color="#2e8b57").pack(pady=20)

    def agregar_al_carrito(self):
        termino = self.entry_busqueda.get().strip()
        cantidad_str = self.entry_cantidad.get().strip()
        if not termino or not cantidad_str: return
        
        try:
            cantidad_a_vender = int(cantidad_str)
        except: return

        producto = buscar_producto_por_id(int(termino)) if termino.isdigit() else buscar_producto_por_nombre(termino)
        
        if producto:
            ya_en_carrito = sum(1 for p in self.carrito if p.id == producto.id)
            
            if (ya_en_carrito + cantidad_a_vender) > producto.stock:
                messagebox.showwarning("Sin Stock", 
                                     f"No puedes agregar {cantidad_a_vender} unidad(es).\n"
                                     f"Stock disponible: {producto.stock}\n"
                                     f"En carrito: {ya_en_carrito}", parent=self)
                return

            for _ in range(cantidad_a_vender): 
                self.carrito.append(producto)   
            self.actualizar_vista_carrito()
            self.entry_busqueda.delete(0, 'end')

    def actualizar_vista_carrito(self):
        for i in self.tabla_carrito.get_children(): self.tabla_carrito.delete(i)
        self.total_venta = 0.0
        res = {}
        for p in self.carrito:
            if p.id not in res: res[p.id] = {"n": f"{p.nombre} ({p.talla})", "p": p.precio, "c": 0}
            res[p.id]["c"] += 1
        for d in res.values():
            sub = d["c"] * d["p"]
            self.total_venta += sub
            self.tabla_carrito.insert("", "end", values=(d["c"], d["n"], f"${d['p']:.2f}", f"${sub:.2f}"))
            
        # Actualizamos las etiquetas del diseño Clean
        self.label_total.configure(text=f"${self.total_venta:.2f}")
        try:
            self.lbl_sub.configure(text=f"${self.total_venta:.2f}")
        except:
            pass

    def cobrar_venta(self):
        if not self.carrito: return
        if not messagebox.askyesno("Confirmar", f"¿Cobrar ${self.total_venta:.2f}?", parent=self): return
        
        folio = guardar_venta(self.usuario.id, self.carrito, self.total_venta)
        if folio:
            registrar_venta_en_excel(folio, self.total_venta, self.usuario.nombre, self.carrito)
            generar_ticket_txt(folio, self.total_venta, self.usuario.nombre, self.carrito)
            
            if messagebox.askyesno("Venta Exitosa", f"Folio registrado: {folio}\n\n¿Deseas abrir el ticket de esta venta?", parent=self):
                if os.path.exists(f"facturas/ticket_{folio}.txt"): 
                    os.startfile(os.path.abspath(f"facturas/ticket_{folio}.txt"))
                else: 
                    messagebox.showwarning("Aviso", "El ticket se generó, pero no se pudo localizar el archivo TXT para abrirlo automáticamente.", parent=self)
            
            self.cancelar_venta()

    def cancelar_venta(self):
        self.carrito.clear()
        self.actualizar_vista_carrito()

    def procesar_devolucion(self):
        id_prod = ctk.CTkInputDialog(text="ID del producto:", title="Devolución").get_input()
        if id_prod and id_prod.isdigit():
            p = buscar_producto_por_id(int(id_prod))
            if p and actualizar_stock_producto(int(id_prod), 1):
                registrar_devolucion_en_excel(self.usuario.nombre, p)
                messagebox.showinfo("Éxito", "Devolución procesada.", parent=self)
                self.cargar_datos_inventario()


    # ==========================================
    # NAVEGACIÓN Y DASHBOARD
    # ==========================================
    def cambiar_tema(self, nuevo_tema: str):
        ctk.set_appearance_mode(nuevo_tema)

    def actualizar_dashboard(self):
        total_v = obtener_total_ventas_dia()
        self.lbl_ventas_hoy.configure(text=f"${total_v:.2f}")

        prods = obtener_reporte_existencias()
        total_p = len(prods) 
        stock_bajo = sum(1 for p in prods if p[5] <= 5)

        self.lbl_total_prods.configure(text=str(total_p))
        self.lbl_stock_bajo.configure(text=str(stock_bajo))

    def mostrar_frame_bienvenida(self):
        self.ocultar_todos_los_frames()
        self.actualizar_dashboard()
        self.frame_bienvenida.grid(row=0, column=0, sticky="nsew")

    def mostrar_frame_inventario(self):
        self.ocultar_todos_los_frames()
        self.frame_inventario.grid(row=0, column=0, sticky="nsew")
        self.cargar_datos_inventario()

    def mostrar_frame_ventas(self):
        self.ocultar_todos_los_frames()
        self.frame_ventas.grid(row=0, column=0, sticky="nsew")
        
    def mostrar_frame_historial(self):
        self.ocultar_todos_los_frames()
        self.frame_historial.grid(row=0, column=0, sticky="nsew")
        self.cargar_datos_historial()

    def mostrar_frame_empleados(self):
        self.ocultar_todos_los_frames()
        self.frame_empleados.grid(row=0, column=0, sticky="nsew")
        self.cargar_datos_empleados()

    def ocultar_todos_los_frames(self):
        self.frame_bienvenida.grid_forget()
        self.frame_inventario.grid_forget()
        self.frame_ventas.grid_forget()
        if hasattr(self, 'frame_historial'): 
            self.frame_historial.grid_forget()
        if hasattr(self, 'frame_empleados'): 
            self.frame_empleados.grid_forget()

    def mostrar_frame_reportes(self):
        if os.path.exists("Reporte_Ventas_Boutique.xlsx"): os.startfile("Reporte_Ventas_Boutique.xlsx")

    def cerrar_sesion(self): sys.exit()