# modelos/producto.py
class Producto:
    def __init__(self, id, nombre, talla, color, precio, stock):
        self.id = id
        self.nombre = nombre
        self.talla = talla
        self.color = color
        self.precio = precio
        self.stock = stock