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
