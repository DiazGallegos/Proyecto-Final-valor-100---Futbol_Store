from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('cambiar-password/', views.cambiar_password, name='cambiar_password'),
]