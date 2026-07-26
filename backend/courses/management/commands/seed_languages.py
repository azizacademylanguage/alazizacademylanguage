from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Filial, User
from courses.models import Dars, Daraja, Fan, Mavzu, OquvchiFan
from courses.utils import toza_daraja_nomi
from exams.models import (
    FinalTest, FinalTestJavob, FinalTestSavol,
    Javob, Mashq, Savol, ShopMahsulot, SozJuftligi,
    ListeningSavol, SpeakingTopshiriq, Bildirishnoma,
)


LEVELS = [
    'Starter',
    'Beginner',
    'Elementary',
    'Pre-Intermediate',
    'Intermediate',
    'Upper-Intermediate',
    'Advanced',
]

LANGUAGES = {
    'English': {
        'description': "Ingliz tilini alifbodan boshlab erkin muloqot va Advanced darajagacha o'rganing.",
        'icon': 'GB',
        'lang_code': 'en-US',
        'speaking': 'Hello, I study English every day and I enjoy learning new words.',
        'topics': {
            'Starter': ['Alphabet and Sounds', 'Greetings and Introductions', 'Numbers and Basic Words'],
            'Beginner': ['Present Simple', 'Daily Routine', 'Basic Questions'],
            'Elementary': ['Past Simple', 'Future Plans', 'Comparatives'],
            'Pre-Intermediate': ['Present Perfect', 'Modal Verbs', 'Conditionals'],
            'Intermediate': ['Passive Voice', 'Reported Speech', 'Relative Clauses'],
            'Upper-Intermediate': ['Advanced Tenses', 'Academic Vocabulary', 'Complex Sentences'],
            'Advanced': ['Nuanced Grammar', 'Formal Writing', 'Fluent Communication'],
        },
        'words': [
            ('hello', 'salom'), ('book', 'kitob'), ('water', 'suv'), ('school', 'maktab'),
            ('friend', "do'st"), ('family', 'oila'), ('work', 'ish'), ('time', 'vaqt'),
            ('city', 'shahar'), ('language', 'til'),
        ],
    },
    'Rus tili': {
        'description': "Rus tilini alifbo va oddiy suhbatdan boshlab ravon nutq darajasigacha o'rganing.",
        'icon': 'RU',
        'lang_code': 'ru-RU',
        'speaking': 'Здравствуйте, я каждый день изучаю русский язык и повторяю новые слова.',
        'topics': {
            'Starter': ['Rus alifbosi', 'Salomlashish va tanishish', 'Sonlar va asosiy so‘zlar'],
            'Beginner': ['Otlarning jinsi', 'Hozirgi zamon', 'Oddiy savollar'],
            'Elementary': ['O‘tgan zamon', 'Kelasi zamon', 'Sifatlar'],
            'Pre-Intermediate': ['Kelishiklar', 'Harakat fe’llari', 'Bog‘langan gaplar'],
            'Intermediate': ['Fe’l turlari', 'Qo‘shma gaplar', 'Bilvosita nutq'],
            'Upper-Intermediate': ['Rasmiy uslub', 'Akademik lug‘at', 'Murakkab grammatika'],
            'Advanced': ['Nutq nozikliklari', 'Professional yozish', 'Erkin muloqot'],
        },
        'words': [
            ('привет', 'salom'), ('книга', 'kitob'), ('вода', 'suv'), ('школа', 'maktab'),
            ('друг', "do'st"), ('семья', 'oila'), ('работа', 'ish'), ('время', 'vaqt'),
            ('город', 'shahar'), ('язык', 'til'),
        ],
    },
    'Koreys tili': {
        'description': "Hangul alifbosidan boshlab TOPIK va professional koreys tili darajasigacha o'rganing.",
        'icon': 'KR',
        'lang_code': 'ko-KR',
        'speaking': '안녕하세요. 저는 매일 한국어를 공부하고 새로운 단어를 연습합니다.',
        'topics': {
            'Starter': ['Hangul harflari', 'Salomlashish va tanishish', 'Sonlar va asosiy so‘zlar'],
            'Beginner': ['Oddiy gap tuzilishi', 'Hozirgi zamon', 'Asosiy qo‘shimchalar'],
            'Elementary': ['O‘tgan zamon', 'Kelasi zamon', 'Hurmat shakllari'],
            'Pre-Intermediate': ['Bog‘lovchi qo‘shimchalar', 'Sabab va natija', 'Istak va reja'],
            'Intermediate': ['Bilvosita nutq', 'Murakkab gaplar', 'TOPIK lug‘ati'],
            'Upper-Intermediate': ['Rasmiy koreys tili', 'Akademik matn', 'Murakkab grammatika'],
            'Advanced': ['Nutq nozikliklari', 'Professional yozish', 'Erkin muloqot'],
        },
        'words': [
            ('안녕하세요', 'salom'), ('책', 'kitob'), ('물', 'suv'), ('학교', 'maktab'),
            ('친구', "do'st"), ('가족', 'oila'), ('일', 'ish'), ('시간', 'vaqt'),
            ('도시', 'shahar'), ('언어', 'til'),
        ],
    },
}


