from django.db import models
from django.contrib.auth.models import User
from tienda.models import Producto

class Carrito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=100, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    completado = models.BooleanField(default=False)
    
    def __str__(self):
        if self.usuario:
            return f"Carrito de {self.usuario.username}"
        return f"Carrito (sesión)"
    
    @property
    def total(self):
        total = 0
        for item in self.items.all():
            total += item.subtotal
        return total
    
    @property
    def cantidad_total(self):
        cantidad = 0
        for item in self.items.all():
            cantidad += item.cantidad
        return cantidad

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
    
    @property
    def subtotal(self):
        return self.producto.precio * self.cantidad