"""Registration business logic."""
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Registration
from apps.events.models import Event


class RegistrationService:

    @staticmethod
    @transaction.atomic
    def register_user(user, event: Event) -> Registration:
        """Register a user to an event with all business rules."""
        # Check if already registered
        existing = Registration.objects.filter(user=user, event=event).first()
        if existing:
            if existing.status == Registration.Status.CANCELLED:
                existing.status = Registration.Status.CONFIRMED
                existing.save(update_fields=['status', 'updated_at'])
                Event.objects.filter(pk=event.pk).update(
                    current_attendees=models.F('current_attendees') + 1
                )
                return existing
            raise ValidationError('Ya estás registrado en este evento.')

        # Check event status
        if event.status != Event.Status.PUBLISHED:
            raise ValidationError('Este evento no está disponible para registro.')

        # Check capacity
        if event.is_full:
            reg = Registration.objects.create(user=user, event=event, status=Registration.Status.WAITLISTED)
            return reg

        # Create registration
        reg = Registration.objects.create(user=user, event=event, status=Registration.Status.CONFIRMED)
        Event.objects.filter(pk=event.pk).update(
            current_attendees=models.F('current_attendees') + 1
        )

        # Send confirmation email
        from apps.notifications.tasks import send_registration_confirmation
        send_registration_confirmation.delay(str(reg.id))

        return reg

    @staticmethod
    @transaction.atomic
    def cancel_registration(registration: Registration) -> Registration:
        """Cancel a registration and free up a spot."""
        if registration.status == Registration.Status.CANCELLED:
            raise ValidationError('Esta inscripción ya está cancelada.')

        was_confirmed = registration.status in [
            Registration.Status.CONFIRMED,
            Registration.Status.CHECKED_IN,
        ]
        registration.status = Registration.Status.CANCELLED
        registration.save(update_fields=['status', 'updated_at'])

        if was_confirmed:
            Event.objects.filter(
                pk=registration.event.pk,
                current_attendees__gt=0
            ).update(current_attendees=models.F('current_attendees') - 1)

            # Promote waitlisted user
            waitlisted = Registration.objects.filter(
                event=registration.event,
                status=Registration.Status.WAITLISTED,
            ).order_by('registration_date').first()

            if waitlisted:
                waitlisted.status = Registration.Status.CONFIRMED
                waitlisted.save(update_fields=['status', 'updated_at'])
                Event.objects.filter(pk=registration.event.pk).update(
                    current_attendees=models.F('current_attendees') + 1
                )
                from apps.notifications.tasks import send_registration_confirmation
                send_registration_confirmation.delay(str(waitlisted.id))

        return registration

    @staticmethod
    @transaction.atomic
    def check_in(registration: Registration) -> Registration:
        """Check-in a user at the event."""
        if registration.status != Registration.Status.CONFIRMED:
            raise ValidationError('Solo se pueden hacer check-in de registros confirmados.')
        registration.status = Registration.Status.CHECKED_IN
        registration.checked_in = True
        registration.checked_in_at = timezone.now()
        registration.save(update_fields=['status', 'checked_in', 'checked_in_at', 'updated_at'])
        return registration


from django.db import models
