from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .models import Event, Category

User = get_user_model()


def create_organizer(email='org@test.com', username='organizer'):
    return User.objects.create_user(
        email=email, username=username,
        first_name='Org', last_name='User',
        password='testpass123', role='organizer',
    )


def create_event(organizer, **kwargs):
    defaults = {
        'title': 'Test Event',
        'description': 'Test Description',
        'start_date': timezone.now() + timedelta(days=1),
        'end_date': timezone.now() + timedelta(days=2),
        'max_capacity': 100,
        'status': Event.Status.PUBLISHED,
        'is_public': True,
    }
    defaults.update(kwargs)
    return Event.objects.create(organizer=organizer, **defaults)


class EventModelTest(TestCase):
    def setUp(self):
        self.organizer = create_organizer()
        self.event = create_event(self.organizer)

    def test_slug_auto_generated(self):
        self.assertEqual(self.event.slug, 'test-event')

    def test_available_spots(self):
        self.assertEqual(self.event.available_spots, 100)

    def test_is_upcoming(self):
        self.assertTrue(self.event.is_upcoming)

    def test_occupancy_percentage(self):
        self.event.current_attendees = 50
        self.assertEqual(self.event.occupancy_percentage, 50)

    def test_is_full(self):
        self.event.current_attendees = 100
        self.assertTrue(self.event.is_full)

    def test_str(self):
        self.assertEqual(str(self.event), 'Test Event')

    def test_unique_slug_on_duplicate_title(self):
        event2 = create_event(self.organizer, title='Test Event')
        self.assertNotEqual(self.event.slug, event2.slug)


class EventViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.organizer = create_organizer()
        self.event = create_event(self.organizer)

    def test_home_view(self):
        response = self.client.get(reverse('events:home'))
        self.assertEqual(response.status_code, 200)

    def test_event_list(self):
        response = self.client.get(reverse('events:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Event')

    def test_event_detail(self):
        response = self.client.get(reverse('events:detail', kwargs={'slug': self.event.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.event.title)

    def test_event_create_requires_login(self):
        response = self.client.get(reverse('events:create'))
        self.assertRedirects(response, f'/auth/login/?next=/events/create/')

    def test_event_create_requires_organizer(self):
        attendee = User.objects.create_user(
            email='att@test.com', username='att',
            first_name='Att', last_name='Endee',
            password='testpass123', role='attendee',
        )
        self.client.login(username='att@test.com', password='testpass123')
        response = self.client.get(reverse('events:create'))
        self.assertRedirects(response, reverse('events:list'))

    def test_calendar_view(self):
        response = self.client.get(reverse('events:calendar'))
        self.assertEqual(response.status_code, 200)
