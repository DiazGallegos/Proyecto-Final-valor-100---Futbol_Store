# tienda/models.py (COMPLETO Y CORREGIDO)
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='categorias/', blank=True, null=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

class Producto(models.Model):
    TALLAS = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Doble Extra Large'),
    ]
    
    MARCAS = [
        ('NIKE', 'Nike'),
        ('ADIDAS', 'Adidas'),
        ('PUMA', 'Puma'),
        ('UMBRO', 'Umbro'),
        ('NEW_BALANCE', 'New Balance'),
        ('REEBOK', 'Reebok'),
        ('JOMA', 'Joma'),
        ('KELME', 'Kelme'),
    ]
    
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_original = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    marca = models.CharField(max_length=20, choices=MARCAS, default='NIKE')
    talla = models.CharField(max_length=5, choices=TALLAS, default='M')
    stock = models.PositiveIntegerField(default=0)
    
    # SOLO 1 IMAGEN
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    
    destacado = models.BooleanField(default=False)
    nuevo = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nombre} - ${self.precio}"
    
    def en_oferta(self):
        return self.precio_original is not None and self.precio < self.precio_original
    
    def porcentaje_descuento(self):
        if self.precio_original and self.precio < self.precio_original:
            descuento = ((self.precio_original - self.precio) / self.precio_original) * 100
            return round(descuento, 0)
        return 0
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-fecha_creacion']

class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20)
    direccion = models.TextField()
    ciudad = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.usuario.get_full_name()}"
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'