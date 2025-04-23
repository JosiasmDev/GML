from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone

class Proyecto(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    creador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proyectos_creados')
    usuarios = models.ManyToManyField(User, related_name='proyectos_asignados')

    def __str__(self):
        return self.titulo

class Tarea(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('completada', 'Completada'),
    )
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='tareas')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_limite = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    asignados = models.ManyToManyField(User, related_name='tareas_asignadas')

    def __str__(self):
        return self.titulo

class Mensaje(models.Model):
    remitente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensajes_enviados')
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensajes_recibidos')
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f"Mensaje de {self.remitente} a {self.destinatario} ({self.fecha_envio})"

class Comentario(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario de {self.autor} en {self.tarea}"

class Grupo(models.Model):
    nombre = models.CharField(max_length=100)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='grupos')
    miembros = models.ManyToManyField(User, related_name='grupos')

    def __str__(self):
        return self.nombre

class Rol(models.Model):
    ROLES = (
        ('administrador', 'Administrador'),
        ('miembro', 'Miembro'),
        ('invitado', 'Invitado'),
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20, choices=ROLES, default='miembro')

    class Meta:
        unique_together = ('usuario', 'proyecto')

    def __str__(self):
        return f"{self.usuario} - {self.rol} en {self.proyecto}"

class MensajeProyecto(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='mensajes')
    remitente = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mensaje de {self.remitente} en {self.proyecto} ({self.fecha_envio})"

class Notification(models.Model):
    LEVELS = (
        ('success', 'success'),
        ('info', 'info'),
        ('warning', 'warning'),
        ('error', 'error'),
    )
    level = models.CharField(choices=LEVELS, default='info', max_length=20)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        related_name='notifications',
        on_delete=models.CASCADE
    )
    unread = models.BooleanField(default=True, db_index=True)
    actor_content_type = models.ForeignKey(
        'contenttypes.ContentType',
        blank=True,
        null=True,
        related_name='notify_actor',
        on_delete=models.CASCADE
    )
    actor_object_id = models.CharField(max_length=255, blank=True, null=True)
    verb = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    target_content_type = models.ForeignKey(
        'contenttypes.ContentType',
        blank=True,
        null=True,
        related_name='notify_target',
        on_delete=models.CASCADE
    )
    target_object_id = models.CharField(max_length=255, blank=True, null=True)
    action_object_content_type = models.ForeignKey(
        'contenttypes.ContentType',
        blank=True,
        null=True,
        related_name='notify_action_object',
        on_delete=models.CASCADE
    )
    action_object_object_id = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    public = models.BooleanField(default=True, db_index=True)
    deleted = models.BooleanField(default=False, db_index=True)
    emailed = models.BooleanField(default=False, db_index=True)
    data = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ('-timestamp',)
        indexes = [
            models.Index(fields=['recipient', 'unread']),
            models.Index(fields=['recipient', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.recipient} - {self.verb}"

    def mark_as_read(self):
        if self.unread:
            self.unread = False
            self.save()

    def mark_as_unread(self):
        if not self.unread:
            self.unread = True
            self.save()