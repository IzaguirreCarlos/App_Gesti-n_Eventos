"""
Event business logic — Service Layer
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Event, Category


class EventService:

    @staticmethod
    @transaction.atomic
    def create_event(organizer, data: dict) -> Event:
        """Create a new event with business rules validation."""
        if not organizer.is_organizer:
            raise ValidationError('Solo los organizadores pueden crear eventos.')
        event = Event(organizer=organizer, **data)
        event.full_clean()
        event.save()
        return event

    @staticmethod
    @transaction.atomic
    def update_event(event: Event, data: dict) -> Event:
        """Update an existing event."""
        for key, value in data.items():
            setattr(event, key, value)
        event.full_clean()
        event.save()
        return event

    @staticmethod
    @transaction.atomic
    def cancel_event(event: Event) -> Event:
        """Cancel an event and notify attendees."""
        from apps.registrations.models import Registration
        from apps.notifications.tasks import send_event_cancellation_email

        event.status = Event.Status.CANCELLED
        event.save(update_fields=['status'])

        # Notify all confirmed registrations
        registrations = Registration.objects.filter(
            event=event, status=Registration.Status.CONFIRMED
        ).select_related('user')

        for reg in registrations:
            send_event_cancellation_email.delay(reg.id)

        return event

    @staticmethod
    def increment_attendees(event: Event) -> None:
        """Atomically increment attendee count."""
        Event.objects.filter(pk=event.pk).update(
            current_attendees=models.F('current_attendees') + 1
        )

    @staticmethod
    def decrement_attendees(event: Event) -> None:
        """Atomically decrement attendee count."""
        from django.db import models as m
        Event.objects.filter(pk=event.pk, current_attendees__gt=0).update(
            current_attendees=m.F('current_attendees') - 1
        )


from django.db import models
