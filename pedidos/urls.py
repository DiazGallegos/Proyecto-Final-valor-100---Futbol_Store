# pedidos/urls.py
from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    # Crear pedido desde carrito
    path('crear/', views.crear_pedido, name='crear_pedido'),
    
    # Ver pedidos
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    
    # Detalle de pedido
    path('<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    
    # Cancelar pedido
    path('<int:pedido_id>/cancelar/', views.cancelar_pedido, name='cancelar_pedido'),
]