from django.db import migrations


CORE_COURSES = [
    (
        'English',
        "Ingliz tilini alifbodan boshlab Advanced darajagacha o'rganing.",
        'GB',
        [
            ('Starter', ['Alphabet and Sounds', 'Greetings and Introductions', 'Numbers and Basic Words']),
            ('Beginner', ['Present Simple', 'Daily Routine', 'Basic Questions']),
            ('Elementary', ['Past Simple', 'Future Plans', 'Comparatives']),
            ('Pre-Intermediate', ['Present Perfect', 'Modal Verbs', 'Conditionals']),
            ('Intermediate', ['Passive Voice', 'Reported Speech', 'Relative Clauses']),
            ('Upper-Intermediate', ['Advanced Tenses', 'Academic Vocabulary', 'Complex Sentences']),
            ('Advanced', ['Nuanced Grammar', 'Formal Writing', 'Fluent Communication']),
        ],
    ),
    (
        'Rus tili',
        "Rus tilini alifbo va oddiy suhbatdan boshlab ravon nutq darajasigacha o'rganing.",
        'RU',
        [
            ('Starter', ['Rus alifbosi', 'Salomlashish va tanishish', 'Sonlar va asosiy so‘zlar']),
            ('Beginner', ['Otlarning jinsi', 'Hozirgi zamon', 'Oddiy savollar']),
            ('Elementary', ['O‘tgan zamon', 'Kelasi zamon', 'Sifatlar']),
            ('Pre-Intermediate', ['Kelishiklar', 'Harakat fe’llari', 'Bog‘langan gaplar']),
            ('Intermediate', ['Fe’l turlari', 'Qo‘shma gaplar', 'Bilvosita nutq']),
            ('Upper-Intermediate', ['Rasmiy uslub', 'Akademik lug‘at', 'Murakkab grammatika']),
            ('Advanced', ['Nutq nozikliklari', 'Professional yozish', 'Erkin muloqot']),
        ],
    ),
    (
        'Koreys tili',
        "Hangul alifbosidan boshlab TOPIK va professional koreys tili darajasigacha o'rganing.",
        'KR',
        [
            ('Starter', ['Hangul harflari', 'Salomlashish va tanishish', 'Sonlar va asosiy so‘zlar']),
            ('Beginner', ['Oddiy gap tuzilishi', 'Hozirgi zamon', 'Asosiy qo‘shimchalar']),
            ('Elementary', ['O‘tgan zamon', 'Kelasi zamon', 'Hurmat shakllari']),
            ('Pre-Intermediate', ['Bog‘lovchi qo‘shimchalar', 'Sabab va natija', 'Istak va reja']),
            ('Intermediate', ['Bilvosita nutq', 'Murakkab gaplar', 'TOPIK lug‘ati']),
            ('Upper-Intermediate', ['Rasmiy koreys tili', 'Akademik matn', 'Murakkab grammatika']),
            ('Advanced', ['Nutq nozikliklari', 'Professional yozish', 'Erkin muloqot']),
        ],
    ),
    (
        'Matematika',
        "Matematikaning asosiy tushunchalari, amallar, tenglamalar va geometriyani o'rganing.",
        '∑',
        [("Boshlang'ich", ['Natural sonlar va amallar', 'Kasrlar va ulushlar', 'Tenglamalar', 'Geometriya asoslari', 'Foiz va masalalar'])],
    ),
    (
        'Ona tili',
        "O'zbek tilining tovush, so'z, gap, imlo va matn tuzish qoidalarini o'rganing.",
        'UZ',
        [("Boshlang'ich", ['Tovush va harflar', "So'z turkumlari", "Gap bo'laklari", 'Imlo qoidalari', 'Matn va uslublar'])],
    ),
    (
        'Tarix',
        "Qadimgi davrdan O'zbekiston mustaqilligigacha bo'lgan muhim tarixiy jarayonlarni o'rganing.",
        'TRX',
        [("Boshlang'ich", ['Qadimgi dunyo', "O'rta asrlar", 'Temuriylar davri', 'Jadidchilik harakati', "O'zbekiston mustaqilligi"])],
    ),
    (
        'Huquq',
        "Konstitutsiya, fuqarolarning huquq va majburiyatlari hamda asosiy huquq sohalarini o'rganing.",
        '⚖',
        [("Boshlang'ich", ['Huquq tushunchasi', "O'zbekiston Konstitutsiyasi", 'Fuqarolik huquqi', 'Mehnat huquqi', 'Huquq va majburiyatlar'])],
    ),
    (
        'IT',
        "Algoritm, dasturlash, internet, ma'lumotlar bazasi va kiberxavfsizlik asoslarini o'rganing.",
        'IT',
        [("Boshlang'ich", ['Algoritm va dasturlash', 'Internet va tarmoqlar', "Ma'lumotlar bazasi", 'Web dasturlash', 'Kiberxavfsizlik'])],
    ),
    (
        'Kompyuter',
        "Kompyuter qurilmalari, operatsion tizim, fayllar, Office dasturlari va xavfsizlikni o'rganing.",
        'PC',
        [("Boshlang'ich", ['Kompyuter qurilmalari', 'Operatsion tizim', 'Fayl va papkalar', 'Microsoft Office', 'Kompyuter xavfsizligi'])],
    ),
    (
        'Arab tili',
        "Arab alifbosi, o'qish, kundalik so'zlar va oddiy gap tuzishni o'rganing.",
        'AR',
        [("Boshlang'ich", ['Arab alifbosi', 'Harakatlar va o‘qish', 'Salomlashish va tanishish', 'Ot va sifat', 'Oddiy gaplar'])],
    ),
    (
        'Turk tili',
        "Turk alifbosi, kundalik muloqot, zamonlar va oddiy gaplarni o'rganing.",
        'TR',
        [("Boshlang'ich", ['Turk alifbosi', 'Salomlashish va tanishish', 'Hozirgi zamon', 'So‘roq gaplar', 'Kundalik muloqot'])],
    ),
]


