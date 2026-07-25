from collections import defaultdict

from django.contrib.auth import get_user_model
from django.db.models import Avg, Max
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdmin
from courses.access import daraja_ochiqmi, mavzu_ochiqmi, mavzu_testdan_otilganmi
from courses.models import Daraja, DarsProgress, OquvchiFan
from .models import (
    FinalTestNatija,
    GateTestNatija,
    MashqNatija,
    SpeakingNatija,
    WritingNatija,
)

User = get_user_model()


def _iso(value):
    return value.isoformat() if value else None


def _float(value):
    return round(float(value or 0), 2)


def _answer_payload(answer):
    selected = [item.matn for item in answer.tanlangan_javoblar.all()]
    if answer.savol.tur == 'text':
        correct = [answer.savol.togri_matn_javob] if answer.savol.togri_matn_javob else []
    else:
        correct = [item.matn for item in answer.savol.javoblar.all() if item.togri]
    return {
        'id': answer.id,
        'savol': answer.savol.matn,
        'savol_turi': answer.savol.tur,
        'tanlangan_javoblar': selected,
        'matn_javob': answer.matn_javob,
        'togri_javoblar': correct,
        'togri': answer.togri_berilgan,
    }


class AdminOquvchiProgressView(APIView):
    """Admin uchun bitta o'quvchining mavzu, dars va urinishlar kesimidagi to'liq progressi."""

    permission_classes = [IsAdmin]

    def get(self, request, oquvchi_id):
        try:
            oquvchi = User.objects.select_related('filial').get(
                id=oquvchi_id,
                role=User.ROLE_OQUVCHI,
            )
        except User.DoesNotExist:
            return Response({'detail': "O'quvchi topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        assignments = list(
            OquvchiFan.objects.filter(oquvchi=oquvchi)
            .select_related('daraja__fan')
            .order_by('daraja__fan__tartib', 'created_at', 'id')
        )

        attempts = list(
            MashqNatija.objects.filter(oquvchi=oquvchi)
            .select_related('mashq__dars__mavzu__daraja__fan')
            .prefetch_related(
                'berilgan_javoblar__tanlangan_javoblar',
                'berilgan_javoblar__savol__javoblar',
            )
            .order_by('-boshlangan_vaqt', '-id')
        )
        attempts_by_mashq = defaultdict(list)
        for item in attempts:
            attempts_by_mashq[item.mashq_id].append(item)

        progress_by_dars = {
            item.dars_id: item
            for item in DarsProgress.objects.filter(oquvchi=oquvchi)
        }
        writing_by_dars = defaultdict(list)
        for item in WritingNatija.objects.filter(oquvchi=oquvchi).select_related('topshiriq__dars').order_by('-created_at'):
            writing_by_dars[item.topshiriq.dars_id].append(item)
        speaking_by_dars = defaultdict(list)
        for item in SpeakingNatija.objects.filter(oquvchi=oquvchi).select_related('topshiriq__dars').order_by('-created_at'):
            speaking_by_dars[item.topshiriq.dars_id].append(item)

        gate_by_daraja = defaultdict(list)
        for item in GateTestNatija.objects.filter(oquvchi=oquvchi).select_related('gate_test__daraja').order_by('-created_at'):
            gate_by_daraja[item.gate_test.daraja_id].append(item)
        final_by_daraja = defaultdict(list)
        for item in FinalTestNatija.objects.filter(oquvchi=oquvchi).select_related('final_test__daraja').order_by('-created_at'):
            final_by_daraja[item.final_test.daraja_id].append(item)

        fanlar = []
        total_topics = 0
        completed_topics = 0
        current_global = None
        global_topic_no = 0

        for assignment in assignments:
            fan = assignment.daraja.fan
            darajalar = list(
                Daraja.objects.filter(fan=fan, tartib__gte=assignment.daraja.tartib)
                .prefetch_related(
                    'mavzular__darslar__mashq',
                    'mavzular__darslar__writing_topshiriqlar',
                    'mavzular__darslar__speaking_topshiriqlar',
                )
                .order_by('tartib', 'id')
            )

            fan_payload = {
                'fan_id': fan.id,
                'fan_nomi': fan.nomi,
                'boshlangich_daraja': assignment.daraja.nomi,
                'darajalar': [],
                'joriy': None,
                'jami_mavzu': 0,
                'tugatilgan_mavzu': 0,
            }

            fan_topic_no = 0
            for daraja in darajalar:
                level_open = daraja_ochiqmi(oquvchi, daraja)
                level_topics = list(daraja.mavzular.all())
                level_payload = {
                    'id': daraja.id,
                    'nomi': daraja.nomi,
                    'tartib': daraja.tartib,
                    'ochiq': level_open,
                    'mavzular': [],
                    'gate_test_natijalari': [
                        {
                            'id': result.id,
                            'foiz': _float(result.foiz),
                            'togri_soni': result.togri_soni,
                            'jami_soni': result.jami_soni,
                            'otdi': result.otdi,
                            'urinish_raqami': result.urinish_raqami,
                            'sana': _iso(result.created_at),
                        }
                        for result in gate_by_daraja.get(daraja.id, [])
                    ],
                    'final_test_natijalari': [
                        {
                            'id': result.id,
                            'foiz': _float(result.foiz),
                            'togri_soni': result.togri_soni,
                            'jami_soni': result.jami_soni,
                            'otdi': result.otdi,
                            'urinish_raqami': result.urinish_raqami,
                            'sana': _iso(result.created_at),
                        }
                        for result in final_by_daraja.get(daraja.id, [])
                    ],
                }

                for topic_index, mavzu in enumerate(level_topics, start=1):
                    fan_topic_no += 1
                    global_topic_no += 1
                    total_topics += 1
                    fan_payload['jami_mavzu'] += 1
                    topic_open = mavzu_ochiqmi(oquvchi, mavzu)
                    topic_passed = mavzu_testdan_otilganmi(oquvchi, mavzu)
                    if topic_passed:
                        completed_topics += 1
                        fan_payload['tugatilgan_mavzu'] += 1

                    lessons = []
                    topic_best = 0.0
                    topic_attempts = 0
                    for dars in mavzu.darslar.all():
                        progress = progress_by_dars.get(dars.id)
                        mashq_payload = None
                        if hasattr(dars, 'mashq'):
                            mashq = dars.mashq
                            mashq_attempts = attempts_by_mashq.get(mashq.id, [])
                            topic_attempts += len(mashq_attempts)
                            best_score = max((_float(item.foiz) for item in mashq_attempts), default=0.0)
                            topic_best = max(topic_best, best_score)
                            mashq_payload = {
                                'id': mashq.id,
                                'sarlavha': mashq.sarlavha,
                                'otish_foizi': int(mashq.otish_bali_foiz or 80),
                                'eng_yaxshi_foiz': best_score,
                                'otilgan': best_score >= int(mashq.otish_bali_foiz or 80),
                                'urinishlar': [
                                    {
                                        'id': result.id,
                                        'urinish_raqami': result.urinish_raqami,
                                        'togri_soni': result.togri_soni,
                                        'jami_soni': result.jami_soni,
                                        'foiz': _float(result.foiz),
                                        'boshlangan_vaqt': _iso(result.boshlangan_vaqt),
                                        'tugagan_vaqt': _iso(result.tugagan_vaqt),
                                        'javoblar': [
                                            _answer_payload(answer)
                                            for answer in result.berilgan_javoblar.all()
                                        ],
                                    }
                                    for result in mashq_attempts
                                ],
                            }

                        lessons.append({
                            'id': dars.id,
                            'sarlavha': dars.sarlavha,
                            'tartib': dars.tartib,
                            'video_tugatilgan': bool(progress and progress.video_tugatilgan),
                            'video_pozitsiya_soniya': progress.video_pozitsiya_soniya if progress else 0,
                            'oxirgi_korilgan': _iso(progress.updated_at) if progress else None,
                            'mashq': mashq_payload,
                            'writing_natijalari': [
                                {
                                    'id': result.id,
                                    'topshiriq': result.topshiriq.matn,
                                    'javob': result.matn_javob,
                                    'foiz': _float(result.ai_foiz) if result.ai_foiz is not None else None,
                                    'izoh': result.ai_izoh,
                                    'xatolar': result.ai_xatolar,
                                    'baholanmoqda': result.baholanmoqda,
                                    'sana': _iso(result.created_at),
                                }
                                for result in writing_by_dars.get(dars.id, [])
                            ],
                            'speaking_natijalari': [
                                {
                                    'id': result.id,
                                    'topshiriq': result.topshiriq.matn,
                                    'foiz': _float(result.ai_foiz) if result.ai_foiz is not None else None,
                                    'izoh': result.ai_izoh,
                                    'baholanmoqda': result.baholanmoqda,
                                    'audio_url': request.build_absolute_uri(result.audio_yozuv.url) if result.audio_yozuv else None,
                                    'sana': _iso(result.created_at),
                                }
                                for result in speaking_by_dars.get(dars.id, [])
                            ],
                        })

                    is_current = bool(level_open and topic_open and not topic_passed and fan_payload['joriy'] is None)
                    topic_payload = {
                        'id': mavzu.id,
                        'nomi': mavzu.nomi,
                        'tartib': mavzu.tartib,
                        'raqam': topic_index,
                        'fan_boyicha_raqam': fan_topic_no,
                        'umumiy_raqam': global_topic_no,
                        'ochiq': topic_open,
                        'otilgan': topic_passed,
                        'joriy': is_current,
                        'eng_yaxshi_foiz': topic_best,
                        'jami_urinishlar': topic_attempts,
                        'darslar': lessons,
                    }
                    level_payload['mavzular'].append(topic_payload)

                    if is_current:
                        fan_payload['joriy'] = {
                            'daraja_id': daraja.id,
                            'daraja_nomi': daraja.nomi,
                            'mavzu_id': mavzu.id,
                            'mavzu_nomi': mavzu.nomi,
                            'mavzu_raqami': topic_index,
                            'fan_boyicha_raqam': fan_topic_no,
                            'umumiy_raqam': global_topic_no,
                        }
                        if current_global is None:
                            current_global = {**fan_payload['joriy'], 'fan_nomi': fan.nomi}

                level_payload['tugatilgan'] = bool(level_topics) and all(item['otilgan'] for item in level_payload['mavzular'])
                final_passed = any(
                    result.otdi and float(result.foiz or 0) >= 80
                    for result in final_by_daraja.get(daraja.id, [])
                )
                level_payload['final_test_otilgan'] = final_passed

                # Mavzular tugagan, ammo yakuniy test hali o'tilmagan bo'lsa,
                # admin "joriy bosqich" sifatida aynan yakuniy testni ko'radi.
                if level_open and level_payload['tugatilgan'] and not final_passed and fan_payload['joriy'] is None:
                    fan_payload['joriy'] = {
                        'daraja_id': daraja.id,
                        'daraja_nomi': daraja.nomi,
                        'mavzu_id': None,
                        'mavzu_nomi': 'Yakuniy test kutilmoqda',
                        'mavzu_raqami': len(level_topics),
                        'fan_boyicha_raqam': fan_topic_no,
                        'umumiy_raqam': global_topic_no,
                        'yakuniy_test': True,
                    }
                    if current_global is None:
                        current_global = {**fan_payload['joriy'], 'fan_nomi': fan.nomi}

                fan_payload['darajalar'].append(level_payload)

            if fan_payload['joriy'] is None and fan_payload['jami_mavzu']:
                fan_payload['joriy'] = {
                    'daraja_nomi': fan_payload['darajalar'][-1]['nomi'],
                    'mavzu_nomi': 'Kurs to‘liq tugatilgan',
                    'mavzu_raqami': len(fan_payload['darajalar'][-1]['mavzular']),
                    'fan_boyicha_raqam': fan_payload['jami_mavzu'],
                    'umumiy_raqam': global_topic_no,
                    'tugallangan': True,
                }
                if current_global is None:
                    current_global = {**fan_payload['joriy'], 'fan_nomi': fan.nomi}

            fanlar.append(fan_payload)

        latest_activity = max(
            [item.boshlangan_vaqt for item in attempts]
            + [item.updated_at for item in progress_by_dars.values()]
            + [item.created_at for values in writing_by_dars.values() for item in values]
            + [item.created_at for values in speaking_by_dars.values() for item in values],
            default=None,
        )
        avg_score = MashqNatija.objects.filter(oquvchi=oquvchi).aggregate(value=Avg('foiz'))['value'] or 0
        best_score = MashqNatija.objects.filter(oquvchi=oquvchi).aggregate(value=Max('foiz'))['value'] or 0

        return Response({
            'oquvchi': {
                'id': oquvchi.id,
                'ism': oquvchi.ism,
                'familya': oquvchi.familya,
                'full_name': oquvchi.full_name,
                'username': oquvchi.username,
                'filial': oquvchi.filial.nomi if oquvchi.filial else '',
                'faol': oquvchi.faol,
                'created_at': _iso(oquvchi.created_at),
            },
            'xulosa': {
                'jami_mavzu': total_topics,
                'tugatilgan_mavzu': completed_topics,
                'progress_foiz': round((completed_topics / total_topics) * 100, 2) if total_topics else 0,
                'jami_urinishlar': len(attempts),
                'ortacha_foiz': _float(avg_score),
                'eng_yaxshi_foiz': _float(best_score),
                'oxirgi_faollik': _iso(latest_activity),
                'joriy': current_global,
            },
            'fanlar': fanlar,
            'generated_at': _iso(timezone.now()),
        })
