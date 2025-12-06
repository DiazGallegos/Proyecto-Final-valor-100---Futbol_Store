from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from tienda.models import Producto
from datetime import datetime
from decimal import Decimal
from django.http import JsonResponse

def ver_carrito(request):
    """Vista para mostrar el carrito"""
    carrito = request.session.get('carrito', {})
    
    productos = []
    total = Decimal('0.00')
    cantidad_total = 0
    
    for producto_id_str, item in carrito.items():
        try:
            producto_id = int(producto_id_str)
            producto = get_object_or_404(Producto, id=producto_id)
            cantidad = item.get('cantidad', 1)
            
            precio_decimal = Decimal(str(producto.precio))
            subtotal = precio_decimal * cantidad
            
            productos.append({
                'id': producto_id,
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal,
                'precio_unitario': precio_decimal
            })
            
            total += subtotal
            cantidad_total += cantidad
            
        except (ValueError, Producto.DoesNotExist):
            if producto_id_str in carrito:
                del carrito[producto_id_str]
                request.session.modified = True
            continue
    
    iva = total * Decimal('0.16')
    total_con_iva = total + iva
    
    context = {
        'productos': productos,
        'total': total,
        'iva': iva,
        'total_con_iva': total_con_iva,
        'cantidad_total': cantidad_total,
        'carrito_vacio': len(productos) == 0
    }
    
    return render(request, 'carrito/carrito.html', context)

def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    if 'carrito' not in request.session:
        request.session['carrito'] = {}
    
    carrito = request.session['carrito']
    producto_key = str(producto_id)
    
    # Verificar si es una petición AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if producto.stock < 1:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': f'¡{producto.nombre} está agotado!'
            })
        messages.error(request, f'¡{producto.nombre} está agotado!')
        return redirect('tienda:productos')
    
    success_message = ""
    success = True
    
    if producto_key in carrito:
        nueva_cantidad = carrito[producto_key]['cantidad'] + 1
        if nueva_cantidad > producto.stock:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': f'Solo hay {producto.stock} unidades disponibles'
                })
            messages.warning(request, f'Solo hay {producto.stock} unidades disponibles')
            success = False
        else:
            carrito[producto_key]['cantidad'] = nueva_cantidad
            success_message = f'¡{producto.nombre} agregado al carrito! (Total: {nueva_cantidad})'
    else:
        carrito[producto_key] = {
            'cantidad': 1, 
            'nombre': producto.nombre, 
            'precio': str(float(producto.precio))
        }
        success_message = f'¡{producto.nombre} agregado al carrito!'
    
    request.session.modified = True
    
    # Calcular cantidad total en el carrito
    cantidad_carrito = sum(item.get('cantidad', 0) for item in carrito.values())
    
    # Si es AJAX, devolver JSON
    if is_ajax:
        return JsonResponse({
            'success': True,
            'message': success_message,
            'carrito_count': cantidad_carrito,
            'producto_nombre': producto.nombre,
            'producto_id': producto_id
        })
    
    # Si no es AJAX, comportamiento normal
    if success_message:
        messages.success(request, success_message)
    return redirect(request.GET.get('next', 'tienda:productos'))

def actualizar_cantidad(request, producto_id):
    nueva_cantidad = request.GET.get('cantidad', 1)
    
    try:
        nueva_cantidad = int(nueva_cantidad)
    except ValueError:
        nueva_cantidad = 1
    
    carrito = request.session.get('carrito', {})
    producto_key = str(producto_id)
    
    if producto_key in carrito:
        producto = get_object_or_404(Producto, id=producto_id)
        
        if nueva_cantidad > 0 and nueva_cantidad <= producto.stock:
            carrito[producto_key]['cantidad'] = nueva_cantidad
            messages.success(request, f'Cantidad actualizada a {nueva_cantidad}')
        elif nueva_cantidad > producto.stock:
            carrito[producto_key]['cantidad'] = producto.stock
            messages.warning(request, f'Solo hay {producto.stock} unidades disponibles')
        else:
            del carrito[producto_key]
            messages.info(request, 'Producto eliminado del carrito')
        
        request.session['carrito'] = carrito
        request.session.modified = True
    
    return redirect('carrito:ver_carrito')

