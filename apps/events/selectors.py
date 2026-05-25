"""
Event data queries — Selector Layer
"""
from django.db.models import QuerySet, Count, Q
from django.utils import timezone
from .models import Event, Category


class EventSelector:

    @staticmethod
    def get_public_events() -> QuerySet:
        return (
            Event.objects
            .filter(status=Event.Status.PUBLISHED, is_public=True)
            .select_related('organizer', 'category')
            .order_by('start_date')
        )

    @staticmethod
    def get_upcoming_events(limit: int = 10) -> QuerySet:
        return (
            Event.objects
            .filter(
                status=Event.Status.PUBLISHED,
                is_public=True,
                start_date__gt=timezone.now()
            )
            .select_related('organizer', 'category')
            .order_by('start_date')[:limit]
        )

    @staticmethod
    def get_organizer_events(organizer) -> QuerySet:
        return (
            Event.objects
            .filter(organizer=organizer)
            .select_related('category')
            .annotate(registration_count=Count('registrations'))
            .order_by('-created_at')
        )

    @staticmethod
    def search_events(query: str = '', category_slug: str = '', event_type: str = '',
                      date_from=None, date_to=None) -> QuerySet:
        qs = Event.objects.filter(status=Event.Status.PUBLISHED, is_public=True).select_related('organizer', 'category')
        if query:
            qs = qs.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(location__icontains=query))
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        if event_type:
            qs = qs.filter(event_type=event_type)
        if date_from:
            qs = qs.filter(start_date__date__gte=date_from)
        if date_to:
            qs = qs.filter(start_date__date__lte=date_to)
        return qs.order_by('start_date')

    @staticmethod
    def get_calendar_events(start, end) -> QuerySet:
        return (
            Event.objects
            .filter(
                status=Event.Status.PUBLISHED,
                is_public=True,
                start_date__gte=start,
                start_date__lte=end,
            )
            .select_related('category')
            .values('id', 'title', 'start_date', 'end_date', 'event_type', 'category__color', 'slug')
        )