def seed_core_catalog(apps, schema_editor):
    Fan = apps.get_model('courses', 'Fan')
    Daraja = apps.get_model('courses', 'Daraja')
    Mavzu = apps.get_model('courses', 'Mavzu')
    Dars = apps.get_model('courses', 'Dars')

    for fan_order, (fan_name, description, icon, levels) in enumerate(CORE_COURSES, start=1):
        fan, _ = Fan.objects.update_or_create(
            nomi=fan_name,
            defaults={
                'tavsif': description,
                'icon': icon,
                'tartib': fan_order,
            },
        )

        for level_order, (level_name, topics) in enumerate(levels, start=1):
            level, _ = Daraja.objects.update_or_create(
                fan=fan,
                nomi=level_name,
                defaults={
                    'tartib': level_order,
                    'ochish_uchun_foiz': 80,
                },
            )

            for topic_order, topic_name in enumerate(topics, start=1):
                topic, _ = Mavzu.objects.update_or_create(
                    daraja=level,
                    tartib=topic_order,
                    defaults={'nomi': topic_name},
                )
                Dars.objects.update_or_create(
                    mavzu=topic,
                    tartib=1,
                    defaults={
                        'sarlavha': topic_name,
                        'tushuntirish_matn': (
                            f"{topic_name} — {fan_name} fanining {level_name} bosqichidagi mavzu. "
                            "Tushuntirishni o‘qing va testdan kamida 80% oling."
                        ),
                        'misollar': '',
                    },
                )


def noop_reverse(apps, schema_editor):
    # Tayyor katalog ma'lumotlari reverse migrationda o'chirilmaydi.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('courses', '0002_daraja_ochish_uchun_foiz_oquvchifan_qolda_ochilgan'),
    ]

    operations = [
        migrations.RunPython(seed_core_catalog, noop_reverse),
    ]
