from django.contrib import admin
from .models import Carrito, ItemCarrito

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'fecha_creacion', 'completado']
    list_filter = ['completado', 'fecha_creacion']

@admin.register(ItemCarrito)
class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ['carrito', 'producto', 'cantidad', 'fecha_agregado']
    list_filter = ['fecha_agregado']