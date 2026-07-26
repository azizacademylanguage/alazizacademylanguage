from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Filial, User
from courses.models import Dars, Daraja, Fan, Mavzu, OquvchiFan
from courses.utils import toza_daraja_nomi
from exams.models import (
    Bildirishnoma,
    FinalTest,
    FinalTestJavob,
    FinalTestSavol,
    Javob,
    ListeningSavol,
    Mashq,
    Savol,
    ShopMahsulot,
    SozJuftligi,
    SpeakingTopshiriq,
)


LANGUAGE_LEVELS = [
    'Starter',
    'Beginner',
    'Elementary',
    'Pre-Intermediate',
    'Intermediate',
    'Upper-Intermediate',
    'Advanced',
]


def language_levels(topics):
    return {level: topics[level] for level in LANGUAGE_LEVELS}


COURSES = {
    'English': {
        'description': "Ingliz tilini alifbodan boshlab erkin muloqot va Advanced darajagacha o'rganing.",
        'icon': 'GB',
        'aliases': ['English', 'Ingliz tili'],
        'lang_code': 'en-US',
        'is_language': True,
        'speaking': 'Hello, I study English every day and I enjoy learning new words.',
        'levels': language_levels({
            'Starter': ['Alphabet and Sounds', 'Greetings and Introductions', 'Numbers and Basic Words'],
            'Beginner': ['Present Simple', 'Daily Routine', 'Basic Questions'],
            'Elementary': ['Past Simple', 'Future Plans', 'Comparatives'],
            'Pre-Intermediate': ['Present Perfect', 'Modal Verbs', 'Conditionals'],
            'Intermediate': ['Passive Voice', 'Reported Speech', 'Relative Clauses'],
            'Upper-Intermediate': ['Advanced Tenses', 'Academic Vocabulary', 'Complex Sentences'],
            'Advanced': ['Nuanced Grammar', 'Formal Writing', 'Fluent Communication'],
        }),
        'words': [
            ('hello', 'salom'), ('book', 'kitob'), ('water', 'suv'), ('school', 'maktab'),
            ('friend', "do'st"), ('family', 'oila'), ('work', 'ish'), ('time', 'vaqt'),
            ('city', 'shahar'), ('language', 'til'),
        ],
    },
    'Rus tili': {
        'description': "Rus tilini alifbo va oddiy suhbatdan boshlab ravon nutq darajasigacha o'rganing.",
        'icon': 'RU',
        'aliases': ['Rus tili', 'Russia', 'Russian'],
        'lang_code': 'ru-RU',
        'is_language': True,
        'speaking': 'Здравствуйте, я каждый день изучаю русский язык и повторяю новые слова.',
        'levels': language_levels({
            'Starter': ['Rus alifbosi', 'Salomlashish va tanishish', 'Sonlar va asosiy so‘zlar'],
            'Beginner': ['Otlarning jinsi', 'Hozirgi zamon', 'Oddiy savollar'],
            'Elementary': ['O‘tgan zamon', 'Kelasi zamon', 'Sifatlar'],
            'Pre-Intermediate': ['Kelishiklar', 'Harakat fe’llari', 'Bog‘langan gaplar'],
            'Intermediate': ['Fe’l turlari', 'Qo‘shma gaplar', 'Bilvosita nutq'],
            'Upper-Intermediate': ['Rasmiy uslub', 'Akademik lug‘at', 'Murakkab grammatika'],
            'Advanced': ['Nutq nozikliklari', 'Professional yozish', 'Erkin muloqot'],
        }),
        'words': [
            ('привет', 'salom'), ('книга', 'kitob'), ('вода', 'suv'), ('школа', 'maktab'),
            ('друг', "do'st"), ('семья', 'oila'), ('работа', 'ish'), ('время', 'vaqt'),
            ('город', 'shahar'), ('язык', 'til'),
        ],
    },
    'Koreys tili': {
        'description': "Hangul alifbosidan boshlab TOPIK va professional koreys tili darajasigacha o'rganing.",
        'icon': 'KR',
        'aliases': ['Koreys tili', 'Korean', 'Koreys tili '],
        'lang_code': 'ko-KR',
        'is_language': True,
        'speaking': '안녕하세요. 저는 매일 한국어를 공부하고 새로운 단어를 연습합니다.',
        'levels': language_levels({
            'Starter': ['Hangul harflari', 'Salomlashish va tanishish', 'Sonlar va asosiy so‘zlar'],
            'Beginner': ['Oddiy gap tuzilishi', 'Hozirgi zamon', 'Asosiy qo‘shimchalar'],
            'Elementary': ['O‘tgan zamon', 'Kelasi zamon', 'Hurmat shakllari'],
            'Pre-Intermediate': ['Bog‘lovchi qo‘shimchalar', 'Sabab va natija', 'Istak va reja'],
            'Intermediate': ['Bilvosita nutq', 'Murakkab gaplar', 'TOPIK lug‘ati'],
            'Upper-Intermediate': ['Rasmiy koreys tili', 'Akademik matn', 'Murakkab grammatika'],
            'Advanced': ['Nutq nozikliklari', 'Professional yozish', 'Erkin muloqot'],
        }),
        'words': [
            ('안녕하세요', 'salom'), ('책', 'kitob'), ('물', 'suv'), ('학교', 'maktab'),
            ('친구', "do'st"), ('가족', 'oila'), ('일', 'ish'), ('시간', 'vaqt'),
            ('도시', 'shahar'), ('언어', 'til'),
        ],
    },
    'Matematika': {
        'description': "Matematikaning asosiy tushunchalari, amallar, tenglamalar va geometriyani o'rganing.",
        'icon': '∑',
        'aliases': ['Matematika', 'Matem'],
        'lang_code': 'uz-UZ',
        'is_language': False,
        'speaking': "Natural sonlar, kasrlar, tenglamalar va geometrik shakllar matematikaning asosiy mavzularidir.",
        'levels': {
            "Boshlang'ich": [
                'Natural sonlar va amallar',
                'Kasrlar va ulushlar',
                'Tenglamalar',
                'Geometriya asoslari',
                'Foiz va masalalar',
            ],
        },
        'words': [
            ('natural son', 'sanashda ishlatiladigan musbat butun son'),
            ("qo'shish", 'sonlarni birlashtirish amali'),
            ('ayirish', 'ikki son orasidagi farqni topish amali'),
            ("ko'paytirish", "bir sonni takroriy qo'shish amali"),
            ("bo'lish", 'miqdorni teng qismlarga ajratish amali'),
            ('kasr', 'butunning bir yoki bir nechta qismini ifodalovchi son'),
            ('tenglama', "noma'lum son qatnashgan tenglik"),
            ('perimetr', "shakl tomonlari uzunliklarining yig'indisi"),
            ('yuza', 'shakl egallagan tekislik miqdori'),
            ('foiz', 'yuzdan bir ulush'),
        ],
    },
    'Ona tili': {
        'description': "O'zbek tilining tovush, so'z, gap, imlo va matn tuzish qoidalarini o'rganing.",
        'icon': 'UZ',
        'aliases': ['Ona tili', "O'zbek tili"],
        'lang_code': 'uz-UZ',
        'is_language': False,
        'speaking': "Ona tili fikrimizni to'g'ri, ravon va tushunarli ifodalashga yordam beradi.",
        'levels': {
            "Boshlang'ich": [
                'Tovush va harflar',
                "So'z turkumlari",
                "Gap bo'laklari",
                'Imlo qoidalari',
                'Matn va uslublar',
            ],
        },
        'words': [
            ('tovush', "nutqda eshitiladigan eng kichik birlik"),
            ('harf', 'tovushning yozuvdagi belgisi'),
            ('ot', 'shaxs, narsa yoki joy nomini bildiruvchi so‘z'),
            ('sifat', 'narsa va shaxsning belgisini bildiruvchi so‘z'),
            ('fe’l', 'harakat yoki holatni bildiruvchi so‘z'),
            ('ega', 'gapda kim yoki nima haqida fikr bildirilganini ko‘rsatuvchi bo‘lak'),
            ('kesim', 'eganing harakati yoki holatini bildiruvchi bo‘lak'),
            ('imlo', "so'zlarni to'g'ri yozish qoidalari"),
            ('gap', 'tugallangan fikrni bildiruvchi birlik'),
            ('matn', 'mazmunan bog‘langan gaplar to‘plami'),
        ],
    },
    'Tarix': {
        'description': "Qadimgi davrdan O'zbekiston mustaqilligigacha bo'lgan muhim tarixiy jarayonlarni o'rganing.",
        'icon': 'TRX',
        'aliases': ['Tarix'],
        'lang_code': 'uz-UZ',
        'is_language': False,
        'speaking': "Tarix o'tmishdagi voqealar, xalqlar va davlatlarning rivojlanishini o'rganadi.",
        'levels': {
            "Boshlang'ich": [
                'Qadimgi dunyo',
                "O'rta asrlar",
                'Temuriylar davri',
                'Jadidchilik harakati',
                "O'zbekiston mustaqilligi",
            ],
        },
        'words': [
            ('tarix', "insoniyat o'tmishini o'rganuvchi fan"),
            ('manba', "o'tmish haqida ma'lumot beruvchi dalil"),
            ('davlat', 'muayyan hudud va boshqaruv tizimiga ega siyosiy tuzilma'),
            ('sivilizatsiya', 'jamiyat taraqqiyotining yuksak bosqichi'),
            ('sulola', 'bir avlodga mansub hukmdorlar ketma-ketligi'),
            ('saltanat', 'katta hududni birlashtirgan davlat'),
            ('jadid', "yangicha ta'lim va taraqqiyot tarafdori"),
            ('mustaqillik', "davlatning o'z taqdirini erkin belgilashi"),
            ('arxeologiya', 'qadimiy topilmalar orqali tarixni o‘rganuvchi fan'),
            ('xronologiya', 'voqealarning vaqt bo‘yicha ketma-ketligi'),
        ],
    },
    'Huquq': {
        'description': "Konstitutsiya, fuqarolarning huquq va majburiyatlari hamda asosiy huquq sohalarini o'rganing.",
        'icon': '⚖',
        'aliases': ['Huquq', 'Huquqshunoslik'],
        'lang_code': 'uz-UZ',
        'is_language': False,
        'speaking': "Huquq jamiyatdagi munosabatlarni tartibga soladi va inson huquqlarini himoya qiladi.",
        'levels': {
            "Boshlang'ich": [
                'Huquq tushunchasi',
                "O'zbekiston Konstitutsiyasi",
                'Fuqarolik huquqi',
                'Mehnat huquqi',
                'Huquq va majburiyatlar',
            ],
        },
        'words': [
            ('huquq', 'davlat tomonidan belgilangan va himoya qilinadigan qoidalar tizimi'),
            ('konstitutsiya', 'davlatning asosiy qonuni'),
            ('qonun', 'barcha uchun majburiy huquqiy qoida'),
            ('fuqaro', 'muayyan davlatga huquqiy mansub shaxs'),
            ('majburiyat', 'bajarilishi shart bo‘lgan vazifa'),
            ('javobgarlik', 'qoidabuzarlik oqibatlari uchun javob berish'),
            ('shartnoma', 'tomonlar o‘rtasidagi huquqiy kelishuv'),
            ('mehnat huquqi', 'xodim va ish beruvchi munosabatlarini tartibga soluvchi soha'),
            ('sud', 'nizolarni qonun asosida hal qiluvchi organ'),
            ('adolat', 'huquq va tenglikka asoslangan munosabat'),
        ],
    },
    'IT': {
        'description': "Algoritm, dasturlash, internet, ma'lumotlar bazasi va kiberxavfsizlik asoslarini o'rganing.",
        'icon': 'IT',
        'aliases': ['IT', 'Axborot texnologiyalari'],
        'lang_code': 'uz-UZ',
        'is_language': False,
        'speaking': "Axborot texnologiyalari ma'lumotlarni yaratish, saqlash va uzatish imkonini beradi.",
        'levels': {
            "Boshlang'ich": [
                'Algoritm va dasturlash',
                'Internet va tarmoqlar',
                "Ma'lumotlar bazasi",
                'Web dasturlash',
                'Kiberxavfsizlik',
            ],
        },
        'words': [
            ('algoritm', 'muammoni yechish uchun aniq ketma-ket ko‘rsatmalar'),
            ('dastur', 'kompyuter bajaradigan buyruqlar to‘plami'),
            ('kod', 'dasturlash tilida yozilgan buyruqlar'),
            ('internet', 'dunyo bo‘ylab ulangan kompyuter tarmoqlari tizimi'),
            ('server', 'boshqa qurilmalarga xizmat ko‘rsatuvchi kompyuter yoki dastur'),
            ('database', "tartiblangan ma'lumotlar to'plami"),
            ('frontend', 'foydalanuvchi ko‘radigan va ishlatadigan dastur qismi'),
            ('backend', 'server, baza va biznes mantiq ishlaydigan dastur qismi'),
            ('parol', 'hisobni himoya qiluvchi maxfiy belgilar to‘plami'),
            ('kiberxavfsizlik', 'raqamli tizim va ma’lumotlarni himoya qilish sohasi'),
        ],
    },
    'Kompyuter': {
        'description': "Kompyuter qurilmalari, operatsion tizim, fayllar, Office dasturlari va xavfsizlikni o'rganing.",
        'icon': 'PC',
        'aliases': ['Kompyuter', 'Kompyuter savodxonligi'],
        'lang_code': 'uz-UZ',
        'is_language': False,
        'speaking': "Kompyuter ma'lumotlarni qayta ishlaydigan elektron qurilma bo'lib, ko'plab dasturlar bilan ishlaydi.",
        'levels': {
            "Boshlang'ich": [
                'Kompyuter qurilmalari',
                'Operatsion tizim',
                'Fayl va papkalar',
                'Microsoft Office',
                'Kompyuter xavfsizligi',
            ],
        },
        'words': [
            ('monitor', 'tasvirni ekranda ko‘rsatuvchi qurilma'),
            ('klaviatura', 'matn va buyruqlarni kiritish qurilmasi'),
            ('sichqoncha', 'kursorni boshqarish qurilmasi'),
            ('protsessor', 'hisoblash va buyruqlarni bajaruvchi asosiy qurilma'),
            ('xotira', 'ma’lumotlarni saqlash uchun ishlatiladigan qurilma'),
            ('operatsion tizim', 'kompyuter qurilmalari va dasturlarini boshqaruvchi tizim'),
            ('fayl', 'nom bilan saqlangan ma’lumotlar birligi'),
            ('papka', 'fayllarni tartiblab saqlash joyi'),
            ('Word', 'matnli hujjatlar bilan ishlash dasturi'),
            ('Excel', 'jadval va hisob-kitoblar bilan ishlash dasturi'),
        ],
    },
    'Arab tili': {
        'description': "Arab alifbosi, o'qish, kundalik so'zlar va oddiy gap tuzishni o'rganing.",
        'icon': 'AR',
        'aliases': ['Arab tili', 'Arabic'],
        'lang_code': 'ar-SA',
        'is_language': True,
        'speaking': 'مرحباً، أنا أتعلم اللغة العربية كل يوم وأراجع الكلمات الجديدة.',
        'levels': {
            "Boshlang'ich": [
                'Arab alifbosi',
                'Harakatlar va o‘qish',
                'Salomlashish va tanishish',
                'Ot va sifat',
                'Oddiy gaplar',
            ],
        },
        'words': [
            ('مرحبا', 'salom'), ('كتاب', 'kitob'), ('ماء', 'suv'), ('مدرسة', 'maktab'),
            ('صديق', "do'st"), ('عائلة', 'oila'), ('عمل', 'ish'), ('وقت', 'vaqt'),
            ('مدينة', 'shahar'), ('لغة', 'til'),
        ],
    },
    'Turk tili': {
        'description': "Turk alifbosi, kundalik muloqot, zamonlar va oddiy gaplarni o'rganing.",
        'icon': 'TR',
        'aliases': ['Turk tili', 'Turkish'],
        'lang_code': 'tr-TR',
        'is_language': True,
        'speaking': 'Merhaba, her gün Türkçe öğreniyorum ve yeni kelimeleri tekrar ediyorum.',
        'levels': {
            "Boshlang'ich": [
                'Turk alifbosi',
                'Salomlashish va tanishish',
                'Hozirgi zamon',
                'So‘roq gaplar',
                'Kundalik muloqot',
            ],
        },
        'words': [
            ('merhaba', 'salom'), ('kitap', 'kitob'), ('su', 'suv'), ('okul', 'maktab'),
            ('arkadaş', "do'st"), ('aile', 'oila'), ('iş', 'ish'), ('zaman', 'vaqt'),
            ('şehir', 'shahar'), ('dil', 'til'),
        ],
    },
}