def eliminar_del_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    producto_key = str(producto_id)
    
    if producto_key in carrito:
        producto_nombre = carrito[producto_key].get('nombre', 'Producto')
        del carrito[producto_key]
        request.session['carrito'] = carrito
        request.session.modified = True
        messages.success(request, f'¡{producto_nombre} eliminado!')
    
    return redirect('carrito:ver_carrito')

def vaciar_carrito(request):
    if 'carrito' in request.session:
        del request.session['carrito']
        messages.info(request, 'Carrito vaciado correctamente.')
    
    return redirect('carrito:ver_carrito')

@login_required
def procesar_pago(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('carrito:ver_carrito')
    
    if request.method == 'POST':
        numero_tarjeta = request.POST.get('numero_tarjeta', '').replace(' ', '')
        fecha_expiracion = request.POST.get('fecha_expiracion', '')
        cvc = request.POST.get('cvc', '')
        nombre_tarjeta = request.POST.get('nombre_tarjeta', '').upper()
        
        errores = []
        
        # Validar número de tarjeta (simplificado para pruebas)
        if not numero_tarjeta or len(numero_tarjeta) < 13:
            errores.append('Número de tarjeta inválido.')
        
        # Validar fecha de expiración (PERMITIR CUALQUIER FECHA FUTURA PARA PRUEBAS)
        try:
            if '/' not in fecha_expiracion:
                raise ValueError
            
            mes_str, ano_str = fecha_expiracion.split('/')
            mes = int(mes_str)
            ano = int(ano_str)
            
            if mes < 1 or mes > 12:
                errores.append('Mes inválido. Debe ser entre 01 y 12.')
            
            # Para pruebas: aceptar cualquier año futuro
            if ano < 24:  # Si es menor a 2024, considerar vencida
                errores.append('La tarjeta está vencida.')
                
        except (ValueError, IndexError):
            errores.append('Fecha de expiración inválida. Use formato MM/AA.')
        
        # Validar CVC
        if not cvc.isdigit() or len(cvc) not in [3, 4]:
            errores.append('CVC inválido. Debe tener 3-4 dígitos.')
        
        # Validar nombre
        if not nombre_tarjeta or len(nombre_tarjeta) < 3:
            errores.append('Nombre inválido.')
        
        # Validar términos
        if not request.POST.get('terminos'):
            errores.append('Debes aceptar los términos y condiciones.')
        
        # Si hay errores, mostrarlos
        if errores:
            for error in errores:
                messages.error(request, error)
            return redirect('carrito:ver_carrito')
        
        # Calcular total
        total = Decimal('0.00')
        for producto_id_str, item in carrito.items():
            try:
                producto = Producto.objects.get(id=int(producto_id_str))
                cantidad = item.get('cantidad', 1)
                precio_decimal = Decimal(str(producto.precio))
                total += precio_decimal * cantidad
            except:
                continue
        
        iva = total * Decimal('0.16')
        total_con_iva = total + iva
        
        # Vaciar carrito después del pago
        if 'carrito' in request.session:
            del request.session['carrito']
        
        # Guardar información del pago
        request.session['ultimo_pago'] = {
            'total': float(total_con_iva),
            'fecha': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'metodo': 'Tarjeta de Crédito',
            'referencia': f'PAGO-{datetime.now().strftime("%Y%m%d%H%M%S")}'
        }
        
        messages.success(request, '¡Pago procesado exitosamente! Tu pedido ha sido confirmado.')
        return redirect('carrito:confirmacion')
    
    return redirect('carrito:ver_carrito')

def confirmacion(request):
    ultimo_pago = request.session.get('ultimo_pago', {})
    
    context = {
        'total': ultimo_pago.get('total', 0),
        'fecha': ultimo_pago.get('fecha', ''),
        'metodo': ultimo_pago.get('metodo', 'Tarjeta'),
        'referencia': ultimo_pago.get('referencia', ''),
    }
    
    return render(request, 'carrito/confirmacion.html', context)