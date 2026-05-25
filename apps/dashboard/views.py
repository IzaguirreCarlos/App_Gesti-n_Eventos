from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.http import HttpResponse
import csv
from apps.events.models import Event
from apps.registrations.models import Registration
from apps.events.selectors import EventSelector


@login_required
def dashboard_index(request):
    user = request.user
    context = {}

    if user.is_organizer:
        events = EventSelector.get_organizer_events(user)
        total_events = events.count()
        total_registrations = Registration.objects.filter(event__organizer=user).count()
        upcoming = events.filter(status='published', start_date__gt=timezone.now()).count()
        cancelled = events.filter(status='cancelled').count()

        # Recent activity
        recent_registrations = (
            Registration.objects
            .filter(event__organizer=user)
            .select_related('user', 'event')
            .order_by('-registration_date')[:10]
        )

        # Stats per event
        event_stats = events[:6]

        context.update({
            'events': events[:8],
            'total_events': total_events,
            'total_registrations': total_registrations,
            'upcoming_events': upcoming,
            'cancelled_events': cancelled,
            'recent_registrations': recent_registrations,
            'event_stats': event_stats,
        })
    else:
        # Attendee dashboard
        registrations = (
            Registration.objects
            .filter(user=user)
            .select_related('event', 'event__category')
            .order_by('-registration_date')
        )
        upcoming_regs = registrations.filter(
            event__start_date__gt=timezone.now(),
            status__in=['confirmed', 'checked_in']
        )
        context.update({
            'registrations': registrations[:8],
            'upcoming_registrations': upcoming_regs[:4],
            'total_registrations': registrations.count(),
        })

    return render(request, 'dashboard/index.html', context)


@login_required
def event_attendees(request, slug):
    event = get_object_or_404(Event, slug=slug, organizer=request.user)
    registrations = (
        Registration.objects
        .filter(event=event)
        .select_related('user')
        .order_by('-registration_date')
    )
    stats = {
        'confirmed': registrations.filter(status='confirmed').count(),
        'checked_in': registrations.filter(status='checked_in').count(),
        'cancelled': registrations.filter(status='cancelled').count(),
        'waitlisted': registrations.filter(status='waitlisted').count(),
    }
    return render(request, 'dashboard/attendees.html', {
        'event': event,
        'registrations': registrations,
        'stats': stats,
    })


@login_required
def export_attendees_csv(request, slug):
    event = get_object_or_404(Event, slug=slug, organizer=request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{event.slug}-asistentes.csv"'
    writer = csv.writer(response)
    writer.writerow(['Nombre', 'Email', 'Estado', 'Check-in', 'Código', 'Fecha Registro'])
    for reg in Registration.objects.filter(event=event).select_related('user'):
        writer.writerow([
            reg.user.get_full_name(),
            reg.user.email,
            reg.get_status_display(),
            'Sí' if reg.checked_in else 'No',
            reg.confirmation_code,
            reg.registration_date.strftime('%Y-%m-%d %H:%M'),
        ])
    return response
