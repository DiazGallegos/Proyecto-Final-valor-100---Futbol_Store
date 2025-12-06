from django.contrib import admin
from .models import Categoria, Producto, Cliente

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'id']
    search_fields = ['nombre']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'categoria', 'marca', 'stock', 'activo', 'destacado']
    list_filter = ['categoria', 'marca', 'activo', 'destacado', 'nuevo']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['precio', 'stock', 'activo', 'destacado']

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'telefono', 'ciudad', 'fecha_registro']
    search_fields = ['usuario__username', 'usuario__email', 'ciudad']