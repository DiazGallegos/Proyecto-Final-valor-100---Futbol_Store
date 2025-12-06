# usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Perfil

# Define un admin inline para Perfil
class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil'
    fields = [
        'tipo_usuario', 
        'telefono', 
        'direccion', 
        'ciudad', 
        'codigo_postal',
        'fecha_nacimiento',
        'avatar'
    ]

# Define un nuevo User admin
class UserAdmin(BaseUserAdmin):
    inlines = (PerfilInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_tipo_usuario')
    list_filter = ('is_staff', 'is_superuser', 'groups')
    
    def get_tipo_usuario(self, obj):
        try:
            return obj.perfil.get_tipo_usuario_display()
        except:
            return "Sin perfil"
    get_tipo_usuario.short_description = 'Tipo de Usuario'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'get_email', 'tipo_usuario', 'telefono', 'ciudad']
    list_filter = ['tipo_usuario', 'ciudad']
    search_fields = ['usuario__username', 'usuario__email', 'telefono']
    list_editable = ['tipo_usuario', 'telefono']
    
    def get_email(self, obj):
        return obj.usuario.email
    get_email.short_description = 'Email'