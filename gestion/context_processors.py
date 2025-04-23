# gestion/context_processors.py
from django.contrib.auth.models import User
from .models import Mensaje
from django.db import models

def chat_data(request):
    if request.user.is_authenticated:
        mensajes_enviados = Mensaje.objects.filter(remitente=request.user)
        mensajes_recibidos = Mensaje.objects.filter(destinatario=request.user)
        
        usuarios_enviados = mensajes_enviados.values_list('destinatario', flat=True)
        usuarios_recibidos = mensajes_recibidos.values_list('remitente', flat=True)
        usuarios_conversados_ids = set(list(usuarios_enviados) + list(usuarios_recibidos))
        usuarios_conversados = User.objects.filter(id__in=usuarios_conversados_ids)
        
        usuarios_con_mensajes_no_leidos = {
            usuario.id: mensajes_recibidos.filter(remitente=usuario, leido=False).exists()
            for usuario in usuarios_conversados
        }
        
        conversacion_con = request.GET.get('con', None)
        mensajes_conversacion = None
        if conversacion_con:
            mensajes_conversacion = Mensaje.objects.filter(
                (models.Q(remitente=request.user) & models.Q(destinatario__id=conversacion_con)) |
                (models.Q(destinatario=request.user) & models.Q(remitente__id=conversacion_con))
            ).order_by('-fecha_envio')  # Orden descendente (más nuevo primero)
            mensajes_conversacion.filter(destinatario=request.user, leido=False).update(leido=True)
        
        return {
            'usuarios_conversados': usuarios_conversados,
            'mensajes_conversacion': mensajes_conversacion,
            'conversacion_con': conversacion_con,
            'usuarios_con_mensajes_no_leidos': usuarios_con_mensajes_no_leidos,
            'todos_los_usuarios': User.objects.all(),
        }
    return {}