class Command(BaseCommand):
    help = "Tayyor fanlar, darajalar, mavzular va 10 savollik testlarni yaratadi yoki yangilaydi."

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
        created_topics = 0

        for fan_order, (fan_name, data) in enumerate(COURSES.items(), start=1):
            fan = self._get_or_create_fan(fan_name, data, fan_order)
            self._create_word_game_words(fan, data['words'])

            for level_order, (level_name, topics) in enumerate(data['levels'].items(), start=1):
                level = self._get_or_create_level(fan, level_name, level_order)
                created_levels.append(level)
                for topic_order, topic_name in enumerate(topics, start=1):
                    self._create_topic_content(
                        level=level,
                        topic_name=topic_name,
                        topic_order=topic_order,
                        words=data['words'],
                        lang_code=data['lang_code'],
                        speaking_text=data['speaking'],
                        is_language=data.get('is_language', False),
                    )
                    created_topics += 1
                self._create_final_test(level, topics, data['words'], data.get('is_language', False))

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
            f"Tayyor: {len(COURSES)} ta fan, {len(created_levels)} ta daraja va {created_topics} ta mavzu yaratildi yoki yangilandi."
        ))
        if not catalog_only:
            self.stdout.write('Loginlar: admin/admin12345, nazoratchi1/naz12345, oquvchi1/stud12345')

    def _create_word_game_words(self, fan, words):
        for order, (term, meaning) in enumerate(words[:10], start=1):
            SozJuftligi.objects.update_or_create(
                fan=fan,
                chet_soz=term,
                uzbek_soz=meaning,
                defaults={'tartib': order, 'faol': True},
            )

    def _create_shop_items(self):
        items = [
            ('AL-AZIZ daftar', "Akademiya logotipli o'quv daftari", 25),
            ('Premium ruchka', "Darslar uchun sifatli ruchka", 35),
            ('Til o‘rganish kitobi', "Tanlangan fan bo‘yicha qo‘shimcha mashqlar kitobi", 80),
            ('Academy futbolkasi', "AL-AZIZ ACADEMY yozuvli futbolka", 160),
            ('Maxsus nishon', "Profil uchun yutuq nishoni", 50),
            ('Ustoz bilan bonus dars', "30 daqiqalik individual bonus dars", 220),
        ]
        for name, description, price in items:
            ShopMahsulot.objects.update_or_create(
                nomi=name,
                defaults={'tavsif': description, 'narx_coin': price, 'faol': True},
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
        aliases = data.get('aliases') or [fan_name]
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

    def _create_topic_content(self, level, topic_name, topic_order, words, lang_code, speaking_text, is_language):
        topic, _ = Mavzu.objects.update_or_create(
            daraja=level,
            tartib=topic_order,
            defaults={'nomi': topic_name},
        )
        subject_word = 'tilidagi' if is_language else 'fanidagi'
        lesson, _ = Dars.objects.update_or_create(
            mavzu=topic,
            tartib=1,
            defaults={
                'sarlavha': topic_name,
                'tushuntirish_matn': (
                    f"{topic_name} — {level.fan.nomi} {subject_word} {level.nomi} bosqichining muhim mavzusi. "
                    "Avval tushuntirishni o‘qing, misollarni takrorlang va so‘ng 10 savollik testni yeching. "
                    "Keyingi mavzu ochilishi uchun kamida 80% natija kerak."
                ),
                'misollar': '\n'.join(
                    f"{idx + 1}. {term} — {meaning}" for idx, (term, meaning) in enumerate(words[:5])
                ),
            },
        )

        ListeningSavol.objects.filter(dars=lesson).delete()
        for idx, (term, meaning) in enumerate(words[:10], start=1):
            wrongs = [
                words[idx % len(words)][1],
                words[(idx + 2) % len(words)][1],
                words[(idx + 4) % len(words)][1],
            ]
            variants = [meaning] + [item for item in wrongs if item != meaning]
            while len(variants) < 4:
                variants.append(f'Noto‘g‘ri variant {len(variants)}')
            ListeningSavol.objects.create(
                dars=lesson,
                audio_matn=term,
                savol=(
                    "Eshitgan so‘zingizning o‘zbekcha tarjimasini tanlang."
                    if is_language else
                    "Eshitgan atamangizga mos ta’rifni tanlang."
                ),
                variantlar=variants[:4],
                togri_javob=meaning,
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
                'sarlavha': f'{topic_name} — 10 savollik test',
                'otish_bali_foiz': 80,
                'vaqt_chegarasi_daq': 15,
            },
        )
        mashq.savollar.all().delete()
        for idx, (term, meaning) in enumerate(words, start=1):
            question = Savol.objects.create(
                mashq=mashq,
                matn=(
                    f'"{term}" so‘zining o‘zbekcha ma’nosini tanlang.'
                    if is_language else
                    f'"{term}" atamasiga mos ta’rifni tanlang.'
                ),
                tur=Savol.TUR_SINGLE,
                tartib=idx,
            )
            choices = [
                meaning,
                words[idx % len(words)][1],
                words[(idx + 2) % len(words)][1],
                words[(idx + 4) % len(words)][1],
            ]
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
                    togri=choice == meaning,
                    tartib=choice_order,
                )

    def _create_final_test(self, level, topics, words, is_language):
        final_test, _ = FinalTest.objects.update_or_create(
            daraja=level,
            defaults={'sarlavha': f'{level.nomi} yakuniy testi', 'otish_bali_foiz': 80},
        )
        final_test.savollar.all().delete()
        for idx, (term, meaning) in enumerate(words, start=1):
            topic = topics[(idx - 1) % len(topics)]
            question = FinalTestSavol.objects.create(
                final_test=final_test,
                matn=(
                    f'{topic}: "{term}" so‘zining to‘g‘ri tarjimasini belgilang.'
                    if is_language else
                    f'{topic}: "{term}" atamasiga mos ta’rifni belgilang.'
                ),
                tartib=idx,
            )
            choices = [
                meaning,
                words[idx % len(words)][1],
                words[(idx + 3) % len(words)][1],
                words[(idx + 6) % len(words)][1],
            ]
            unique = []
            for choice in choices:
                if choice not in unique:
                    unique.append(choice)
            while len(unique) < 4:
                unique.append(f'Noto‘g‘ri javob {len(unique)}')
            for choice_order, choice in enumerate(unique[:4], start=1):
                FinalTestJavob.objects.create(
                    savol=question,
                    matn=choice,
                    togri=choice == meaning,
                    tartib=choice_order,
                )
