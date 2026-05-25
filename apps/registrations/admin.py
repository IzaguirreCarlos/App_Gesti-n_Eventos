from django.contrib import admin
from .models import Registration


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'status', 'checked_in', 'confirmation_code', 'registration_date']
    list_filter = ['status', 'checked_in']
    search_fields = ['user__email', 'event__title', 'confirmation_code']
    readonly_fields = ['id', 'confirmation_code', 'qr_code', 'registration_date', 'updated_at']
    ordering = ['-registration_date']
    actions = ['check_in_attendees', 'cancel_registrations']

    @admin.action(description='Hacer check-in')
    def check_in_attendees(self, request, queryset):
        for reg in queryset.filter(status='confirmed'):
            from .services import RegistrationService
            RegistrationService.check_in(reg)

    @admin.action(description='Cancelar registros')
    def cancel_registrations(self, request, queryset):
        for reg in queryset:
            from .services import RegistrationService
            try:
                RegistrationService.cancel_registration(reg)
            except Exception:
                pass
