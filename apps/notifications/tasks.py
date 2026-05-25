"""Celery async tasks for notifications."""
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_registration_confirmation(self, registration_id: str):
    """Send registration confirmation email."""
    try:
        from apps.registrations.models import Registration
        reg = Registration.objects.select_related('user', 'event').get(id=registration_id)
        subject = f'✅ Confirmación de registro: {reg.event.title}'
        html_message = render_to_string('emails/registration_confirmation.html', {
            'registration': reg,
            'user': reg.user,
            'event': reg.event,
        })
        send_mail(
            subject=subject,
            message=f'Tu registro ha sido confirmado. Código: {reg.confirmation_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reg.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        from apps.notifications.models import Notification
        Notification.objects.create(
            user=reg.user,
            type='registration_confirmed',
            title='Registro confirmado',
            message=f'Tu registro para {reg.event.title} ha sido confirmado.',
            email_sent=True,
        )
        logger.info(f'Confirmation email sent to {reg.user.email} for {reg.event.title}')
    except Exception as exc:
        logger.error(f'Error sending confirmation: {exc}')
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_event_cancellation_email(self, registration_id: str):
    """Notify user that an event was cancelled."""
    try:
        from apps.registrations.models import Registration
        reg = Registration.objects.select_related('user', 'event').get(id=registration_id)
        subject = f'❌ Evento cancelado: {reg.event.title}'
        html_message = render_to_string('emails/event_cancelled.html', {
            'registration': reg,
            'user': reg.user,
            'event': reg.event,
        })
        send_mail(
            subject=subject,
            message=f'El evento {reg.event.title} ha sido cancelado.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reg.user.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task
def send_event_reminder():
    """Send reminders for events starting in 24 hours."""
    from datetime import timedelta
    from django.utils import timezone
    from apps.registrations.models import Registration

    tomorrow = timezone.now() + timedelta(hours=24)
    window_start = tomorrow - timedelta(hours=1)

    registrations = Registration.objects.filter(
        status='confirmed',
        event__start_date__gte=window_start,
        event__start_date__lte=tomorrow,
        event__status='published',
    ).select_related('user', 'event')

    for reg in registrations:
        try:
            subject = f'🔔 Recordatorio: {reg.event.title} mañana'
            html_message = render_to_string('emails/event_reminder.html', {
                'registration': reg,
                'user': reg.user,
                'event': reg.event,
            })
            send_mail(
                subject=subject,
                message=f'Recuerda que mañana tienes el evento: {reg.event.title}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[reg.user.email],
                html_message=html_message,
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f'Reminder error for {reg.user.email}: {e}')
