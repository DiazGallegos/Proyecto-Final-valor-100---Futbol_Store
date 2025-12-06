# usuarios/signals.py (CORREGIDO)
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Perfil

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crear perfil automáticamente cuando se crea un usuario"""
    if created:
        # Verificar si ya existe un perfil (por si acaso)
        if not hasattr(instance, 'perfil'):
            Perfil.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    """Guardar perfil automáticamente cuando se guarda un usuario"""
    try:
        instance.perfil.save()
    except Perfil.DoesNotExist:
        # Si no existe el perfil, lo creamos
        Perfil.objects.create(usuario=instance)