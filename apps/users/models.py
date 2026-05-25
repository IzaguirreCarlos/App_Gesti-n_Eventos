from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('El email es obligatorio'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ATTENDEE = 'attendee', _('Asistente')
        ORGANIZER = 'organizer', _('Organizador')
        ADMIN = 'admin', _('Administrador')

    email = models.EmailField(_('email'), unique=True, db_index=True)
    username = models.CharField(_('usuario'), max_length=50, unique=True)
    first_name = models.CharField(_('nombre'), max_length=100)
    last_name = models.CharField(_('apellido'), max_length=100)
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(_('biografía'), blank=True, max_length=500)
    role = models.CharField(_('rol'), max_length=20, choices=Role.choices, default=Role.ATTENDEE)
    is_verified = models.BooleanField(_('verificado'), default=False)
    is_active = models.BooleanField(_('activo'), default=True)
    is_staff = models.BooleanField(_('staff'), default=False)
    date_joined = models.DateTimeField(_('fecha de registro'), default=timezone.now)
    last_login = models.DateTimeField(_('último acceso'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = _('usuario')
        verbose_name_plural = _('usuarios')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f'{self.get_full_name()} <{self.email}>'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def get_short_name(self):
        return self.first_name

    @property
    def is_organizer(self):
        return self.role in [self.Role.ORGANIZER, self.Role.ADMIN]

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
