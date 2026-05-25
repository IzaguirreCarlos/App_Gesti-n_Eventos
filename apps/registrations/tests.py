from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from apps.events.models import Event
from .models import Registration
from .services import RegistrationService
from django.core.exceptions import ValidationError

User = get_user_model()


def make_user(email, username, role='attendee'):
    return User.objects.create_user(
        email=email, username=username,
        first_name='Test', last_name='User',
        password='pass123', role=role,
    )


def make_event(organizer, capacity=10, status='published'):
    return Event.objects.create(
        title='Test Event',
        description='Desc',
        organizer=organizer,
        start_date=timezone.now() + timedelta(days=1),
        end_date=timezone.now() + timedelta(days=2),
        max_capacity=capacity,
        status=status,
    )


class RegistrationServiceTest(TestCase):
    def setUp(self):
        self.organizer = make_user('org@t.com', 'org', 'organizer')
        self.user = make_user('user@t.com', 'user')
        self.event = make_event(self.organizer)

    def test_register_success(self):
        reg = RegistrationService.register_user(self.user, self.event)
        self.assertEqual(reg.status, Registration.Status.CONFIRMED)
        self.event.refresh_from_db()
        self.assertEqual(self.event.current_attendees, 1)

    def test_duplicate_registration_raises(self):
        RegistrationService.register_user(self.user, self.event)
        with self.assertRaises(ValidationError):
            RegistrationService.register_user(self.user, self.event)

    def test_waitlist_when_full(self):
        self.event.current_attendees = 10
        self.event.save()
        reg = RegistrationService.register_user(self.user, self.event)
        self.assertEqual(reg.status, Registration.Status.WAITLISTED)

    def test_cancel_registration(self):
        reg = RegistrationService.register_user(self.user, self.event)
        RegistrationService.cancel_registration(reg)
        reg.refresh_from_db()
        self.assertEqual(reg.status, Registration.Status.CANCELLED)
        self.event.refresh_from_db()
        self.assertEqual(self.event.current_attendees, 0)

    def test_confirmation_code_generated(self):
        reg = RegistrationService.register_user(self.user, self.event)
        self.assertTrue(len(reg.confirmation_code) > 0)

    def test_check_in(self):
        reg = RegistrationService.register_user(self.user, self.event)
        checked = RegistrationService.check_in(reg)
        self.assertTrue(checked.checked_in)
        self.assertEqual(checked.status, Registration.Status.CHECKED_IN)
