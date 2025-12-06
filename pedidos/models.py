# pedidos/models.py - VERSIÓN COMPLETA
from django.db import models
from django.contrib.auth.models import User
from tienda.models import Producto

class Pedido(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('PROCESANDO', 'Procesando'),
        ('ENVIADO', 'Enviado'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    METODOS_PAGO = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA', 'Tarjeta'),
        ('TRANSFERENCIA', 'Transferencia'),
    ]
    
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, default='EFECTIVO')
    direccion_envio = models.TextField()
    ciudad = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10)
    telefono = models.CharField(max_length=20)
    notas = models.TextField(blank=True)
    pagado = models.BooleanField(default=False)
    
    # Campos para pago con tarjeta
    ultimos_digitos_tarjeta = models.CharField(max_length=4, blank=True, null=True)
    nombre_titular = models.CharField(max_length=100, blank=True, null=True)
    fecha_pago = models.DateTimeField(blank=True, null=True)
    codigo_transaccion = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.username} - ${self.total}"
    
    @property
    def estado_color(self):
        """Devuelve clase CSS según el estado"""
        colores = {
            'PENDIENTE': 'warning',
            'PROCESANDO': 'info',
            'ENVIADO': 'primary',
            'ENTREGADO': 'success',
            'CANCELADO': 'danger',
        }
        return colores.get(self.estado, 'secondary')
    
    @property
    def metodo_pago_icono(self):
        """Devuelve icono según método de pago"""
        iconos = {
            'EFECTIVO': 'fas fa-money-bill-wave',
            'TARJETA': 'fas fa-credit-card',
            'TRANSFERENCIA': 'fas fa-university',
        }
        return iconos.get(self.metodo_pago, 'fas fa-question-circle')
    
    @property
    def cantidad_total_items(self):
        """Devuelve la cantidad total de productos en el pedido"""
        return sum(item.cantidad for item in self.items.all())
    
    @property
    def fecha_formateada(self):
        """Devuelve fecha formateada"""
        from django.utils import timezone
        from django.utils.formats import date_format
        return date_format(timezone.localtime(self.fecha_pedido), "d/m/Y H:i")
    
    class Meta:
        ordering = ['-fecha_pedido']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

class ItemPedido(models.Model):
    pedido = models.ForeignKey('Pedido', related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        if self.producto:
            return f"{self.cantidad} x {self.producto.nombre}"
        return f"{self.cantidad} x Producto eliminado"
    
    @property
    def subtotal(self):
        """Calcula subtotal del item"""
        return self.precio * self.cantidad
    
    @property
    def subtotal_formateado(self):
        """Devuelve subtotal formateado como string"""
        return f"${self.subtotal:,.0f}"
    
    @property
    def precio_formateado(self):
        """Devuelve precio formateado como string"""
        return f"${self.precio:,.0f}"
    
    @property
    def nombre_producto(self):
        """Devuelve nombre del producto o placeholder"""
        if self.producto:
            return self.producto.nombre
        return "Producto no disponible"
    
    class Meta:
        verbose_name = 'Ítem del pedido'
        verbose_name_plural = 'Ítems del pedido'