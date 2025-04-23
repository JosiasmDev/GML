from django.db import models
from django.conf import settings
from django.utils import timezone

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
        app_label = 'notifications'
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