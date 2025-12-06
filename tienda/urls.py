from django.urls import path
from . import views

app_name = 'tienda'

urlpatterns = [
    # ========== PÁGINAS PRINCIPALES ==========
    # Página principal - IMPORTANTE: se llama 'inicio'
    path('', views.inicio, name='inicio'),
    
    # ========== PRODUCTOS ==========
    # Lista de todos los productos
    path('productos/', views.productos, name='productos'),
    
    # Detalle de un producto específico
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    
    # ========== CATEGORÍAS ==========
    # Lista todas las categorías
    path('categorias/', views.categorias, name='categorias'),
    
    # Productos por categoría específica
    path('categoria/<int:categoria_id>/', views.productos_por_categoria, name='productos_por_categoria'),
    
    # ========== BÚSQUEDA ==========
    # Búsqueda de productos
    path('buscar/', views.buscar_productos, name='buscar'),
    
    # ========== SECCIONES ESPECIALES ==========
    # Productos en oferta
    path('ofertas/', views.productos_oferta, name='ofertas'),
    
    # Productos nuevos
    path('novedades/', views.productos_nuevos, name='novedades'),
    
    # Productos destacados
    path('destacados/', views.productos_destacados, name='destacados'),
    
    # ========== PÁGINAS INFORMATIVAS ==========
    # Acerca de
    path('about/', views.about, name='about'),
    
    # Contacto
    path('contacto/', views.contacto, name='contacto'),
    
    # Términos y condiciones
    path('condiciones/', views.condiciones, name='condiciones'),
    
    # Política de privacidad
    path('privacidad/', views.privacidad, name='privacidad'),
]