class Command(BaseCommand):
    help = "English, Rus tili va Koreys tili kurslarini daraja, mavzu va 10 savollik testlari bilan yaratadi."

    def add_arguments(self, parser):
        parser.add_argument(
            '--catalog-only',
            action='store_true',
            help="Faqat fanlar, darajalar, testlar, so'zlar va do'kon mahsulotlarini yaratadi.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        catalog_only = options.get('catalog_only', False)
        admin = None if catalog_only else self._create_users()
        created_levels = []

        for fan_order, (fan_name, data) in enumerate(LANGUAGES.items(), start=1):
            fan = self._get_or_create_fan(fan_name, data, fan_order)
            self._create_word_game_words(fan, data['words'])
            for level_order, level_name in enumerate(LEVELS, start=1):
                level = self._get_or_create_level(fan, level_name, level_order)
                created_levels.append(level)
                for topic_order, topic_name in enumerate(data['topics'][level_name], start=1):
                    self._create_topic_content(
                        level=level,
                        topic_name=topic_name,
                        topic_order=topic_order,
                        words=data['words'],
                        lang_code=data['lang_code'],
                        speaking_text=data['speaking'],
                    )
                self._create_final_test(level, data['topics'][level_name], data['words'])

        self._create_shop_items()

        if not catalog_only:
            demo = User.objects.get(username='oquvchi1')
            english_beginner = Daraja.objects.get(fan__nomi='English', nomi='Beginner')
            OquvchiFan.objects.filter(oquvchi=demo).delete()
            OquvchiFan.objects.create(
                oquvchi=demo,
                daraja=english_beginner,
                biriktirgan=admin,
                qolda_ochilgan=True,
            )
            Bildirishnoma.objects.get_or_create(
                oquvchi=demo,
                sarlavha='Platformaga xush kelibsiz!',
                defaults={
                    'matn': 'Bugungi shaxsiy rejangizni oching, listening va speaking mashqlarini bajaring.',
                    'tur': 'info',
                    'havola': '/oquvchi',
                },
            )

        self.stdout.write(self.style.SUCCESS(
            f"Tayyor: 3 ta fan, {len(created_levels)} ta daraja, Listening, Speaking, QR sertifikat, streak va PWA ma'lumotlari."
        ))
        if not catalog_only:
            self.stdout.write("Loginlar: admin/admin12345, nazoratchi1/naz12345, oquvchi1/stud12345")

    def _create_word_game_words(self, fan, words):
        """Har bir fan uchun so'z o'yinida ishlatiladigan aynan 10 ta tarjima jufti."""
        for order, (foreign, uzbek) in enumerate(words[:10], start=1):
            SozJuftligi.objects.update_or_create(
                fan=fan,
                chet_soz=foreign,
                uzbek_soz=uzbek,
                defaults={'tartib': order, 'faol': True},
            )

    def _create_shop_items(self):
        items = [
            ('AL-AZIZ daftar', "Akademiya logotipli o'quv daftari", 25),
            ('Premium ruchka', "Darslar uchun sifatli ruchka", 35),
            ('Til o‘rganish kitobi', "Tanlangan til bo‘yicha qo‘shimcha mashqlar kitobi", 80),
            ('Academy futbolkasi', "AL-AZIZ ACADEMY yozuvli futbolka", 160),
            ('Maxsus nishon', "Profil uchun yutuq nishoni", 50),
            ('Ustoz bilan bonus dars', "30 daqiqalik individual bonus dars", 220),
        ]
        for name, description, price in items:
            ShopMahsulot.objects.update_or_create(
                nomi=name,
                defaults={
                    'tavsif': description,
                    'narx_coin': price,
                    'faol': True,
                },
            )

    def _create_users(self):
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={'role': User.ROLE_ADMIN, 'is_staff': True, 'is_superuser': True},
        )
        if created or not admin.check_password('admin12345'):
            admin.set_password('admin12345')
        admin.role = User.ROLE_ADMIN
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()

        filial, _ = Filial.objects.get_or_create(
            nomi='Asosiy filial',
            defaults={'manzil': 'Toshkent'},
        )
        naz, created = User.objects.get_or_create(
            username='nazoratchi1',
            defaults={
                'role': User.ROLE_NAZORATCHI,
                'filial': filial,
                'ism': 'Aziz',
                'familya': 'Karimov',
                'yaratgan': admin,
            },
        )
        if created or not naz.check_password('naz12345'):
            naz.set_password('naz12345')
        naz.role = User.ROLE_NAZORATCHI
        naz.filial = filial
        naz.save()

        student, created = User.objects.get_or_create(
            username='oquvchi1',
            defaults={
                'role': User.ROLE_OQUVCHI,
                'filial': filial,
                'ism': 'Malika',
                'familya': 'Yusupova',
                'yaratgan': admin,
            },
        )
        if created or not student.check_password('stud12345'):
            student.set_password('stud12345')
        student.role = User.ROLE_OQUVCHI
        student.filial = filial
        student.yaratgan = admin
        student.save()
        return admin

    def _get_or_create_fan(self, fan_name, data, order):
        aliases = {
            'English': ['English', 'Ingliz tili'],
            'Rus tili': ['Rus tili', 'Russia', 'Russian'],
            'Koreys tili': ['Koreys tili', 'Korean', 'Koreys tili '],
        }[fan_name]
        fan = Fan.objects.filter(nomi__in=aliases).order_by('id').first()
        if not fan:
            fan = Fan(nomi=fan_name)
        fan.nomi = fan_name
        fan.tavsif = data['description']
        fan.icon = data['icon']
        fan.tartib = order
        fan.save()
        return fan

    def _get_or_create_level(self, fan, level_name, order):
        level = None
        for candidate in fan.darajalar.all():
            if toza_daraja_nomi(candidate.nomi).lower() == level_name.lower():
                level = candidate
                break
        if level is None:
            level = Daraja(fan=fan, nomi=level_name)
        level.nomi = level_name
        level.tartib = order
        level.ochish_uchun_foiz = 80
        level.save()
        return level

    def _create_topic_content(self, level, topic_name, topic_order, words, lang_code, speaking_text):
        topic, _ = Mavzu.objects.update_or_create(
            daraja=level,
            tartib=topic_order,
            defaults={'nomi': topic_name},
        )
        lesson, _ = Dars.objects.update_or_create(
            mavzu=topic,
            tartib=1,
            defaults={
                'sarlavha': topic_name,
                'tushuntirish_matn': (
                    f"{topic_name} - {level.fan.nomi} tilidagi {level.nomi} darajasining muhim mavzusi. "
                    "Avval qoidani o'qing, misollarni takrorlang va so'ng 10 savollik testni yeching. "
                    "Keyingi mavzu ochilishi uchun kamida 80% natija kerak."
                ),
                'misollar': '\n'.join(
                    f"{idx + 1}. {foreign} - {uzbek}" for idx, (foreign, uzbek) in enumerate(words[:5])
                ),
            },
        )
        ListeningSavol.objects.filter(dars=lesson).delete()
        for idx, (foreign, uzbek) in enumerate(words[:10], start=1):
            wrongs = [
                words[idx % len(words)][1],
                words[(idx + 2) % len(words)][1],
                words[(idx + 4) % len(words)][1],
            ]
            variants = [uzbek] + [item for item in wrongs if item != uzbek]
            while len(variants) < 4:
                variants.append(f'Noto‘g‘ri variant {len(variants)}')
            ListeningSavol.objects.create(
                dars=lesson,
                audio_matn=foreign,
                savol="Eshitgan so‘zingizning o‘zbekcha tarjimasini tanlang.",
                variantlar=variants[:4],
                togri_javob=uzbek,
                til_kodi=lang_code,
                tartib=idx,
            )

        SpeakingTopshiriq.objects.update_or_create(
            dars=lesson,
            tartib=1,
            defaults={'matn': speaking_text},
        )

        mashq, _ = Mashq.objects.update_or_create(
            dars=lesson,
            defaults={
                'sarlavha': f'{topic_name} - 10 savollik test',
                'otish_bali_foiz': 80,
                'vaqt_chegarasi_daq': 15,
            },
        )
        mashq.savollar.all().delete()
        for idx, (foreign, uzbek) in enumerate(words, start=1):
            question = Savol.objects.create(
                mashq=mashq,
                matn=f'"{foreign}" so‘zining o‘zbekcha ma’nosini tanlang.',
                tur=Savol.TUR_SINGLE,
                tartib=idx,
            )
            wrong1 = words[(idx) % len(words)][1]
            wrong2 = words[(idx + 2) % len(words)][1]
            wrong3 = words[(idx + 4) % len(words)][1]
            choices = [uzbek, wrong1, wrong2, wrong3]
            unique = []
            for choice in choices:
                if choice not in unique:
                    unique.append(choice)
            while len(unique) < 4:
                unique.append(f'Noto‘g‘ri variant {len(unique)}')
            for choice_order, choice in enumerate(unique[:4], start=1):
                Javob.objects.create(
                    savol=question,
                    matn=choice,
                    togri=choice == uzbek,
                    tartib=choice_order,
                )

    def _create_final_test(self, level, topics, words):
        final_test, _ = FinalTest.objects.update_or_create(
            daraja=level,
            defaults={
                'sarlavha': f'{level.nomi} yakuniy testi',
                'otish_bali_foiz': 80,
            },
        )
        final_test.savollar.all().delete()
        for idx, (foreign, uzbek) in enumerate(words, start=1):
            topic = topics[(idx - 1) % len(topics)]
            question = FinalTestSavol.objects.create(
                final_test=final_test,
                matn=f'{topic}: "{foreign}" so‘zining to‘g‘ri tarjimasini belgilang.',
                tartib=idx,
            )
            wrongs = [
                words[(idx) % len(words)][1],
                words[(idx + 3) % len(words)][1],
                words[(idx + 6) % len(words)][1],
            ]
            choices = [uzbek] + [x for x in wrongs if x != uzbek]
            while len(choices) < 4:
                choices.append(f'Noto‘g‘ri javob {len(choices)}')
            for choice_order, choice in enumerate(choices[:4], start=1):
                FinalTestJavob.objects.create(
                    savol=question,
                    matn=choice,
                    togri=choice == uzbek,
                    tartib=choice_order,
                )
