from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from courses.access import daraja_ochiqmi
from courses.models import Dars, Daraja, Fan, Mavzu, OquvchiFan
from exams.models import (
    FinalTest,
    FinalTestJavob,
    FinalTestSavol,
    Mashq,
    MashqNatija,
    Sertifikat,
)

User = get_user_model()


class FinalLevelAndCertificateTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_final', password='admin12345', role=User.ROLE_ADMIN,
        )
        self.student = User.objects.create_user(
            username='student_final', password='student12345', role=User.ROLE_OQUVCHI,
            ism='Ali', familya='Valiyev',
        )
        self.fan = Fan.objects.create(nomi='English', tartib=1)
        self.beginner = Daraja.objects.create(
            fan=self.fan, nomi='Beginner — 16–30%', tartib=1, ochish_uchun_foiz=80,
        )
        self.elementary = Daraja.objects.create(
            fan=self.fan, nomi='2. Elementary — 31–45%', tartib=2, ochish_uchun_foiz=80,
        )
        OquvchiFan.objects.create(
            oquvchi=self.student,
            daraja=self.beginner,
            biriktirgan=self.admin,
            qolda_ochilgan=True,
        )

        for index in range(1, 4):
            topic = Mavzu.objects.create(
                daraja=self.beginner, nomi=f'Mavzu {index}', tartib=index,
            )
            lesson = Dars.objects.create(
                mavzu=topic, sarlavha=f'Dars {index}', tartib=1,
            )
            quiz = Mashq.objects.create(
                dars=lesson, sarlavha=f'Test {index}', otish_bali_foiz=80,
            )
            MashqNatija.objects.create(
                oquvchi=self.student,
                mashq=quiz,
                togri_soni=8,
                jami_soni=10,
                foiz=80,
            )

        self.final_test = FinalTest.objects.create(
            daraja=self.beginner,
            sarlavha='Beginner yakuniy testi',
            otish_bali_foiz=80,
        )
        self.correct_answers = []
        for index in range(1, 11):
            question = FinalTestSavol.objects.create(
                final_test=self.final_test,
                matn=f'Savol {index}',
                tartib=index,
            )
            correct = FinalTestJavob.objects.create(
                savol=question, matn='To‘g‘ri', togri=True, tartib=1,
            )
            FinalTestJavob.objects.create(
                savol=question, matn='Noto‘g‘ri', togri=False, tartib=2,
            )
            self.correct_answers.append((question.id, correct.id))

    def _payload(self, correct_count):
        answers = []
        for index, (question_id, correct_id) in enumerate(self.correct_answers):
            answers.append({
                'savol': question_id,
                'tanlangan_javoblar': [correct_id] if index < correct_count else [],
            })
        return {'javoblar': answers}

    def test_79_percent_does_not_open_next_level(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(
            f'/api/oquvchi/final-test/{self.beginner.id}/topshirish/',
            self._payload(7),
            format='json',
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertFalse(response.data['otdi'])
        self.assertFalse(response.data['keyingi_daraja']['ochildi'])
        self.assertFalse(daraja_ochiqmi(self.student, self.elementary))
        self.assertEqual(Sertifikat.objects.count(), 0)

    def test_80_percent_opens_next_level_and_creates_downloadable_certificate(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(
            f'/api/oquvchi/final-test/{self.beginner.id}/topshirish/',
            self._payload(8),
            format='json',
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertTrue(response.data['otdi'])
        self.assertTrue(response.data['keyingi_daraja']['ochildi'])
        self.assertIn('Elementary', response.data['xabar'])
        self.assertTrue(daraja_ochiqmi(self.student, self.elementary))

        certificate = Sertifikat.objects.get(oquvchi=self.student, daraja=self.beginner)
        self.assertEqual(float(certificate.foiz), 80.0)

        public_response = self.client.get(f'/api/sertifikat-tekshirish/{certificate.kod}/')
        self.assertEqual(public_response.status_code, 200)
        self.assertTrue(public_response.data['haqiqiy'])
        self.assertEqual(public_response.data['daraja_nomi'], 'Beginner')

        pdf_response = self.client.get(f'/api/sertifikat/{certificate.kod}/pdf/')
        self.assertEqual(pdf_response.status_code, 200)
        self.assertEqual(pdf_response['Content-Type'], 'application/pdf')
        self.assertTrue(pdf_response.content.startswith(b'%PDF'))

        qr_response = self.client.get(f'/api/sertifikat/{certificate.kod}/qr/')
        self.assertEqual(qr_response.status_code, 200)
        self.assertEqual(qr_response['Content-Type'], 'image/png')
        self.assertTrue(qr_response.content.startswith(b'\x89PNG'))

        self.client.force_authenticate(self.admin)
        admin_response = self.client.get('/api/admin/sertifikatlar/')
        self.assertEqual(admin_response.status_code, 200)
        self.assertEqual(len(admin_response.data), 1)
        self.assertEqual(admin_response.data[0]['oquvchi_ism'], 'Ali Valiyev')


class QuickGameAndShopTests(APITestCase):
    def setUp(self):
        from accounts.models import Filial
        from exams.models import ShopMahsulot, SozJuftligi

        self.branch = Filial.objects.create(nomi='Test filial')
        self.other_branch = Filial.objects.create(nomi='Boshqa filial')
        self.admin = User.objects.create_user(
            username='shop_admin', password='pass12345', role=User.ROLE_ADMIN,
        )
        self.manager = User.objects.create_user(
            username='manager', password='pass12345', role=User.ROLE_NAZORATCHI,
            filial=self.branch,
        )
        self.other_manager = User.objects.create_user(
            username='other_manager', password='pass12345', role=User.ROLE_NAZORATCHI,
            filial=self.other_branch,
        )
        self.student = User.objects.create_user(
            username='game_student', password='pass12345', role=User.ROLE_OQUVCHI,
            ism='Sardor', familya='Testov', filial=self.branch, yaratgan=self.manager,
        )
        self.fan = Fan.objects.create(nomi='Test English', tartib=1)
        self.level = Daraja.objects.create(fan=self.fan, nomi='Starter', tartib=1)
        OquvchiFan.objects.create(
            oquvchi=self.student, daraja=self.level, biriktirgan=self.manager, qolda_ochilgan=True,
        )
        for index in range(10):
            SozJuftligi.objects.create(
                fan=self.fan,
                chet_soz=f'word-{index}',
                uzbek_soz=f'soz-{index}',
                tartib=index + 1,
            )
        self.product = ShopMahsulot.objects.create(
            nomi='Test kitob', tavsif='Sinov mahsuloti', narx_coin=6, faol=True,
        )

    def test_quick_translation_game_awards_coins_only_once(self):
        from exams.models import OquvchiCoin, TezkorOyiniSessiya

        self.client.force_authenticate(self.student)
        start = self.client.get('/api/oquvchi/tezkor-oyin/')
        self.assertEqual(start.status_code, 200, start.data)
        self.assertEqual(len(start.data['savollar']), 10)
        self.assertNotIn('togri', start.data['savollar'][0])

        session = TezkorOyiniSessiya.objects.get(token=start.data['token'])
        answers = [
            {'savol': question['id'], 'javob': question['togri']}
            for question in session.savollar
        ]
        finish = self.client.post(
            f"/api/oquvchi/tezkor-oyin/{session.token}/yakunlash/",
            {'javoblar': answers},
            format='json',
        )
        self.assertEqual(finish.status_code, 200, finish.data)
        self.assertEqual(finish.data['togri_soni'], 10)
        self.assertEqual(finish.data['berilgan_coin'], 15)
        # 15 o'yin coini + bir martalik 10 coinlik "Tezkor tarjimon" yutug'i.
        self.assertEqual(finish.data['balans'], 25)

        second_finish = self.client.post(
            f"/api/oquvchi/tezkor-oyin/{session.token}/yakunlash/",
            {'javoblar': answers},
            format='json',
        )
        self.assertEqual(second_finish.status_code, 200)
        self.assertTrue(second_finish.data['allaqachon_yakunlangan'])
        self.assertEqual(OquvchiCoin.objects.get(oquvchi=self.student).balans, 25)

    def test_shop_purchase_is_visible_to_admin_and_same_branch_manager(self):
        from exams.models import OquvchiCoin, ShopBuyurtma

        OquvchiCoin.objects.create(oquvchi=self.student, balans=10)
        self.client.force_authenticate(self.student)
        purchase = self.client.post(f'/api/oquvchi/shop/{self.product.id}/xarid/', {}, format='json')
        self.assertEqual(purchase.status_code, 201, purchase.data)
        self.assertEqual(purchase.data['qolgan_balans'], 4)
        order = ShopBuyurtma.objects.get(oquvchi=self.student)

        self.client.force_authenticate(self.admin)
        admin_list = self.client.get('/api/boshqaruv/shop-buyurtmalar/')
        self.assertEqual(admin_list.status_code, 200)
        self.assertEqual(len(admin_list.data), 1)
        self.assertEqual(admin_list.data[0]['filial_nomi'], 'Test filial')

        self.client.force_authenticate(self.manager)
        manager_list = self.client.get('/api/boshqaruv/shop-buyurtmalar/')
        self.assertEqual(len(manager_list.data), 1)
        update = self.client.patch(
            f'/api/boshqaruv/shop-buyurtmalar/{order.id}/status/',
            {'status': 'berildi'},
            format='json',
        )
        self.assertEqual(update.status_code, 200)
        self.assertEqual(update.data['status'], 'berildi')

        self.client.force_authenticate(self.other_manager)
        other_list = self.client.get('/api/boshqaruv/shop-buyurtmalar/')
        self.assertEqual(other_list.status_code, 200)
        self.assertEqual(len(other_list.data), 0)
