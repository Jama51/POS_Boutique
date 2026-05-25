import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import sys
import os

# Aseguramos que Python encuentre la lógica
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logica.servicio_inventario import obtener_reporte_existencias
from logica.servicio_ventas import buscar_producto_por_id, buscar_producto_por_nombre, guardar_venta
from logica.servicio_reportes import registrar_venta_en_excel, generar_ticket_txt, registrar_devolucion_en_excel
from logica.servicio_admin import *
from modelos.producto import Producto

class VentanaPrincipal(ctk.CTkToplevel):
    def __init__(self, usuario, login_window=None):
        super().__init__()

        self.usuario = usuario
        self.login_window = login_window
        self.title(f"Boutique Zamora - Panel de {usuario.nombre} (Rol: {usuario.rol})")
        self.geometry("1100x680")
        self.minsize(980, 660)
        self.resizable(True, True)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.carrito = []
        self.total_venta = 0.0
        self.productos_completos = []
        self.carpeta_imagenes = "imagenes_productos"
        self._imagenes_tk = []
        self.producto_seleccionado_id = None
        self.carta_seleccionada = None
        self.descuento = 0.0
        self.total_impuestos = 0.0
        self.total_descuento = 0.0
        self.total_con_impuestos = 0.0
        self.lbl_descuento = None
        self.combo_pago = None
        self.entry_descuento = None
        self.entry_efectivo = None
        self.lbl_pago_activo = None
        self.lbl_cambio = None
        self.carrito_table = None

        self.estilo_boton_primario = {
            "font": ("Roboto", 13, "bold"),
            "corner_radius": 18,
            "height": 46,
            "fg_color": ("#6d5dd3", "#5e46b8"),
            "hover_color": ("#7f6ef1", "#6f5fd3"),
            "text_color": "white"
        }
        self.estilo_boton_secundario = {
            "font": ("Roboto", 12, "bold"),
            "corner_radius": 16,
            "height": 42,
            "fg_color": ("#2f3652", "#343f5f"),
            "hover_color": ("#3f4e7a", "#485c94"),
            "text_color": "white"
        }
        self.estilo_boton_exito = {
            "font": ("Roboto", 12, "bold"),
            "corner_radius": 16,
            "height": 42,
            "fg_color": ("#2e8b57", "#237249"),
            "hover_color": ("#3b9f66", "#2d8b55"),
            "text_color": "white"
        }
        self.estilo_boton_peligro = {
            "font": ("Roboto", 12, "bold"),
            "corner_radius": 16,
            "height": 42,
            "fg_color": ("#b22222", "#8b1a1a"),
            "hover_color": ("#c44d4d", "#a33a3a"),
            "text_color": "white"
        }
        self.estilo_boton_texto = {
            "font": ("Roboto", 12, "bold"),
            "corner_radius": 16,
            "height": 42,
            "fg_color": "transparent",
            "hover_color": ("#3b4a6c", "#44547c"),
            "text_color": ("gray10", "gray90")
        }

        self.ttk_style = ttk.Style(self)
        try:
            self.ttk_style.theme_use("default")
        except Exception:
            pass
        self.ttk_style.configure("Custom.Treeview",
                                 background="#131a24",
                                 fieldbackground="#131a24",
                                 foreground="#e5e5e5",
                                 rowheight=33,
                                 font=("Roboto", 11),
                                 bordercolor="#243046",
                                 borderwidth=0)
        self.ttk_style.map("Custom.Treeview",
                           background=[("selected", "#3b4c78")],
                           foreground=[("selected", "white")])
        self.ttk_style.configure("Custom.Treeview.Heading",
                                 background="#101822",
                                 foreground="#9aa5bf",
                                 relief="flat",
                                 font=("Roboto", 11, "bold"))
        self.ttk_style.configure("Custom.Treeview.Column", anchor="center")

        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="🛍️ BOUTIQUE", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 30))

        self.btn_inicio = self.crear_boton(self.sidebar_frame, estilo="texto", text="📊  Dashboard", command=self.mostrar_frame_bienvenida, anchor="w", width=220)
        self.btn_inicio.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        self.btn_inventario = self.crear_boton(self.sidebar_frame, estilo="texto", text="📦  Inventario", command=self.mostrar_frame_inventario, anchor="w", width=220)
        self.btn_inventario.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.btn_ventas = self.crear_boton(self.sidebar_frame, estilo="texto", text="🛒  Punto de Venta", command=self.mostrar_frame_ventas, anchor="w", width=220)
        self.btn_ventas.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        self.btn_historial = self.crear_boton(self.sidebar_frame, estilo="texto", text="📜  Historial", command=self.mostrar_frame_historial, anchor="w", width=220)
        self.btn_historial.grid(row=4, column=0, padx=20, pady=5, sticky="ew")

        if str(self.usuario.rol).lower() in ["1", "administrador", "admin"]:
            ctk.CTkLabel(self.sidebar_frame, text="ADMINISTRACIÓN", font=("Roboto", 11, "bold"), text_color="gray").grid(row=5, column=0, padx=20, pady=(20, 5), sticky="w")

            self.btn_empleados = ctk.CTkButton(self.sidebar_frame, text="👥  Personal", command=self.mostrar_frame_empleados, anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
            self.btn_empleados.grid(row=6, column=0, padx=20, pady=5, sticky="ew")

            self.btn_reportes = ctk.CTkButton(self.sidebar_frame, text="📈  Reportes Excel", command=self.mostrar_frame_reportes, anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
            self.btn_reportes.grid(row=7, column=0, padx=20, pady=5, sticky="ew")

        self.menu_tema = ctk.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light"], command=self.cambiar_tema)
        self.menu_tema.grid(row=9, column=0, padx=20, pady=(10, 10), sticky="s")

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

        self.main_container = ctk.CTkFrame(self, corner_radius=10)
        self.main_container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        self.crear_frame_bienvenida()
        self.crear_frame_inventario()
        self.crear_frame_ventas()
        self.crear_frame_historial()
        if str(self.usuario.rol).lower() in ["1", "administrador", "admin"]:
            self.crear_frame_empleados()

        self.frame_bienvenida.grid(row=0, column=0, sticky="nsew")
    # VISTA: DASHBOARD DE BIENVENIDA MODERNO
    # ==========================================
    def crear_boton(self, parent, estilo="primario", **kwargs):
        estilos = {
            "primario": self.estilo_boton_primario,
            "secundario": self.estilo_boton_secundario,
            "exito": self.estilo_boton_exito,
            "peligro": self.estilo_boton_peligro,
            "texto": self.estilo_boton_texto
        }
        params = estilos.get(estilo, self.estilo_boton_primario).copy()
        params.update(kwargs)
        return ctk.CTkButton(parent, **params)

    def crear_frame_bienvenida(self):
        self.frame_bienvenida = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.frame_bienvenida.grid_columnconfigure((0, 1, 2, 3), weight=1)

        header_frame = ctk.CTkFrame(self.frame_bienvenida, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(20, 20))
        
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
        self.lbl_mas_vendido = crear_tarjeta(self.frame_bienvenida, 1, 3, "#5a3d8d", "🔥", "Más vendido hoy", "Ninguno")

        low_stock_frame = ctk.CTkFrame(self.frame_bienvenida, fg_color=("#161616", "#1f1f1f"), corner_radius=15)
        low_stock_frame.grid(row=2, column=0, columnspan=4, padx=15, pady=(0, 20), sticky="nsew")
        low_stock_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(low_stock_frame, text="Artículos con stock bajo", font=("Roboto", 14, "bold")).grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))
        self.lbl_items_stock_bajo = ctk.CTkLabel(low_stock_frame, text="Ninguno", font=("Roboto", 12), text_color="gray")
        self.lbl_items_stock_bajo.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 15))

        chart_frame = ctk.CTkFrame(self.frame_bienvenida, corner_radius=15, fg_color=("#161616", "#1f1f1f"))
        chart_frame.grid(row=3, column=0, columnspan=4, padx=15, pady=20, sticky="nsew")
        self.frame_bienvenida.grid_rowconfigure(3, weight=1)
        chart_frame.grid_rowconfigure(0, weight=1)
        chart_frame.grid_columnconfigure(0, weight=1)

        header_chart = ctk.CTkFrame(chart_frame, fg_color="transparent")
        header_chart.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 5))
        ctk.CTkLabel(header_chart, text="Ventas de los últimos 5 días", font=("Roboto", 16, "bold")).pack(side="left")
        self.lbl_chart_subtitulo = ctk.CTkLabel(header_chart, text="Monitoreo visual en tiempo real", text_color="gray")
        self.lbl_chart_subtitulo.pack(side="left", padx=(15, 0))

        self.bienvenida_chart_area = ctk.CTkFrame(chart_frame, fg_color="transparent")
        self.bienvenida_chart_area.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        self.chart_canvas = None
        self._grafica_redraw_id = None
        self.bienvenida_chart_area.bind("<Configure>", self._programar_redibujo_dashboard)
        self.actualizar_dashboard()
        self.dibujar_grafica_ventas_ultimos_dias()

    def _programar_redibujo_dashboard(self, event=None):
        if self._grafica_redraw_id:
            self.after_cancel(self._grafica_redraw_id)
        self._grafica_redraw_id = self.after(120, self.dibujar_grafica_ventas_ultimos_dias)

    def dibujar_grafica_ventas_ultimos_dias(self):
        datos = obtener_ventas_ultimos_5_dias()
        etiquetas = [dia for dia, monto in datos]
        montos = [monto for dia, monto in datos]

        if not etiquetas:
            etiquetas = ["-" for _ in range(5)]
            montos = [0.0 for _ in range(5)]

        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()

        fig = Figure(figsize=(7, 3), dpi=100, facecolor="#161616")
        ax = fig.add_subplot(111, facecolor="#161616")

        colores = ["#4a90e2", "#3d7be3", "#3467d4", "#2d55c2", "#2644a8"]
        barras = ax.bar(etiquetas, montos, color=colores, edgecolor="#8ab4f8", linewidth=1.5)

        ax.set_title("Ventas últimos 5 días", color="#e5e5e5", fontsize=16, pad=14)
        ax.set_ylabel("MXN", color="#d0d0d0", fontsize=11)
        ax.set_xlabel("Fecha", color="#d0d0d0", fontsize=11)
        ax.tick_params(colors="#a8a8a8", labelsize=10)

        for spine in ax.spines.values():
            spine.set_color("#3a3a3a")
        ax.grid(axis="y", color="#222222", linestyle="--", linewidth=0.8, alpha=0.7)

        for bar, monto in zip(barras, montos):
            altura = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, altura + max(montos) * 0.02, f"${altura:.0f}",
                    ha="center", va="bottom", color="#e0e0e0", fontsize=9)

        fig.tight_layout(pad=1.2)

        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.bienvenida_chart_area)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill="both", expand=True)

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

        btn_actualizar = self.crear_boton(frame_controles, estilo="secundario", text="🔄 Refrescar", command=self.cargar_datos_inventario, width=120)
        btn_actualizar.pack(side="left", padx=5)

        # --- BOTÓN DE FOTOS ADAPTADO ---
        btn_foto = self.crear_boton(frame_controles, estilo="primario", text="🖼️ Ver/Subir Foto", command=self.ventana_foto_producto_carta, width=120, fg_color=("#8b6508", "#b8860b"), hover_color=("#b8860b", "#cea53a"))
        btn_foto.pack(side="left", padx=5)

        if str(self.usuario.rol).lower() in ["1", "administrador", "admin"]:
            btn_nuevo = self.crear_boton(frame_controles, estilo="exito", text="➕ Nuevo", command=self.ventana_nuevo_producto, width=100)
            btn_nuevo.pack(side="left", padx=5)

            btn_editar = self.crear_boton(frame_controles, estilo="primario", text="📝 Editar", command=self.ventana_editar_producto_carta, width=100)
            btn_editar.pack(side="left", padx=5)

            btn_surtir = self.crear_boton(frame_controles, estilo="secundario", text="📦 Surtir", command=self.surtir_producto_carta, width=100)
            btn_surtir.pack(side="left", padx=5)

            btn_eliminar = self.crear_boton(frame_controles, estilo="peligro", text="🗑️ Eliminar", command=self.eliminar_producto_carta, width=100)
            btn_eliminar.pack(side="right", padx=5)

        # --- CONTENEDOR DE CARTAS (Grid) ---
        self.contenedor_cartas_wrapper = ctk.CTkFrame(self.frame_inventario, fg_color="transparent")
        self.contenedor_cartas_wrapper.pack(side="top", fill="both", expand=True, padx=15, pady=5)

        bg_color = self.frame_inventario._apply_appearance_mode(("#f9f9f9", "#1f1f1f"))
        self.canvas_inventario = tk.Canvas(self.contenedor_cartas_wrapper, highlightthickness=0, bg=bg_color)
        self.scrollbar_inventario = ctk.CTkScrollbar(self.contenedor_cartas_wrapper, orientation="vertical", command=self.canvas_inventario.yview)
        self.canvas_inventario.configure(yscrollcommand=self.scrollbar_inventario.set)

        self.scrollbar_inventario.pack(side="right", fill="y")
        self.canvas_inventario.pack(side="left", fill="both", expand=True)

        self.contenedor_cartas = ctk.CTkFrame(self.canvas_inventario, fg_color="transparent")
        self.canvas_window = self.canvas_inventario.create_window((0, 0), window=self.contenedor_cartas, anchor="nw")

        self.contenedor_cartas.bind("<Configure>", lambda e: self.canvas_inventario.configure(scrollregion=self.canvas_inventario.bbox("all")))
        self.canvas_inventario.bind("<Configure>", lambda e: self.canvas_inventario.itemconfigure(self.canvas_window, width=e.width))
        self.canvas_inventario.bind("<Enter>", lambda e: self.canvas_inventario.bind_all("<MouseWheel>", self._on_mousewheel_inventario))
        self.canvas_inventario.bind("<Leave>", lambda e: self.canvas_inventario.unbind_all("<MouseWheel>"))

        self.columnas_inventario = 4
        for idx in range(6):
            self.contenedor_cartas.grid_columnconfigure(idx, weight=1, uniform="col")

        self.canvas_inventario.bind("<Configure>", self._actualizar_columnas_inventario)

    def _actualizar_columnas_inventario(self, event=None):
        ancho = event.width if event else self.canvas_inventario.winfo_width()
        columnas = max(1, min(6, ancho // 260))
        if columnas == self.columnas_inventario:
            return

        self.columnas_inventario = columnas
        for idx in range(6):
            self.contenedor_cartas.grid_columnconfigure(idx, weight=1, uniform="col")

        self.filtrar_inventario_cartas()

    def _on_mousewheel_inventario(self, event):
        if self.canvas_inventario.winfo_height() < self.contenedor_cartas.winfo_height():
            self.canvas_inventario.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def cargar_datos_inventario(self):
        # 1. Limpiar cartas anteriores de forma SEGURA
        if hasattr(self, 'lista_cartas'):
            for _, carta in self.lista_cartas:
                carta.destroy()
        self.lista_cartas = [] # Creamos nuestra lista segura
        self.productos_por_id = {}
        
        self.producto_seleccionado_id = None
        self.carta_seleccionada = None

        # 2. Obtener los productos reales
        self.productos_completos = obtener_reporte_existencias() 
        self.productos_por_id = {p[0]: p for p in self.productos_completos}
        
        if not self.productos_completos:
            lbl_vacio = ctk.CTkLabel(self.contenedor_cartas, text="El inventario está vacío.", font=("Roboto", 16))
            lbl_vacio.grid(row=0, column=0, columnspan=self.columnas_inventario, pady=50)
            self.lista_cartas.append((None, lbl_vacio))
            return

        # 3. Generar las cartas en el Grid
        columna = 0
        fila = 0
        for p in self.productos_completos:
            self.crear_carta_producto(p, fila, columna)
            
            columna += 1
            if columna >= self.columnas_inventario:
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
            except Exception:
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
        self.lista_cartas.append((id_p, carta))

    def filtrar_inventario_cartas(self, event=None):
        query = self.entry_filtro.get().lower().strip()
        cat_rapida = self.segment_filtro.get()
        
        if not hasattr(self, 'lista_cartas'): return
        
        # Ocultamos TODAS las cartas de la pantalla (limpiamos el tablero)
        for _, carta in self.lista_cartas:
            carta.grid_forget()
            
        # Variables para reorganizar las cartas visibles desde el principio
        columna = 0
        fila = 0
        
        palabras_camisas = ["camisa", "playera", "t-shirt", "polo", "blusa"]
        palabras_pantalones = ["pantalon", "pantalón", "jeans", "short", "bermuda"]

        for id_p, carta in self.lista_cartas:
            if id_p is None:
                continue

            producto = self.productos_por_id.get(id_p)
            if not producto:
                continue

            _, nombre_p, talla_p, color_p, _, _ = producto
            nombre_l, talla_l = str(nombre_p).lower(), str(talla_p).lower()
            
            coincide_busqueda = not query or (query in nombre_l or query in str(id_p) or query in talla_l)
            
            coincide_cat = False
            if cat_rapida == "Todo":
                coincide_cat = True
            elif cat_rapida == "Camisas":
                coincide_cat = any(palabra in nombre_l for palabra in palabras_camisas)
            elif cat_rapida == "Pantalones":
                coincide_cat = any(palabra in nombre_l for palabra in palabras_pantalones)
            
            if coincide_busqueda and coincide_cat:
                carta.grid(row=fila, column=columna, padx=10, pady=10, sticky="nsew")
                columna += 1
                if columna >= self.columnas_inventario:
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
        
        # Grid layout: 80% Izquierda (Lista), 20% Derecho (Cobro)
        self.frame_ventas.grid_columnconfigure(0, weight=8)
        self.frame_ventas.grid_columnconfigure(1, weight=2, minsize=340)
        self.frame_ventas.grid_rowconfigure(0, weight=1)

        panel_izquierdo = ctk.CTkFrame(self.frame_ventas, fg_color=("#10131a", "#141824"), corner_radius=18, border_width=1, border_color=("#222b38", "#1f2735"))
        panel_izquierdo.grid(row=0, column=0, sticky="nsew", padx=(0, 20), pady=5)
        panel_izquierdo.grid_columnconfigure(0, weight=1)
        panel_izquierdo.grid_rowconfigure(0, weight=0)
        panel_izquierdo.grid_rowconfigure(1, weight=0)
        panel_izquierdo.grid_rowconfigure(2, weight=6)
        panel_izquierdo.grid_rowconfigure(3, weight=5)

        cabecera_ventas = ctk.CTkFrame(panel_izquierdo, fg_color="transparent")
        cabecera_ventas.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        ctk.CTkLabel(cabecera_ventas, text="Punto de Venta", font=("Roboto", 26, "bold"), text_color="white").pack(side="left")
        ctk.CTkLabel(cabecera_ventas, text="Manual y eficiente", font=("Roboto", 12), text_color="#8c97b8").pack(side="left", padx=12)

        acciones_ventas = ctk.CTkFrame(cabecera_ventas, fg_color="transparent")
        acciones_ventas.pack(side="right")
        self.crear_boton(acciones_ventas, estilo="secundario", text="Cerrar sesión", width=130, command=self.cerrar_sesion).pack(side="right", padx=(10, 0))
        self.crear_boton(acciones_ventas, estilo="peligro", text="Salir", width=90, command=self.salir_aplicacion).pack(side="right", padx=(0, 0))

        frame_busqueda = ctk.CTkFrame(panel_izquierdo, fg_color=("#121821", "#161d29"), corner_radius=16, border_width=1, border_color=("#232f44", "#1f2937"))
        frame_busqueda.grid(row=1, column=0, sticky="ew", pady=(0, 18), padx=20)
        frame_busqueda.grid_columnconfigure(0, weight=1)
        frame_busqueda.grid_columnconfigure(1, weight=0)
        frame_busqueda.grid_columnconfigure(2, weight=0)

        self.entry_busqueda = ctk.CTkEntry(frame_busqueda, placeholder_text="Buscar producto por ID o nombre...", height=46, font=("Roboto", 13), corner_radius=16, border_width=1)
        self.entry_busqueda.grid(row=0, column=0, sticky="ew", padx=(16, 10), pady=10)
        self.entry_busqueda.bind("<Return>", lambda e: self.agregar_al_carrito())

        self.entry_cantidad = ctk.CTkEntry(frame_busqueda, placeholder_text="1", width=80, height=46, font=("Roboto", 13), justify="center", corner_radius=16, border_width=1)
        self.entry_cantidad.insert(0, "1")
        self.entry_cantidad.grid(row=0, column=1, padx=(0, 10), pady=10)

        btn_agregar = self.crear_boton(frame_busqueda, estilo="primario", text="Agregar", command=self.agregar_al_carrito, width=120)
        btn_agregar.grid(row=0, column=2, padx=(0, 18), pady=10)

        self.catalogo_scroll = ctk.CTkScrollableFrame(panel_izquierdo, fg_color=("#131824", "#141a27"), corner_radius=16, border_width=1, border_color=("#212b3b", "#1f2737"), orientation="horizontal", height=520)
        self.catalogo_scroll.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 12))
        self.catalogo_content = ctk.CTkFrame(self.catalogo_scroll, fg_color="transparent")
        self.catalogo_content.pack(fill="both", expand=True, padx=10, pady=10)
        self.catalogo_content.bind("<Configure>", lambda e: self._programar_reflow_catalogo())

        frame_tabla = ctk.CTkFrame(panel_izquierdo, fg_color=("#12181f", "#141c24"), corner_radius=16, border_width=1, border_color=("#222f44", "#1e2b40"))
        frame_tabla.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 20))
        frame_tabla.grid_rowconfigure(0, weight=0)
        frame_tabla.grid_rowconfigure(1, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)

        self.carrito_table_header = ctk.CTkFrame(frame_tabla, fg_color=("#161d2b", "#1b2334"), corner_radius=14)
        self.carrito_table_header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))
        ctk.CTkLabel(self.carrito_table_header, text="IMAGEN", width=70, anchor="w", text_color="gray", font=("Roboto", 11, "bold")).pack(side="left", padx=8)
        ctk.CTkLabel(self.carrito_table_header, text="PRODUCTO", width=170, anchor="w", text_color="gray", font=("Roboto", 11, "bold")).pack(side="left", padx=8)
        ctk.CTkLabel(self.carrito_table_header, text="TALLA", width=70, anchor="center", text_color="gray", font=("Roboto", 11, "bold")).pack(side="left", padx=8)
        ctk.CTkLabel(self.carrito_table_header, text="CANT.", width=70, anchor="center", text_color="gray", font=("Roboto", 11, "bold")).pack(side="left", padx=8)
        ctk.CTkLabel(self.carrito_table_header, text="P. UNIT.", width=90, anchor="e", text_color="gray", font=("Roboto", 11, "bold")).pack(side="left", padx=8)
        ctk.CTkLabel(self.carrito_table_header, text="SUBTOTAL", width=90, anchor="e", text_color="gray", font=("Roboto", 11, "bold")).pack(side="left", padx=8)
        ctk.CTkLabel(self.carrito_table_header, text="", width=50, anchor="center", text_color="gray", font=("Roboto", 11, "bold")).pack(side="left", padx=8)

        self.contenedor_carrito = ctk.CTkScrollableFrame(frame_tabla, fg_color=("#131924", "#151d28"), corner_radius=16, border_width=1, border_color=("#212f48", "#1f2f41"))
        self.contenedor_carrito.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.contenedor_carrito.grid_rowconfigure(0, weight=1)
        self.contenedor_carrito.grid_columnconfigure(0, weight=1)

        self.carrito_table = ctk.CTkFrame(self.contenedor_carrito, fg_color="transparent")
        self.carrito_table.pack(fill="both", expand=True, padx=4, pady=4)

        # ---------------------------------------------------------
        # PANEL DERECHO: Cobro Integrado
        # ---------------------------------------------------------
        panel_derecho = ctk.CTkFrame(self.frame_ventas, corner_radius=18, fg_color=("#121824", "#171e2f"), border_width=1, border_color=("#262f3a", "#2f3a46"))
        panel_derecho.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=5)
        panel_derecho.grid_rowconfigure(10, weight=1)
        
        ctk.CTkLabel(panel_derecho, text="Resumen de Pago", font=("Roboto", 22, "bold"), text_color="white").pack(anchor="w", padx=25, pady=(25, 10))
        ctk.CTkLabel(panel_derecho, text="Control rápido de cobro", font=("Roboto", 12), text_color="#8c97b8").pack(anchor="w", padx=25)

        resumen_frame = ctk.CTkFrame(panel_derecho, fg_color=("#161c2c", "#1b2334"), corner_radius=18, border_width=1, border_color=("#273149", "#2d3950"))
        resumen_frame.pack(fill="x", padx=25, pady=20)

        self.lbl_total_articulos = ctk.CTkLabel(resumen_frame, text="0 artículos", font=("Roboto", 12), text_color="#8c97b8")
        self.lbl_total_articulos.pack(anchor="w", padx=20, pady=(20, 4))

        ctk.CTkLabel(resumen_frame, text="Subtotal", font=("Roboto", 11), text_color="gray").pack(anchor="w", padx=20, pady=(0, 2))
        self.lbl_sub = ctk.CTkLabel(resumen_frame, text="$0.00", font=("Roboto", 24, "bold"), text_color="white")
        self.lbl_sub.pack(anchor="w", padx=20)

        ctk.CTkLabel(resumen_frame, text="Descuento", font=("Roboto", 11), text_color="gray").pack(anchor="w", padx=20, pady=(16, 2))
        discount_row = ctk.CTkFrame(resumen_frame, fg_color=("#121822", "#151c28"), corner_radius=14)
        discount_row.pack(fill="x", padx=20, pady=(0, 10))
        self.entry_descuento = ctk.CTkEntry(discount_row, placeholder_text="0.00", width=220, height=36, font=("Roboto", 12), justify="right", corner_radius=14, border_width=1)
        self.entry_descuento.insert(0, "0.00")
        self.entry_descuento.pack(side="left", padx=10, pady=6)
        self.entry_descuento.bind("<FocusOut>", lambda e: self.actualizar_totales_ventas())
        self.entry_descuento.bind("<Return>", lambda e: self.actualizar_totales_ventas())

        ctk.CTkLabel(resumen_frame, text="El descuento se aplica al subtotal neto.", font=("Roboto", 10), text_color="#7c8cc4").pack(anchor="w", padx=20, pady=(2, 8))
        ctk.CTkFrame(resumen_frame, height=1, fg_color=("#273149", "#2b3450")).pack(fill="x", padx=20, pady=18)

        total_frame = ctk.CTkFrame(resumen_frame, fg_color="transparent")
        total_frame.pack(fill="x", padx=20, pady=(0, 20))
        ctk.CTkLabel(total_frame, text="TOTAL", font=("Roboto", 18, "bold"), text_color="white").pack(side="left")
        self.label_total = ctk.CTkLabel(total_frame, text="$0.00", font=("Roboto", 30, "bold"), text_color="#9d7cff")
        self.label_total.pack(side="right")

        ctk.CTkLabel(panel_derecho, text="Método de pago", font=("Roboto", 12), text_color="#8c97b8").pack(anchor="w", padx=25, pady=(8, 4))
        self.combo_pago = ctk.CTkComboBox(panel_derecho, values=["Efectivo", "Tarjeta", "Transferencia"], width=260, state="readonly", fg_color=("#161e2f", "#1b2335"), button_color=("#6d5dd3", "#5e46b8"), text_color="white")
        self.combo_pago.set("Efectivo")
        self.combo_pago.pack(anchor="w", padx=25)
        self.combo_pago.configure(command=lambda v: self.actualizar_totales_ventas())

        self.lbl_pago_activo = ctk.CTkLabel(panel_derecho, text="Activo: Efectivo", font=("Roboto", 11), text_color="#a7b1d8")
        self.lbl_pago_activo.pack(anchor="w", padx=25, pady=(6, 10))

        ctk.CTkLabel(panel_derecho, text="Efectivo recibido", font=("Roboto", 12), text_color="#8c97b8").pack(anchor="w", padx=25, pady=(8, 4))
        self.entry_efectivo = ctk.CTkEntry(panel_derecho, placeholder_text="0.00", width=260, height=42, font=("Roboto", 13), corner_radius=14, border_width=1, justify="right")
        self.entry_efectivo.insert(0, "0.00")
        self.entry_efectivo.pack(anchor="w", padx=25)
        self.entry_efectivo.bind("<FocusOut>", lambda e: self.actualizar_totales_ventas())
        self.entry_efectivo.bind("<Return>", lambda e: self.actualizar_totales_ventas())

        ctk.CTkLabel(panel_derecho, text="Cambio", font=("Roboto", 12), text_color="#8c97b8").pack(anchor="w", padx=25, pady=(16, 4))
        self.lbl_cambio = ctk.CTkLabel(panel_derecho, text="$0.00", font=("Roboto", 22, "bold"), text_color="#76ffb0")
        self.lbl_cambio.pack(anchor="w", padx=25)

        btn_cobrar = self.crear_boton(panel_derecho, estilo="primario", text="Cobrar", command=self.cobrar_venta, width=260, height=50, font=("Roboto", 15, "bold"), corner_radius=18, fg_color=("#8d5cff", "#7c4ee6"), hover_color=("#a073ff", "#8d6cef"))
        btn_cobrar.pack(fill="x", padx=25, pady=(30, 10))
        
        btn_frame = ctk.CTkFrame(panel_derecho, fg_color="transparent")
        btn_frame.pack(fill="x", padx=25, pady=(0, 25))
        
        btn_cancelar = self.crear_boton(btn_frame, estilo="secundario", text="Limpiar carrito", command=self.cancelar_venta, corner_radius=14, width=120)
        btn_cancelar.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        btn_devolucion = self.crear_boton(btn_frame, estilo="primario", text="Devolución", command=self.procesar_devolucion, corner_radius=14, width=120)
        btn_devolucion.pack(side="right", fill="x", expand=True, padx=(8, 0))

        # Inicializar catálogo y carrito
        try:
            self.cargar_catalogo_productos()
        except Exception:
            pass
        self.actualizar_vista_carrito()

    # ==========================================
    # VISTA: HISTORIAL DE VENTAS
    # ==========================================
    def crear_frame_historial(self):
        self.frame_historial = ctk.CTkFrame(self.main_container, fg_color="transparent")
        
        ctk.CTkLabel(self.frame_historial, text="Historial de Ventas", font=("Roboto", 20, "bold")).pack(pady=20)

        frame_botones = ctk.CTkFrame(self.frame_historial, fg_color="transparent")
        frame_botones.pack(fill="x", padx=20, pady=10)
        self.crear_boton(frame_botones, estilo="secundario", text="🔄 Actualizar Lista", command=self.cargar_datos_historial).pack(side="left", padx=10)
        self.crear_boton(frame_botones, estilo="primario", text="📄 Ver Ticket", command=self.abrir_ticket_historial, width=140).pack(side="left", padx=10)

        # --- MEJORA VISUAL: TABLA DE HISTORIAL CON SCROLLBAR ---
        frame_tabla = ctk.CTkFrame(self.frame_historial, fg_color=("#12181f", "#141c24"), corner_radius=18, border_width=1, border_color=("#243046", "#1f2d40"))
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

        columnas = ("Folio", "Fecha y Hora", "Total", "Cajero")
        self.tabla_historial = ttk.Treeview(frame_tabla, columns=columnas, show="headings", style="Custom.Treeview", selectmode="browse")
        self.tabla_historial.tag_configure("oddrow", background="#131a24")
        self.tabla_historial.tag_configure("evenrow", background="#151e28")
        
        anchos = {"Folio": 120, "Fecha y Hora": 260, "Total": 140, "Cajero": 180}
        for col in columnas:
            self.tabla_historial.heading(col, text=col)
            self.tabla_historial.column(col, width=anchos[col], anchor="center", stretch=True)

        scrollbar = ctk.CTkScrollbar(frame_tabla, command=self.tabla_historial.yview)
        self.tabla_historial.configure(yscrollcommand=scrollbar.set)

        self.tabla_historial.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

    def cargar_datos_historial(self):
        for i in self.tabla_historial.get_children():
            self.tabla_historial.delete(i)
        
        try:
            ventas = obtener_historial_ventas()
            for index, v in enumerate(ventas):
                tag = "evenrow" if index % 2 == 0 else "oddrow"
                self.tabla_historial.insert("", "end", values=(v[0], v[1], f"${v[2]:.2f}", v[3]), tags=(tag,))
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

        self.crear_boton(frame_controles, estilo="secundario", text="🔄 Refrescar", command=self.cargar_datos_empleados, width=100).pack(side="left", padx=5)
        self.crear_boton(frame_controles, estilo="exito", text="➕ Nuevo Cajero", command=self.ventana_nuevo_empleado, width=120).pack(side="left", padx=5)
        self.crear_boton(frame_controles, estilo="primario", text="📝 Editar Acceso", command=self.ventana_editar_empleado, width=120).pack(side="left", padx=5)
        self.crear_boton(frame_controles, estilo="peligro", text="🗑️ Dar de Baja", command=self.eliminar_empleado_gui, width=120).pack(side="right", padx=5)

        # --- MEJORA VISUAL: TABLA DE EMPLEADOS CON SCROLLBAR ---
        frame_tabla = ctk.CTkFrame(self.frame_empleados, fg_color=("#12181f", "#141c24"), corner_radius=18, border_width=1, border_color=("#243046", "#1f2d40"))
        frame_tabla.pack(side="top", fill="both", expand=True, padx=20, pady=5)

        columnas = ("ID", "Usuario", "Nombre Completo", "Rol")
        self.tabla_empleados = ttk.Treeview(frame_tabla, columns=columnas, show="headings", style="Custom.Treeview", selectmode="browse")
        self.tabla_empleados.tag_configure("oddrow", background="#131a24")
        self.tabla_empleados.tag_configure("evenrow", background="#151e28")
        
        anchos = {"ID": 80, "Usuario": 180, "Nombre Completo": 320, "Rol": 120}
        for col in columnas:
            self.tabla_empleados.heading(col, text=col)
            self.tabla_empleados.column(col, width=anchos[col], anchor="center", stretch=True)
        for col in columnas:
            self.tabla_empleados.heading(col, text=col)
            self.tabla_empleados.column(col, width=anchos[col], anchor="center")

        scrollbar = ctk.CTkScrollbar(frame_tabla, command=self.tabla_empleados.yview)
        self.tabla_empleados.configure(yscrollcommand=scrollbar.set)

        self.tabla_empleados.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

    def cargar_datos_empleados(self):
        for i in self.tabla_empleados.get_children(): self.tabla_empleados.delete(i)
        try:
            empleados = obtener_empleados() 
            for index, emp in enumerate(empleados):
                rol_str = "Admin" if str(emp[3]) == "1" else "Cajero"
                tag = "evenrow" if index % 2 == 0 else "oddrow"
                self.tabla_empleados.insert("", "end", values=(emp[0], emp[1], emp[2], rol_str), tags=(tag,))
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
        except:
            messagebox.showwarning("Cantidad inválida", "Ingresa una cantidad válida mayor a cero.", parent=self)
            return

        if cantidad_a_vender <= 0:
            messagebox.showwarning("Cantidad inválida", "La cantidad debe ser mayor a cero.", parent=self)
            return

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
        if not self.carrito_table:
            return
        for widget in self.carrito_table.winfo_children():
            widget.destroy()

        self.total_venta = 0.0
        agrupado = {}
        for p in self.carrito:
            if p.id not in agrupado:
                agrupado[p.id] = {"producto": p, "cantidad": 0}
            agrupado[p.id]["cantidad"] += 1

        if not agrupado:
            placeholder = ctk.CTkLabel(self.carrito_table, text="El carrito está vacío.", font=("Roboto", 14), text_color="gray")
            placeholder.pack(expand=True, fill="both", pady=0)
            cantidad_total = 0
        else:
            cantidad_total = 0
            for id_p, info in agrupado.items():
                producto = info["producto"]
                cantidad = info["cantidad"]
                subtotal = producto.precio * cantidad
                self.total_venta += subtotal
                cantidad_total += cantidad

                row = ctk.CTkFrame(self.carrito_table, fg_color=("#10131a", "#131a23"), corner_radius=14, border_width=1, border_color=("#243046", "#1f2d40"))
                row.pack(fill="x", padx=6, pady=6)
                row.grid_columnconfigure(1, weight=1)

                img_frame = ctk.CTkFrame(row, fg_color=("#121821", "#161d29"), corner_radius=12)
                img_frame.grid(row=0, column=0, padx=8, pady=10)
                img_label = ctk.CTkLabel(img_frame, text="", width=56, height=56)
                img_label.pack(expand=True, padx=6, pady=6)
                ruta_img = f"{self.carpeta_imagenes}/prod_{id_p}.png"
                if os.path.exists(ruta_img):
                    try:
                        img_pil = Image.open(ruta_img)
                        img_pil.thumbnail((56, 56))
                        img_ctk = ctk.CTkImage(light_image=img_pil, size=(56, 56))
                        img_label.configure(image=img_ctk, text="")
                        self._imagenes_tk.append(img_ctk)
                    except Exception:
                        img_label.configure(text="📷", font=("Roboto", 14), text_color="gray")
                else:
                    img_label.configure(text="📷", font=("Roboto", 14), text_color="gray")

                ctk.CTkLabel(row, text=producto.nombre, anchor="w", font=("Roboto", 12, "bold"), text_color="white").grid(row=0, column=1, sticky="w", padx=(12, 4), pady=10)
                ctk.CTkLabel(row, text=producto.talla, width=80, anchor="center", font=("Roboto", 12), text_color="#9aa5bf").grid(row=0, column=2, padx=4, pady=10)

                cantidad_frame = ctk.CTkFrame(row, fg_color=("#121822", "#151c28"), corner_radius=12)
                cantidad_frame.grid(row=0, column=3, padx=6, pady=10)
                qty_var = tk.StringVar(value=str(cantidad))
                qty_entry = ctk.CTkEntry(cantidad_frame, textvariable=qty_var, width=60, height=30, justify="center", font=("Roboto", 12), corner_radius=10, border_width=1)
                qty_entry.pack(padx=4, pady=4)
                qty_entry.bind("<FocusOut>", lambda e, id_p=id_p, var=qty_var: self._actualizar_cantidad_carrito(id_p, var.get()))
                qty_entry.bind("<Return>", lambda e, id_p=id_p, var=qty_var: self._actualizar_cantidad_carrito(id_p, var.get()))

                ctk.CTkLabel(row, text=f"${producto.precio:.2f}", width=100, anchor="e", font=("Roboto", 12), text_color="#8fb7ff").grid(row=0, column=4, padx=10, pady=10)
                ctk.CTkLabel(row, text=f"${subtotal:.2f}", width=100, anchor="e", font=("Roboto", 12, "bold"), text_color="#9d7cff").grid(row=0, column=5, padx=10, pady=10)
                ctk.CTkButton(row, text="✕", width=36, height=36, fg_color=("#c0392b", "#e74c3c"), hover_color=("#e74c3c", "#ff6b6b"), command=lambda id_p=id_p: self._eliminar_item_carrito(id_p), corner_radius=12).grid(row=0, column=6, padx=(10, 14), pady=10)

        self.label_total.configure(text=f"${self.total_venta:.2f}")
        if self.lbl_sub:
            self.lbl_sub.configure(text=f"${self.total_venta:.2f}")
        if self.lbl_total_articulos:
            self.lbl_total_articulos.configure(text=f"{cantidad_total} artículo(s)")
        self.actualizar_totales_ventas()

    def _actualizar_cantidad_carrito(self, id_producto, valor):
        try:
            nueva_cantidad = int(valor)
        except ValueError:
            self.actualizar_vista_carrito()
            return

        if nueva_cantidad <= 0:
            self.carrito = [p for p in self.carrito if p.id != id_producto]
            self.actualizar_vista_carrito()
            return

        items = [p for p in self.carrito if p.id == id_producto]
        if not items:
            return

        producto = items[0]
        if nueva_cantidad > producto.stock:
            messagebox.showwarning("Sin Stock", f"No hay suficientes unidades en stock. Disponible: {producto.stock}", parent=self)
            self.actualizar_vista_carrito()
            return

        nuevos = [p for p in self.carrito if p.id != id_producto]
        for _ in range(nueva_cantidad):
            nuevos.append(producto)
        self.carrito = nuevos
        self.actualizar_vista_carrito()

    def _eliminar_item_carrito(self, id_producto):
        self.carrito = [p for p in self.carrito if p.id != id_producto]
        self.actualizar_vista_carrito()

    def actualizar_totales_ventas(self):
        subtotal = self.total_venta
        try:
            descuento = float(self.entry_descuento.get()) if self.entry_descuento else 0.0
        except ValueError:
            descuento = 0.0
        descuento = max(0.0, descuento)

        descuento = min(descuento, subtotal)
        impuestos = 0.0
        total = max(0.0, subtotal - descuento)

        metodo = self.combo_pago.get() if self.combo_pago else "Efectivo"
        es_efectivo = metodo == "Efectivo"

        if es_efectivo:
            try:
                efectivo = float(self.entry_efectivo.get()) if self.entry_efectivo else 0.0
            except ValueError:
                efectivo = 0.0
        else:
            efectivo = 0.0

        cambio = efectivo - total if es_efectivo else 0.0
        cambio = cambio if cambio > 0 else 0.0

        if self.entry_efectivo:
            self.entry_efectivo.configure(state="normal" if es_efectivo else "disabled")
        if self.lbl_pago_activo:
            pago_text = f"Activo: {metodo}"
            pago_color = "#76ffb0" if es_efectivo else "#7c9cff"
            self.lbl_pago_activo.configure(text=pago_text, text_color=pago_color)
        if self.lbl_sub:
            self.lbl_sub.configure(text=f"${subtotal:.2f}")
        if self.lbl_descuento:
            self.lbl_descuento.configure(text=f"- ${descuento:.2f}")
        if self.label_total:
            self.label_total.configure(text=f"${total:.2f}")
        if self.lbl_cambio:
            self.lbl_cambio.configure(text=f"${cambio:.2f}")

        self.total_descuento = descuento
        self.total_impuestos = impuestos
        self.total_con_impuestos = total

    # -----------------------
    # Catálogo (ventas)
    # -----------------------
    def cargar_catalogo_productos(self):
        # Limpiar anteriores
        if hasattr(self, 'lista_cards_catalogo'):
            for w in self.lista_cards_catalogo:
                try: w.destroy()
                except: pass
        self.lista_cards_catalogo = []

        productos = obtener_reporte_existencias()
        if not productos:
            lbl = ctk.CTkLabel(self.catalogo_content, text="No hay productos en catálogo.", font=("Roboto", 14), text_color="gray")
            lbl.pack(pady=30)
            self.lista_cards_catalogo.append(lbl)
            return

        for p in productos:
            card = self.crear_card_producto_catalogo(p)
            self.lista_cards_catalogo.append(card)

        self._programar_reflow_catalogo()

    def crear_card_producto_catalogo(self, producto):
        id_p, nombre_p, talla_p, color_p, precio_p, stock_p = producto
        card = ctk.CTkFrame(self.catalogo_content, fg_color=("#1a1a1a", "#202020"), corner_radius=16, border_width=1, border_color=("#2c2c2c", "#333333"))
        card.configure(width=360, height=520)
        card.pack_propagate(False)

        frame_img = ctk.CTkFrame(card, fg_color=("#161616", "#1d1d1d"), corner_radius=14)
        frame_img.pack(padx=18, pady=(18, 12), fill="x")
        frame_img.pack_propagate(False)
        img_label = ctk.CTkLabel(frame_img, text="", height=220)
        img_label.pack(expand=True, fill="both")
        ruta_img = f"{self.carpeta_imagenes}/prod_{id_p}.png"
        if os.path.exists(ruta_img):
            try:
                img_pil = Image.open(ruta_img)
                img_pil.thumbnail((180, 180))
                img_ctk = ctk.CTkImage(light_image=img_pil, size=(180, 180))
                img_label.configure(image=img_ctk, text="")
                # keep reference
                self._imagenes_tk.append(img_ctk)
            except Exception:
                img_label.configure(text="📷", font=("Roboto", 18), text_color="gray")
        else:
            img_label.configure(text="📷", font=("Roboto", 18), text_color="gray")

        ctk.CTkLabel(card, text=nombre_p, font=("Roboto", 14, "bold"), text_color="white", wraplength=320).pack(anchor="w", padx=16, pady=(8, 0))
        ctk.CTkLabel(card, text=f"{talla_p} · {color_p}", font=("Roboto", 12), text_color="gray").pack(anchor="w", padx=16, pady=(6, 0))
        ctk.CTkLabel(card, text=f"Stock: {stock_p}", font=("Roboto", 12), text_color=("#7c93ff", "#9aa5ff")).pack(anchor="w", padx=16, pady=(6, 0))
        ctk.CTkLabel(card, text=f"${precio_p:.2f}", font=("Roboto", 18, "bold"), text_color="#7c93ff").pack(anchor="w", padx=16, pady=(10, 10))

        button_row = ctk.CTkFrame(card, fg_color="transparent")
        button_row.pack(fill="x", padx=16, pady=(0, 16))
        add_enabled = stock_p > 0
        btn_add = ctk.CTkButton(
            button_row,
            text="Agregar" if add_enabled else "Sin stock",
            command=(lambda p=producto: self._agregar_producto_directo(p)) if add_enabled else None,
            fg_color=("#6d7cff", "#6d7cff") if add_enabled else ("#444444", "#444444"),
            hover_color=("#7f6ef1", "#6f5fd3") if add_enabled else ("#444444", "#444444"),
            corner_radius=18,
            height=44,
            state="normal" if add_enabled else "disabled"
        )
        btn_add.pack(fill="x")

        return card

    def _agregar_producto_directo(self, producto, cantidad=1):
        if not producto:
            return

        _, nombre, talla, color, precio, stock = producto
        if stock <= 0:
            messagebox.showwarning("Sin stock", f"{nombre} no tiene existencias disponibles.", parent=self)
            return

        ya_en_carrito = sum(1 for p in self.carrito if p.id == producto[0])
        if ya_en_carrito + cantidad > stock:
            messagebox.showwarning(
                "Sin stock",
                f"No puedes agregar {cantidad} unidad(es).\n"
                f"Stock disponible: {stock}\n"
                f"En carrito: {ya_en_carrito}",
                parent=self
            )
            return

        for _ in range(cantidad):
            self.carrito.append(Producto(producto[0], producto[1], producto[2], producto[3], producto[4], producto[5]))
        self.actualizar_vista_carrito()

    def _programar_reflow_catalogo(self, event=None):
        if getattr(self, '_catalogo_reflow_id', None):
            self.after_cancel(self._catalogo_reflow_id)
        self._catalogo_reflow_id = self.after(120, self._reflow_catalogo)

    def _reflow_catalogo(self):
        # limpiar layout previo
        for w in self.catalogo_content.winfo_children():
            try:
                w.pack_forget()
            except Exception:
                try:
                    w.grid_forget()
                except Exception:
                    pass

        for card in getattr(self, 'lista_cards_catalogo', []):
            if isinstance(card, ctk.CTkLabel) and card.cget('text').startswith("No hay"):
                card.pack(pady=30)
                continue
            card.pack(side="left", fill="y", padx=10, pady=10)

    def cobrar_venta(self):
        if not self.carrito: return
        self.actualizar_totales_ventas()
        total = getattr(self, 'total_con_impuestos', self.total_venta)
        metodo = self.combo_pago.get() if self.combo_pago else "Efectivo"

        if metodo == "Efectivo":
            try:
                efectivo = float(self.entry_efectivo.get()) if self.entry_efectivo else 0.0
            except Exception:
                efectivo = 0.0
            if efectivo < total:
                messagebox.showwarning("Pago insuficiente", "El efectivo ingresado no cubre el total.", parent=self)
                return

        if not messagebox.askyesno("Confirmar", f"¿Cobrar ${total:.2f}?", parent=self): return
        
        folio = guardar_venta(self.usuario.id, self.carrito, total)
        if folio:
            descuento = getattr(self, 'total_descuento', 0.0)
            metodo_pago = self.combo_pago.get() if self.combo_pago else "Efectivo"
            efectivo = 0.0
            if metodo_pago == "Efectivo":
                try:
                    efectivo = float(self.entry_efectivo.get()) if self.entry_efectivo else 0.0
                except Exception:
                    efectivo = 0.0

            registrar_venta_en_excel(folio, self.total_venta, descuento, total, self.usuario.nombre, metodo_pago, self.carrito)
            generar_ticket_txt(folio, self.total_venta, descuento, total, self.usuario.nombre, metodo_pago, efectivo, self.carrito)
            
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

        mas_vendido = obtener_producto_mas_vendido_hoy()
        if mas_vendido:
            nombre_producto, cantidad_vendida = mas_vendido
            self.lbl_mas_vendido.configure(text=f"{nombre_producto} ({cantidad_vendida})")
        else:
            self.lbl_mas_vendido.configure(text="Ninguno")

        articulos_bajo = obtener_articulos_stock_bajo()
        if articulos_bajo:
            lista_items = [f"{nombre} ({stock})" for nombre, stock in articulos_bajo]
            self.lbl_items_stock_bajo.configure(text=", ".join(lista_items))
        else:
            self.lbl_items_stock_bajo.configure(text="Ninguno")

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

    def cerrar_sesion(self):
        if self.login_window:
            self.login_window.deiconify()
            self.login_window.lift()
            self.destroy()
        else:
            sys.exit()

    def salir_aplicacion(self):
        sys.exit()