from django.urls import path
from . import views

app_name = 'carrito'

urlpatterns = [
    path('', views.ver_carrito, name='ver_carrito'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),  # Cambiado aquí
    path('actualizar/<int:producto_id>/', views.actualizar_cantidad, name='actualizar'),
    path('eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar'),
    path('vaciar/', views.vaciar_carrito, name='vaciar'),
    path('procesar-pago/', views.procesar_pago, name='procesar_pago'),
    path('confirmacion/', views.confirmacion, name='confirmacion'),
]