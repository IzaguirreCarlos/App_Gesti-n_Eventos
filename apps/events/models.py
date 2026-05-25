from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone
from django.core.validators import MinValueValidator
import uuid

User = get_user_model()


class Category(models.Model):
    name = models.CharField('nombre', max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    color = models.CharField('color hex', max_length=7, default='#6366f1')
    icon = models.CharField('icono', max_length=50, default='calendar', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Event(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Borrador'
        PUBLISHED = 'published', 'Publicado'
        CANCELLED = 'cancelled', 'Cancelado'
        COMPLETED = 'completed', 'Completado'

    class EventType(models.TextChoices):
        PRESENTIAL = 'presential', 'Presencial'
        VIRTUAL = 'virtual', 'Virtual'
        HYBRID = 'hybrid', 'Híbrido'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('título', max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField('descripción')
    short_description = models.CharField('descripción corta', max_length=300, blank=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events', verbose_name='organizador')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    event_type = models.CharField('tipo', max_length=20, choices=EventType.choices, default=EventType.PRESENTIAL)
    start_date = models.DateTimeField('fecha inicio')
    end_date = models.DateTimeField('fecha fin')
    location = models.CharField('ubicación', max_length=300, blank=True)
    address = models.TextField('dirección', blank=True)
    virtual_link = models.URLField('enlace virtual', blank=True)
    virtual_platform = models.CharField('plataforma virtual', max_length=100, blank=True)
    max_capacity = models.PositiveIntegerField('capacidad máxima', validators=[MinValueValidator(1)])
    current_attendees = models.PositiveIntegerField('asistentes actuales', default=0)
    cover_image = models.ImageField('imagen de portada', upload_to='events/covers/', null=True, blank=True)
    status = models.CharField('estado', max_length=20, choices=Status.choices, default=Status.DRAFT)
    is_public = models.BooleanField('es público', default=True)
    is_free = models.BooleanField('es gratuito', default=True)
    price = models.DecimalField('precio', max_digits=10, decimal_places=2, default=0)
    tags = models.CharField('etiquetas', max_length=500, blank=True, help_text='Separadas por coma')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'evento'
        verbose_name_plural = 'eventos'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status', 'is_public']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['organizer']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            n = 1
            while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{n}'
                n += 1
            self.slug = slug
        if not self.short_description and self.description:
            self.short_description = self.description[:297] + '...' if len(self.description) > 300 else self.description
        super().save(*args, **kwargs)

    @property
    def available_spots(self):
        return max(0, self.max_capacity - self.current_attendees)

    @property
    def is_full(self):
        return self.current_attendees >= self.max_capacity

    @property
    def is_upcoming(self):
        return self.start_date > timezone.now()

    @property
    def is_ongoing(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    @property
    def occupancy_percentage(self):
        if self.max_capacity == 0:
            return 0
        return round((self.current_attendees / self.max_capacity) * 100)

    def get_tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]
