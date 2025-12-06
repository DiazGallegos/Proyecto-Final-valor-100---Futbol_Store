from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Producto, Categoria

# ========== VISTAS PRINCIPALES ==========

def inicio(request):
    """Página principal de la tienda"""
    productos_destacados = Producto.objects.filter(destacado=True, activo=True)[:8]
    productos_nuevos = Producto.objects.filter(nuevo=True, activo=True)[:8]
    productos_oferta = Producto.objects.filter(
        activo=True,
        precio_original__isnull=False
    )[:4]
    categorias = Categoria.objects.all()[:6]
    
    context = {
        'productos_destacados': productos_destacados,
        'productos_nuevos': productos_nuevos,
        'productos_oferta': productos_oferta,
        'categorias': categorias,
    }
    return render(request, 'tienda/inicio.html', context)

def productos(request):
    """Lista todos los productos con paginación"""
    productos_list = Producto.objects.filter(activo=True).order_by('-fecha_creacion')
    categorias = Categoria.objects.all()
    
    # Filtrar por categoría si se especifica
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        productos_list = productos_list.filter(categoria_id=categoria_id)
    
    # Filtrar por marca si se especifica
    marca = request.GET.get('marca')
    if marca:
        productos_list = productos_list.filter(marca=marca)
    
    # Paginación
    paginator = Paginator(productos_list, 12)  # 12 productos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'productos': page_obj,
        'categorias': categorias,
        'categoria_actual': categoria_id,
        'marca_actual': marca,
    }
    return render(request, 'tienda/productos.html', context)

def detalle_producto(request, producto_id):
    """Detalle de un producto específico"""
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    
    # Productos relacionados (misma categoría)
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria,
        activo=True
    ).exclude(id=producto_id)[:4]
    
    # Productos de la misma marca
    productos_misma_marca = Producto.objects.filter(
        marca=producto.marca,
        activo=True
    ).exclude(id=producto_id)[:4]
    
    context = {
        'producto': producto,
        'productos_relacionados': productos_relacionados,
        'productos_misma_marca': productos_misma_marca,
    }
    return render(request, 'tienda/detalle_producto.html', context)

def productos_por_categoria(request, categoria_id):
    """Productos filtrados por categoría"""
    categoria = get_object_or_404(Categoria, id=categoria_id)
    productos_list = Producto.objects.filter(categoria=categoria, activo=True).order_by('-fecha_creacion')
    
    # Paginación
    paginator = Paginator(productos_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'categoria': categoria,
        'productos': page_obj,
    }
    return render(request, 'tienda/productos_categoria.html', context)

def categorias(request):
    """Lista todas las categorías"""
    categorias_list = Categoria.objects.all()
    return render(request, 'tienda/categorias.html', {'categorias': categorias_list})

def buscar_productos(request):
    """Búsqueda de productos"""
    query = request.GET.get('q', '').strip()
    productos_list = Producto.objects.filter(activo=True)
    
    if query:
        productos_list = productos_list.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(categoria__nombre__icontains=query) |
            Q(marca__icontains=query)
        ).distinct()
    
    # Paginación
    paginator = Paginator(productos_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'productos': page_obj,
        'query': query,
        'resultados_count': productos_list.count(),
    }
    return render(request, 'tienda/buscar.html', context)

def productos_oferta(request):
    """Productos en oferta"""
    productos_oferta = Producto.objects.filter(
        activo=True,
        precio_original__isnull=False
    ).order_by('-fecha_creacion')
    
    # Paginación
    paginator = Paginator(productos_oferta, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'productos': page_obj,
        'titulo': 'Productos en Oferta',
    }
    return render(request, 'tienda/ofertas.html', context)

def productos_nuevos(request):
    """Productos nuevos"""
    productos_nuevos = Producto.objects.filter(nuevo=True, activo=True).order_by('-fecha_creacion')
    
    # Paginación
    paginator = Paginator(productos_nuevos, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'productos': page_obj,
        'titulo': 'Productos Nuevos',
    }
    return render(request, 'tienda/novedades.html', context)

def productos_destacados(request):
    """Productos destacados"""
    productos_destacados = Producto.objects.filter(destacado=True, activo=True).order_by('-fecha_creacion')
    
    # Paginación
    paginator = Paginator(productos_destacados, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'productos': page_obj,
        'titulo': 'Productos Destacados',
    }
    return render(request, 'tienda/destacados.html', context)

# ========== VISTAS ADICIONALES ==========

def about(request):
    """Página Acerca de"""
    context = {
        'titulo': 'Acerca de FútbolStore',
    }
    return render(request, 'tienda/about.html', context)

def contacto(request):
    """Página de Contacto"""
    context = {
        'titulo': 'Contacto',
    }
    return render(request, 'tienda/contacto.html', context)

def condiciones(request):
    """Términos y condiciones"""
    return render(request, 'tienda/condiciones.html')

def privacidad(request):
    """Política de privacidad"""
    return render(request, 'tienda/privacidad.html')