from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    class Type(models.TextChoices):
        REGISTRATION_CONFIRMED = 'registration_confirmed', 'Registro Confirmado'
        REGISTRATION_CANCELLED = 'registration_cancelled', 'Registro Cancelado'
        EVENT_REMINDER = 'event_reminder', 'Recordatorio'
        EVENT_CANCELLED = 'event_cancelled', 'Evento Cancelado'
        WAITLIST_PROMOTED = 'waitlist_promoted', 'Ascendido de lista de espera'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=50, choices=Type.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', 'is_read'])]

    def __str__(self):
        return f'{self.user.email} - {self.title}'
