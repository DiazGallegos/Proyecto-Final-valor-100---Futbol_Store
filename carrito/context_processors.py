# carrito/context_processors.py

from .models import Carrito

def carrito(request):
    """Context processor para mostrar cantidad en navbar"""
    try:
        if request.user.is_authenticated:
            carrito = Carrito.objects.filter(
                usuario=request.user,
                completado=False
            ).first()
            if carrito:
                return {
                    'carrito_cantidad': carrito.cantidad_total,
                    'carrito_total': carrito.total,
                }
        else:
            carrito_id = request.session.get('carrito_id')
            if carrito_id:
                carrito = Carrito.objects.filter(id=carrito_id, completado=False).first()
                if carrito:
                    return {
                        'carrito_cantidad': carrito.cantidad_total,
                        'carrito_total': carrito.total,
                    }
    except:
        pass
    
    return {
        'carrito_cantidad': 0,
        'carrito_total': 0,
    }