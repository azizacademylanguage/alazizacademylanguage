from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from courses.models import Dars, Daraja, Fan, Mavzu, OquvchiFan
from exams.models import Javob, Mashq, Savol

User = get_user_model()


class LearningFlowTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_test',
            password='admin123',
            role=User.ROLE_ADMIN,
        )
        self.fan = Fan.objects.create(nomi='English', tartib=1)
        self.beginner = Daraja.objects.create(fan=self.fan, nomi='Beginner', tartib=1)
        self.elementary = Daraja.objects.create(fan=self.fan, nomi='Elementary', tartib=2)

    def test_admin_creates_student_with_selected_level(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post('/api/admin/oquvchilar/', {
            'username': 'student1',
            'password': 'pass1234',
            'ism': 'Ali',
            'familya': 'Valiyev',
            'daraja': self.elementary.id,
        }, format='json')

        self.assertEqual(response.status_code, 201, response.data)
        student = User.objects.get(username='student1')
        assignment = OquvchiFan.objects.get(oquvchi=student)
        self.assertEqual(assignment.daraja, self.elementary)
        self.assertTrue(student.check_password('pass1234'))

        self.client.force_authenticate(student)
        fanlar_response = self.client.get('/api/oquvchi/fanlarim/')
        self.assertEqual(fanlar_response.status_code, 200)
        levels = fanlar_response.data[0]['darajalar']
        self.assertEqual(len(levels), 2)
        self.assertFalse(next(item for item in levels if item['id'] == self.beginner.id)['ochiq'])
        self.assertTrue(next(item for item in levels if item['id'] == self.elementary.id)['ochiq'])

    def test_next_topic_opens_only_after_80_percent(self):
        student = User.objects.create_user(
            username='student2',
            password='pass1234',
            role=User.ROLE_OQUVCHI,
        )
        OquvchiFan.objects.create(
            oquvchi=student,
            daraja=self.beginner,
            biriktirgan=self.admin,
            qolda_ochilgan=True,
        )

        topic1 = Mavzu.objects.create(daraja=self.beginner, nomi='Topic 1', tartib=1)
        topic2 = Mavzu.objects.create(daraja=self.beginner, nomi='Topic 2', tartib=2)
        lesson = Dars.objects.create(mavzu=topic1, sarlavha='Lesson 1', tartib=1)
        quiz = Mashq.objects.create(dars=lesson, sarlavha='Quiz 1', otish_bali_foiz=80)
        question = Savol.objects.create(mashq=quiz, matn='2+2?', tur=Savol.TUR_SINGLE, tartib=1)
        wrong = Javob.objects.create(savol=question, matn='3', togri=False, tartib=1)
        correct = Javob.objects.create(savol=question, matn='4', togri=True, tartib=2)

        self.client.force_authenticate(student)
        topics_response = self.client.get(f'/api/oquvchi/mavzular/{self.beginner.id}/')
        self.assertEqual(topics_response.status_code, 200)
        states = {item['id']: item['ochiq'] for item in topics_response.data}
        self.assertTrue(states[topic1.id])
        self.assertFalse(states[topic2.id])

        failed = self.client.post(f'/api/oquvchi/mashq/{quiz.id}/topshirish/', {
            'javoblar': [{'savol': question.id, 'tanlangan_javoblar': [wrong.id]}],
        }, format='json')
        self.assertEqual(failed.status_code, 201)
        self.assertFalse(failed.data['otdi'])
        self.assertFalse(failed.data['keyingi_mavzu_ochildi'])

        passed = self.client.post(f'/api/oquvchi/mashq/{quiz.id}/topshirish/', {
            'javoblar': [{'savol': question.id, 'tanlangan_javoblar': [correct.id]}],
        }, format='json')
        self.assertEqual(passed.status_code, 201)
        self.assertTrue(passed.data['otdi'])
        self.assertTrue(passed.data['keyingi_mavzu_ochildi'])

        topics_response = self.client.get(f'/api/oquvchi/mavzular/{self.beginner.id}/')
        states = {item['id']: item['ochiq'] for item in topics_response.data}
        self.assertTrue(states[topic2.id])
