from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Event, Category
from .forms import EventForm, EventFilterForm
from .selectors import EventSelector
from .services import EventService


def home(request):
    upcoming = EventSelector.get_upcoming_events(6)
    categories = Category.objects.all()
    total_events = Event.objects.filter(status='published').count()
    return render(request, 'events/home.html', {
        'upcoming_events': upcoming,
        'categories': categories,
        'total_events': total_events,
    })


def event_list(request):
    form = EventFilterForm(request.GET)
    events = EventSelector.search_events(
        query=request.GET.get('q', ''),
        category_slug=request.GET.get('category', ''),
        event_type=request.GET.get('event_type', ''),
        date_from=request.GET.get('date_from'),
        date_to=request.GET.get('date_to'),
    )
    paginator = Paginator(events, 12)
    page = paginator.get_page(request.GET.get('page'))
    categories = Category.objects.all()

    if request.headers.get('HX-Request'):
        return render(request, 'events/partials/event_cards.html', {'page': page})

    return render(request, 'events/list.html', {'page': page, 'form': form, 'categories': categories})


def event_detail(request, slug):
    event = get_object_or_404(
        Event.objects.select_related('organizer', 'category').prefetch_related('registrations'),
        slug=slug,
        status=Event.Status.PUBLISHED,
    )
    user_registration = None
    if request.user.is_authenticated:
        user_registration = event.registrations.filter(user=request.user).first()
    return render(request, 'events/detail.html', {
        'event': event,
        'user_registration': user_registration,
    })


def calendar_view(request):
    return render(request, 'events/calendar.html')


def calendar_events_api(request):
    """Return events as JSON for FullCalendar."""
    start = request.GET.get('start')
    end = request.GET.get('end')
    if not start or not end:
        return JsonResponse([], safe=False)
    events = EventSelector.get_calendar_events(start, end)
    data = [
        {
            'id': str(e['id']),
            'title': e['title'],
            'start': e['start_date'].isoformat(),
            'end': e['end_date'].isoformat(),
            'url': f'/events/{e["slug"]}/',
            'color': e['category__color'] or '#6366f1',
            'extendedProps': {'type': e['event_type']},
        }
        for e in events
    ]
    return JsonResponse(data, safe=False)


@login_required
def event_create(request):
    if not request.user.is_organizer:
        messages.error(request, 'Necesitas ser organizador para crear eventos.')
        return redirect('events:list')
    form = EventForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        event = form.save(commit=False)
        event.organizer = request.user
        event.save()
        messages.success(request, f'Evento "{event.title}" creado correctamente.')
        return redirect('events:detail', slug=event.slug)
    return render(request, 'events/create.html', {'form': form})


@login_required
def event_edit(request, slug):
    event = get_object_or_404(Event, slug=slug, organizer=request.user)
    form = EventForm(request.POST or None, request.FILES or None, instance=event)
    if form.is_valid():
        form.save()
        messages.success(request, 'Evento actualizado correctamente.')
        return redirect('events:detail', slug=event.slug)
    return render(request, 'events/edit.html', {'form': form, 'event': event})


@login_required
@require_http_methods(['POST'])
def event_delete(request, slug):
    event = get_object_or_404(Event, slug=slug, organizer=request.user)
    event.delete()
    messages.success(request, 'Evento eliminado.')
    return redirect('dashboard:index')
