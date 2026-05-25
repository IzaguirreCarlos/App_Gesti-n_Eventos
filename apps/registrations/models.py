import uuid
import qrcode
from io import BytesIO
from django.db import models
from django.contrib.auth import get_user_model
from django.core.files import File
from apps.events.models import Event

User = get_user_model()


class Registration(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        CONFIRMED = 'confirmed', 'Confirmado'
        CANCELLED = 'cancelled', 'Cancelado'
        WAITLISTED = 'waitlisted', 'Lista de espera'
        CHECKED_IN = 'checked_in', 'Registrado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    status = models.CharField('estado', max_length=20, choices=Status.choices, default=Status.CONFIRMED)
    checked_in = models.BooleanField('registrado en evento', default=False)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    confirmation_code = models.CharField('código de confirmación', max_length=12, unique=True, blank=True)
    qr_code = models.ImageField('código QR', upload_to='qr_codes/', blank=True, null=True)
    notes = models.TextField('notas', blank=True)
    registration_date = models.DateTimeField('fecha de registro', auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'registro'
        verbose_name_plural = 'registros'
        unique_together = ['user', 'event']
        ordering = ['-registration_date']
        indexes = [
            models.Index(fields=['event', 'status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['confirmation_code']),
        ]

    def __str__(self):
        return f'{self.user.email} → {self.event.title}'

    def save(self, *args, **kwargs):
        if not self.confirmation_code:
            self.confirmation_code = str(uuid.uuid4()).upper()[:12]
        if not self.qr_code:
            self._generate_qr_code()
        super().save(*args, **kwargs)

    def _generate_qr_code(self):
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(f'IZAG:{self.confirmation_code}')
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        self.qr_code.save(f'qr_{self.confirmation_code}.png', File(buffer), save=False)

    @property
    def is_active(self):
        return self.status in [self.Status.CONFIRMED, self.Status.CHECKED_IN]
