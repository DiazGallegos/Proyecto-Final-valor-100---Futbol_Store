from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Perfil(models.Model):
    TIPOS_USUARIO = [
        ('CLIENTE', 'Cliente'),
        ('ADMIN', 'Administrador'),
        ('EMPLEADO', 'Empleado'),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    tipo_usuario = models.CharField(max_length=20, choices=TIPOS_USUARIO, default='CLIENTE')
    telefono = models.CharField(max_length=20, blank=True, null=True, default='')
    direccion = models.TextField(blank=True, null=True, default='')
    ciudad = models.CharField(max_length=100, blank=True, null=True, default='')
    codigo_postal = models.CharField(max_length=10, blank=True, null=True, default='')
    fecha_nacimiento = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"
    
    def es_admin(self):
        return self.tipo_usuario == 'ADMIN'
    
    def es_empleado(self):
        return self.tipo_usuario == 'EMPLEADO'
    
    def es_cliente(self):
        return self.tipo_usuario == 'CLIENTE'

# Signals para crear perfil automáticamente
@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(
            usuario=instance,
            telefono='',  # <-- VALOR POR DEFECTO
            direccion='', # <-- VALOR POR DEFECTO
            ciudad='',    # <-- VALOR POR DEFECTO
            codigo_postal=''  # <-- VALOR POR DEFECTO
        )

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    try:
        instance.perfil.save()
    except Perfil.DoesNotExist:
        Perfil.objects.create(
            usuario=instance,
            telefono='',
            direccion='',
            ciudad='',
            codigo_postal=''
        )