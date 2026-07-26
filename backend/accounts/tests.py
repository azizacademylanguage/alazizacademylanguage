from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from accounts.models import Filial
from courses.models import Daraja, Fan, OquvchiFan

User = get_user_model()


class AdminStudentCreateTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_test',
            password='admin12345',
            role=User.ROLE_ADMIN,
            is_staff=True,
            is_superuser=True,
        )
        self.filial = Filial.objects.create(nomi='Asosiy filial', manzil='Toshkent')
        self.fan = Fan.objects.create(nomi='English', tartib=1)
        self.daraja = Daraja.objects.create(fan=self.fan, nomi='Beginner', tartib=1)
        self.client.force_authenticate(self.admin)

    def test_admin_can_create_student_without_explicit_filial(self):
        response = self.client.post('/api/admin/oquvchilar/', {
            'ism': 'Ali',
            'familya': 'Valiyev',
            'username': 'ali_student',
            'password': 'student12345',
            'daraja': self.daraja.id,
        }, format='json')

        self.assertEqual(response.status_code, 201, response.data)
        student = User.objects.get(username='ali_student')
        self.assertEqual(student.role, User.ROLE_OQUVCHI)
        self.assertEqual(student.filial, self.filial)
        self.assertTrue(student.check_password('student12345'))
        self.assertTrue(
            OquvchiFan.objects.filter(oquvchi=student, daraja=self.daraja).exists()
        )

    def test_duplicate_login_returns_validation_error(self):
        User.objects.create_user(
            username='used_login',
            password='student12345',
            role=User.ROLE_OQUVCHI,
        )
        response = self.client.post('/api/admin/oquvchilar/', {
            'ism': 'Vali',
            'familya': 'Aliyev',
            'username': 'USED_LOGIN',
            'password': 'student12345',
            'daraja': self.daraja.id,
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('username', response.data)

    def test_tariff_and_payment_status_are_normalized(self):
        response = self.client.post('/api/admin/oquvchilar/', {
            'ism': 'Malika',
            'familya': 'Karimova',
            'username': 'malika_student',
            'password': 'student12345',
            'daraja': self.daraja.id,
            'tarif': 'VIP',
            'tolov_holati': 'qarzdor',
        }, format='json')

        self.assertEqual(response.status_code, 201, response.data)
        student = User.objects.get(username='malika_student')
        self.assertEqual(student.tarif, User.TARIF_YAGONA)
        self.assertEqual(student.tolov_holati, User.TOLOV_TOLANMAGAN)


    def test_start_date_sets_end_date_one_calendar_month_later(self):
        response = self.client.post('/api/admin/oquvchilar/', {
            'ism': 'Oysha',
            'familya': 'Aliyeva',
            'username': 'oysha_login',
            'password': 'OyshaSecure45',
            'daraja': self.daraja.id,
            'boshlanish_sana': '2026-01-31',
        }, format='json')

        self.assertEqual(response.status_code, 201, response.data)
        student = User.objects.get(username='oysha_login')
        self.assertEqual(str(student.tugash_sana), '2026-02-28')
        self.assertTrue(student.check_password('OyshaSecure45'))

    def test_same_names_are_allowed_but_login_stays_unique(self):
        User.objects.create_user(username='first_login', password='FirstSecure45', ism='Ali', familya='Valiyev', role=User.ROLE_OQUVCHI)
        response = self.client.post('/api/admin/oquvchilar/', {
            'ism': 'Ali',
            'familya': 'Valiyev',
            'username': 'second_login',
            'password': 'SecondSecure45',
            'daraja': self.daraja.id,
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(User.objects.filter(ism='Ali', familya='Valiyev').count(), 2)

    def test_admin_can_reset_any_user_password(self):
        student = User.objects.create_user(username='reset_me', password='oldpass', role=User.ROLE_OQUVCHI)
        response = self.client.patch(f'/api/admin/foydalanuvchilar/{student.id}/', {
            'password': 'newpass123'
        }, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        student.refresh_from_db()
        self.assertTrue(student.check_password('newpass123'))

    def test_login_and_password_cannot_be_the_same(self):
        response = self.client.post('/api/admin/oquvchilar/', {
            'ism': 'Aziz',
            'familya': 'Karimov',
            'username': 'aziz_login',
            'password': 'AZIZ_LOGIN',
            'daraja': self.daraja.id,
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)

    def test_password_is_required_when_admin_creates_student(self):
        response = self.client.post('/api/admin/oquvchilar/', {
            'ism': 'Nozima',
            'familya': 'Aliyeva',
            'username': 'nozima_login',
            'daraja': self.daraja.id,
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)

    def test_admin_can_mark_unpaid_student_as_paid(self):
        student = User.objects.create_user(
            username='payment_student',
            password='PaymentSecure45',
            role=User.ROLE_OQUVCHI,
            tolov_holati=User.TOLOV_TOLANMAGAN,
        )
        response = self.client.patch(
            f'/api/admin/oquvchilar/{student.id}/',
            {'tolov_holati': 'tolangan'},
            format='json',
        )

        self.assertEqual(response.status_code, 200, response.data)
        student.refresh_from_db()
        self.assertEqual(student.tolov_holati, User.TOLOV_TOLANGAN)
