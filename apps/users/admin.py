from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'get_full_name', 'username', 'role', 'is_verified', 'is_active', 'created_at']
    list_filter = ['role', 'is_verified', 'is_active', 'is_staff']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']
    list_editable = ['role', 'is_verified']
    readonly_fields = ['created_at', 'updated_at', 'last_login']
    actions = ['verify_users', 'make_organizer']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Info Personal'), {'fields': ('username', 'first_name', 'last_name', 'bio', 'avatar')}),
        (_('Rol y Permisos'), {'fields': ('role', 'is_verified', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Fechas'), {'fields': ('date_joined', 'last_login', 'created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'username', 'first_name', 'last_name', 'role', 'password1', 'password2')}),
    )

    @admin.action(description='Verificar usuarios seleccionados')
    def verify_users(self, request, queryset):
        queryset.update(is_verified=True)

    @admin.action(description='Hacer organizador')
    def make_organizer(self, request, queryset):
        queryset.update(role='organizer')
