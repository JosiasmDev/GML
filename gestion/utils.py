from django.contrib.contenttypes.models import ContentType
from .models import Notification

def notify(sender, recipient, verb, target=None, action_object=None, level='info', description=None, data=None):
    """
    Envía una notificación a un usuario.
    
    Args:
        sender: El usuario que realiza la acción
        recipient: El usuario que recibe la notificación
        verb: La acción realizada (string)
        target: El objeto objetivo de la acción (opcional)
        action_object: El objeto de la acción (opcional)
        level: Nivel de la notificación ('success', 'info', 'warning', 'error')
        description: Descripción adicional (opcional)
        data: Datos adicionales en formato JSON (opcional)
    """
    actor_content_type = ContentType.objects.get_for_model(sender) if sender else None
    target_content_type = ContentType.objects.get_for_model(target) if target else None
    action_object_content_type = ContentType.objects.get_for_model(action_object) if action_object else None

    notification = Notification.objects.create(
        level=level,
        recipient=recipient,
        actor_content_type=actor_content_type,
        actor_object_id=sender.id if sender else None,
        verb=verb,
        description=description,
        target_content_type=target_content_type,
        target_object_id=target.id if target else None,
        action_object_content_type=action_object_content_type,
        action_object_object_id=action_object.id if action_object else None,
        data=data
    )
    
    return notification 