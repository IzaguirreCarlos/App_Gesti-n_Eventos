from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Registration
from .services import RegistrationService
from apps.events.models import Event


@login_required
@require_POST
def register_to_event(request, slug):
    event = get_object_or_404(Event, slug=slug, status='published')
    try:
        reg = RegistrationService.register_user(request.user, event)
        if reg.status == Registration.Status.WAITLISTED:
            messages.warning(request, 'El evento está lleno. Has sido agregado a la lista de espera.')
        else:
            messages.success(request, f'¡Registro exitoso! Tu código: {reg.confirmation_code}')
    except Exception as e:
        messages.error(request, str(e))
    return redirect('events:detail', slug=slug)


@login_required
@require_POST
def cancel_registration(request, pk):
    reg = get_object_or_404(Registration, pk=pk, user=request.user)
    try:
        RegistrationService.cancel_registration(reg)
        messages.success(request, 'Inscripción cancelada correctamente.')
    except Exception as e:
        messages.error(request, str(e))
    return redirect('dashboard:index')


@login_required
def my_registrations(request):
    registrations = (
        Registration.objects
        .filter(user=request.user)
        .select_related('event', 'event__category', 'event__organizer')
        .order_by('-registration_date')
    )
    return render(request, 'registrations/my_registrations.html', {'registrations': registrations})


@login_required
def registration_detail(request, pk):
    reg = get_object_or_404(Registration, pk=pk, user=request.user)
    return render(request, 'registrations/detail.html', {'registration': reg})
