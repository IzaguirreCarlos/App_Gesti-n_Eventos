from django.contrib import admin
from django.utils.html import format_html
from .models import Event, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_preview', 'slug']
    prepopulated_fields = {'slug': ('name',)}

    def color_preview(self, obj):
        return format_html('<span style="background:{}; padding:2px 10px; border-radius:3px; color:white">{}</span>', obj.color, obj.color)
    color_preview.short_description = 'Color'


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer', 'category', 'event_type', 'start_date', 'status', 'current_attendees', 'max_capacity', 'occupancy_bar']
    list_filter = ['status', 'event_type', 'is_public', 'is_free', 'category']
    search_fields = ['title', 'organizer__email', 'location']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'current_attendees']
    date_hierarchy = 'start_date'
    ordering = ['-created_at']
    actions = ['publish_events', 'cancel_events']

    fieldsets = (
        ('Información Principal', {'fields': ('title', 'slug', 'description', 'short_description', 'cover_image')}),
        ('Organización', {'fields': ('organizer', 'category', 'status', 'is_public')}),
        ('Tipo y Lugar', {'fields': ('event_type', 'location', 'address', 'virtual_link', 'virtual_platform')}),
        ('Fechas', {'fields': ('start_date', 'end_date')}),
        ('Capacidad', {'fields': ('max_capacity', 'current_attendees')}),
        ('Precio', {'fields': ('is_free', 'price')}),
        ('Metadatos', {'fields': ('tags', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def occupancy_bar(self, obj):
        pct = obj.occupancy_percentage
        color = '#22c55e' if pct < 70 else '#f59e0b' if pct < 90 else '#ef4444'
        return format_html(
            '<div style="width:100px;background:#e5e7eb;border-radius:4px;overflow:hidden">'
            '<div style="width:{}%;background:{};height:12px;"></div></div> {}%',
            pct, color, pct
        )
    occupancy_bar.short_description = 'Ocupación'

    @admin.action(description='Publicar eventos')
    def publish_events(self, request, queryset):
        queryset.update(status='published')

    @admin.action(description='Cancelar eventos')
    def cancel_events(self, request, queryset):
        queryset.update(status='cancelled')
