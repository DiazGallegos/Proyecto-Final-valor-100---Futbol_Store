from django import template
from django.apps import apps

register = template.Library()

@register.simple_tag
def get_categorias():
    """
    Obtiene todas las categorías para el menú
    """
    try:
        # Intenta importar el modelo Categoria
        Categoria = apps.get_model('tienda', 'Categoria')
        return Categoria.objects.all()
    except:
        # Si no existe, retorna lista vacía para evitar errores
        return []
