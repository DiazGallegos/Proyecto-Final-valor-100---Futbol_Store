from django.contrib import admin
from .models import Pedido, ItemPedido

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 1

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'fecha_pedido', 'total', 'estado', 'pagado']
    list_filter = ['estado', 'pagado', 'fecha_pedido', 'metodo_pago']
    search_fields = ['cliente__username', 'direccion_envio']
    inlines = [ItemPedidoInline]

@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'producto', 'cantidad', 'precio']