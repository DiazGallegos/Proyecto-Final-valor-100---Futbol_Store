from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .models import Perfil
from pedidos.models import Pedido
from .forms import RegistroFormPersonalizado

# ========== VISTAS DE AUTENTICACIÓN ==========

def registro(request):
    """Vista para registrar un nuevo usuario"""
    if request.method == 'POST':
        form = RegistroFormPersonalizado(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, '¡Registro exitoso! Bienvenido a la tienda.')
                return redirect('/')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = RegistroFormPersonalizado()
    
    return render(request, 'usuarios/registro.html', {'form': form})

def login_view(request):
    """Vista para iniciar sesión"""
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}!')
            return redirect('/')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    else:
        form = AuthenticationForm()
    
    return render(request, 'usuarios/login.html', {'form': form})

def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente')
    return redirect('/')

# ========== VISTAS DE PERFIL ==========

@login_required
def perfil(request):
    """Vista para ver y editar el perfil del usuario"""
    try:
        perfil_usuario = request.user.perfil
    except Perfil.DoesNotExist:
        perfil_usuario = Perfil.objects.create(
            usuario=request.user,
            telefono='',
            direccion='',
            ciudad='',
            codigo_postal=''
        )
    
    if request.method == 'POST':
        # Actualizar información del usuario
        if 'first_name' in request.POST:
            request.user.first_name = request.POST['first_name']
        if 'last_name' in request.POST:
            request.user.last_name = request.POST['last_name']
        if 'email' in request.POST:
            request.user.email = request.POST['email']
        request.user.save()
        
        # Actualizar perfil
        if 'telefono' in request.POST:
            perfil_usuario.telefono = request.POST['telefono']
        if 'direccion' in request.POST:
            perfil_usuario.direccion = request.POST['direccion']
        if 'ciudad' in request.POST:
            perfil_usuario.ciudad = request.POST['ciudad']
        if 'codigo_postal' in request.POST:
            perfil_usuario.codigo_postal = request.POST['codigo_postal']
        
        if 'avatar' in request.FILES:
            perfil_usuario.avatar = request.FILES['avatar']
        
        perfil_usuario.save()
        
        # Cambiar contraseña
        nueva_password = request.POST.get('nueva_password', '')
        confirmar_password = request.POST.get('confirmar_password', '')
        
        if nueva_password and confirmar_password:
            if nueva_password == confirmar_password:
                if len(nueva_password) >= 3:
                    request.user.set_password(nueva_password)
                    request.user.save()
                    update_session_auth_hash(request, request.user)
                    messages.success(request, 'Contraseña actualizada correctamente')
                else:
                    messages.error(request, 'La contraseña debe tener al menos 3 caracteres')
            else:
                messages.error(request, 'Las contraseñas no coinciden')
        
        messages.success(request, 'Perfil actualizado correctamente')
        return redirect('usuarios:perfil')
    
    # Obtener pedidos del usuario
    try:
        pedidos = Pedido.objects.filter(cliente=request.user).order_by('-fecha_pedido')[:10]
        total_pedidos = Pedido.objects.filter(cliente=request.user).count()
    except Exception as e:
        pedidos = []
        total_pedidos = 0
    
    context = {
        'perfil': perfil_usuario,
        'pedidos': pedidos,
        'total_pedidos': total_pedidos,
    }
    
    return render(request, 'usuarios/perfil.html', context)

@login_required
def mis_pedidos(request):
    """Vista para ver todos los pedidos del usuario"""
    try:
        pedidos = Pedido.objects.filter(cliente=request.user).order_by('-fecha_pedido')
    except:
        pedidos = []
    
    context = {
        'pedidos': pedidos,
    }
    
    return render(request, 'usuarios/pedidos.html', context)

@login_required
def cambiar_password(request):
    """Vista para cambiar la contraseña desde el perfil"""
    if request.method == 'POST':
        nueva_password = request.POST.get('nueva_password')
        confirmar_password = request.POST.get('confirmar_password')
        
        if nueva_password == confirmar_password:
            if len(nueva_password) >= 3:
                request.user.set_password(nueva_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Contraseña actualizada correctamente')
                return redirect('usuarios:perfil')
            else:
                messages.error(request, 'La contraseña debe tener al menos 3 caracteres')
        else:
            messages.error(request, 'Las contraseñas no coinciden')
    
    return render(request, 'usuarios/cambiar_password.html')