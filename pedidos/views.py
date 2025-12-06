# pedidos/views.py - VERSIÓN COMPLETA CORREGIDA
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime
import re
import uuid
from .models import Pedido, ItemPedido
from tienda.models import Producto

# ========== FUNCIONES DE VALIDACIÓN ==========
def validar_tarjeta(numero, fecha_vencimiento, cvv):
    """Validar datos de tarjeta de crédito"""
    errores = []
    
    # Validar número de tarjeta (16 dígitos)
    numero_limpio = re.sub(r'\D', '', numero)
    if len(numero_limpio) != 16 or not numero_limpio.isdigit():
        errores.append("El número de tarjeta debe tener 16 dígitos")
    
    # Validar fecha de vencimiento (MM/YY)
    fecha_pattern = re.match(r'(\d{2})/(\d{2})', fecha_vencimiento)
    if not fecha_pattern:
        errores.append("Formato de fecha inválido. Use MM/YY")
    else:
        mes = int(fecha_pattern.group(1))
        anio = int(fecha_pattern.group(2))
        
        # Validar mes
        if mes < 1 or mes > 12:
            errores.append("Mes inválido (1-12)")
        
        # Validar que no sea fecha pasada
        hoy = timezone.now()
        anio_completo = 2000 + anio
        
        # Último día del mes de vencimiento
        from calendar import monthrange
        ultimo_dia_mes = monthrange(anio_completo, mes)[1]
        fecha_vencimiento_obj = datetime(anio_completo, mes, ultimo_dia_mes)
        
        if fecha_vencimiento_obj.date() < hoy.date():
            errores.append("La tarjeta está vencida")
    
    # Validar CVV (3-4 dígitos)
    if not re.match(r'^\d{3,4}$', cvv):
        errores.append("CVV inválido (3-4 dígitos)")
    
    return errores

