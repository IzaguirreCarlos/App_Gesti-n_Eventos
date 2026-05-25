from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User',
            password='testpass123',
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.get_full_name(), 'Test User')
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_verified)
        self.assertEqual(self.user.role, 'attendee')

    def test_is_organizer(self):
        self.assertFalse(self.user.is_organizer)
        self.user.role = 'organizer'
        self.assertTrue(self.user.is_organizer)

    def test_superuser_creation(self):
        admin = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            first_name='Admin',
            last_name='User',
            password='adminpass123',
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_verified)
        self.assertEqual(admin.role, 'admin')

    def test_str(self):
        self.assertIn('test@example.com', str(self.user))


class AuthViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='view@example.com',
            username='viewuser',
            first_name='View',
            last_name='User',
            password='viewpass123',
        )

    def test_login_view_get(self):
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post(reverse('users:login'), {
            'username': 'view@example.com',
            'password': 'viewpass123',
        })
        self.assertRedirects(response, reverse('dashboard:index'))

    def test_login_failure(self):
        response = self.client.post(reverse('users:login'), {
            'username': 'view@example.com',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_register_view(self):
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.client.login(username='view@example.com', password='viewpass123')
        response = self.client.get(reverse('users:logout'))
        self.assertRedirects(response, reverse('events:list'))
