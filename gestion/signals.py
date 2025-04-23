# gestion/signals.py
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from notifications.signals import notify
from .models import Tarea, Mensaje

'''
@receiver(m2m_changed, sender=Tarea.asignados.through)
def notificar_asignacion_tarea(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for user_id in pk_set:
            usuario = instance.asignados.get(id=user_id)
            notify.send(
                instance.proyecto.creador,
                recipient=usuario,
                verb='te asignó la tarea',
                target=instance
            )



@receiver(post_save, sender=Mensaje)
def notificar_mensaje(sender, instance, created, **kwargs):
    if created:
        notify.send(
            instance.remitente,
            recipient=instance.destinatario,
            verb='te envió un mensaje',
            target=instance
        )
'''