# ========== VISTAS PRINCIPALES ==========
@login_required
def crear_pedido(request):
    """Crear pedido con pago por tarjeta"""
    carrito = request.session.get('carrito', {})
    
    if not carrito:
        messages.error(request, 'Tu carrito está vacío')
        return redirect('carrito:ver_carrito')
    
    # Calcular total
    total = 0
    for item_id, item_data in carrito.items():
        if isinstance(item_data, dict):
            precio = float(item_data.get('precio', 0))
            cantidad = int(item_data.get('cantidad', 1))
            total += precio * cantidad
    
    if request.method == 'POST':
        # Obtener datos del formulario
        numero_tarjeta = request.POST.get('numero_tarjeta', '').strip()
        fecha_vencimiento = request.POST.get('fecha_vencimiento', '').strip()
        cvv = request.POST.get('cvv', '').strip()
        nombre_titular = request.POST.get('nombre_titular', '').strip()
        direccion_envio = request.POST.get('direccion', '').strip()
        ciudad = request.POST.get('ciudad', '').strip()
        codigo_postal = request.POST.get('codigo_postal', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        notas = request.POST.get('notas', '').strip()
        
        # Validar campos obligatorios
        campos_obligatorios = {
            'numero_tarjeta': 'Número de tarjeta',
            'fecha_vencimiento': 'Fecha de vencimiento',
            'cvv': 'CVV',
            'nombre_titular': 'Nombre del titular',
            'direccion': 'Dirección de envío',
            'ciudad': 'Ciudad',
            'codigo_postal': 'Código postal',
            'telefono': 'Teléfono',
        }
        
        errores = []
        for campo, nombre in campos_obligatorios.items():
            valor = request.POST.get(campo, '').strip()
            if not valor:
                errores.append(f'{nombre} es obligatorio')
        
        if errores:
            for error in errores:
                messages.error(request, error)
            return redirect('pedidos:crear_pedido')
        
        # Validar tarjeta
        errores_tarjeta = validar_tarjeta(numero_tarjeta, fecha_vencimiento, cvv)
        if errores_tarjeta:
            for error in errores_tarjeta:
                messages.error(request, error)
            return redirect('pedidos:crear_pedido')
        
        # Validar teléfono
        telefono_limpio = re.sub(r'\D', '', telefono)
        if len(telefono_limpio) != 10:
            messages.error(request, 'Teléfono inválido (debe tener 10 dígitos)')
            return redirect('pedidos:crear_pedido')
        
        # Validar código postal
        if not re.match(r'^\d{5,6}$', codigo_postal):
            messages.error(request, 'Código postal inválido')
            return redirect('pedidos:crear_pedido')
        
        try:
            # Crear pedido
            pedido = Pedido.objects.create(
                cliente=request.user,
                total=total,
                estado='PROCESANDO',
                metodo_pago='TARJETA',
                direccion_envio=direccion_envio,
                ciudad=ciudad,
                codigo_postal=codigo_postal,
                telefono=telefono_limpio,
                notas=notas,
                pagado=True,
                ultimos_digitos_tarjeta=numero_tarjeta[-4:],
                nombre_titular=nombre_titular,
                fecha_pago=timezone.now(),
                codigo_transaccion=f"TXN-{uuid.uuid4().hex[:12].upper()}"
            )
            
            # Crear items del pedido
            for item_id, item_data in carrito.items():
                if isinstance(item_data, dict):
                    producto_id = item_data.get('producto_id')
                    if producto_id:
                        producto = get_object_or_404(Producto, id=producto_id)
                        
                        ItemPedido.objects.create(
                            pedido=pedido,
                            producto=producto,
                            cantidad=item_data.get('cantidad', 1),
                            precio=item_data.get('precio', 0)
                        )
            
            # Vaciar carrito
            del request.session['carrito']
            request.session.modified = True
            
            # Mensaje de éxito
            messages.success(request, f'''
            ✅ ¡Pago Exitoso!
            Pedido #{pedido.id} - ${total:,.0f}
            Tarjeta: **** **** **** {pedido.ultimos_digitos_tarjeta}
            ''')
            
            return redirect('usuarios:mis_pedidos')
            
        except Exception as e:
            messages.error(request, f'Error al procesar el pago: {str(e)}')
            return redirect('pedidos:crear_pedido')
    
    # GET request - Mostrar formulario
    total_recalculado = 0
    carrito_valido = {}
    
    for item_id, item_data in carrito.items():
        if isinstance(item_data, dict):
            precio = float(item_data.get('precio', 0))
            cantidad = int(item_data.get('cantidad', 1))
            total_recalculado += precio * cantidad
            carrito_valido[item_id] = item_data
    
    context = {
        'carrito': carrito_valido,
        'total': total_recalculado,
        'items_count': len(carrito_valido),
        'ano_actual': timezone.now().year % 100,
        'mes_actual': timezone.now().month,
    }
    
    return render(request, 'pedidos/crear_pedido.html', context)

@login_required
def mis_pedidos(request):
    """Ver todos los pedidos del usuario"""
    pedidos = Pedido.objects.filter(cliente=request.user).order_by('-fecha_pedido')
    
    context = {
        'pedidos': pedidos
    }
    
    return render(request, 'pedidos/mis_pedidos.html', context)

@login_required
def detalle_pedido(request, pedido_id):
    """Ver detalle de un pedido específico"""
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    items = pedido.items.all()
    
    context = {
        'pedido': pedido,
        'items': items
    }
    
    return render(request, 'pedidos/detalle_pedido.html', context)

@login_required
def cancelar_pedido(request, pedido_id):
    """Cancelar un pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    
    if pedido.estado in ['PENDIENTE', 'PROCESANDO']:
        pedido.estado = 'CANCELADO'
        pedido.save()
        messages.success(request, f'Pedido #{pedido_id} cancelado exitosamente')
    else:
        messages.error(request, 'No se puede cancelar este pedido en su estado actual')
    
    return redirect('usuarios:mis_pedidos')