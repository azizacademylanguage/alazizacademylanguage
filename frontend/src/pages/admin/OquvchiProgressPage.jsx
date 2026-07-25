import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { getAdminOquvchiProgress } from '../../api/admin';
import { Badge, Card, EmptyState, ProgressBar, Skeleton } from '../../components/ui';
import {
  ArrowLeft,
  BarChart3,
  BookOpen,
  CheckCircle2,
  ChevronDown,
  CircleX,
  FileText,
  Headphones,
  ListChecks,
  LockKeyhole,
  PlayCircle,
  Target,
  UserRound,
} from 'lucide-react';
import { cleanLevelName } from '../../utils/course';

const formatDate = (value) => value
  ? new Date(value).toLocaleString('uz-UZ', { dateStyle: 'medium', timeStyle: 'short' })
  : '—';

const scoreTone = (score, passed = false) => {
  if (passed || Number(score) >= 80) return 'success';
  if (Number(score) >= 50) return 'warning';
  return 'danger';
};

function SummaryCard({ icon: Icon, label, value, sub }) {
  return (
    <Card className="p-4 sm:p-5">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'var(--color-paper-warm)', color: 'var(--color-forest)' }}>
          <Icon size={19} />
        </div>
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: '#9C9584' }}>{label}</p>
          <p className="font-display text-xl font-extrabold truncate" style={{ color: 'var(--color-ink)' }}>{value}</p>
          {sub && <p className="text-xs mt-0.5" style={{ color: '#8A8371' }}>{sub}</p>}
        </div>
      </div>
    </Card>
  );
}

function Answers({ answers = [] }) {
  if (!answers.length) {
    return <p className="text-xs" style={{ color: '#8A8371' }}>Bu urinish uchun savol-javob tafsiloti saqlanmagan.</p>;
  }
  return (
    <div className="space-y-2 mt-3">
      {answers.map((answer, index) => {
        const selected = answer.matn_javob || answer.tanlangan_javoblar?.join(', ') || 'Javob berilmagan';
        const correct = answer.togri_javoblar?.join(', ') || 'Ko‘rsatilmagan';
        return (
          <div key={answer.id || index} className="rounded-xl border p-3" style={{ borderColor: answer.togri ? '#BFD8C4' : '#E6C0BC', background: answer.togri ? '#F5FAF6' : '#FFF8F7' }}>
            <div className="flex items-start gap-2">
              {answer.togri ? <CheckCircle2 size={16} className="mt-0.5 shrink-0" style={{ color: '#2F6E42' }} /> : <CircleX size={16} className="mt-0.5 shrink-0" style={{ color: 'var(--color-red)' }} />}
              <div className="min-w-0 text-sm">
                <p className="font-semibold" style={{ color: 'var(--color-ink)' }}>{index + 1}. {answer.savol}</p>
                <p className="mt-1"><span className="font-medium">O‘quvchi javobi:</span> {selected}</p>
                {!answer.togri && <p className="mt-1" style={{ color: '#2F6E42' }}><span className="font-medium">To‘g‘ri javob:</span> {correct}</p>}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function Attempts({ mashq }) {
  if (!mashq) return <p className="text-xs mt-3" style={{ color: '#8A8371' }}>Bu darsda test mavjud emas.</p>;
  if (!mashq.urinishlar?.length) {
    return <p className="text-xs mt-3" style={{ color: '#8A8371' }}>O‘quvchi testni hali topshirmagan.</p>;
  }
  return (
    <div className="mt-4 space-y-2">
      <div className="flex flex-wrap items-center gap-2">
        <Badge tone={scoreTone(mashq.eng_yaxshi_foiz, mashq.otilgan)}>Eng yaxshi: {mashq.eng_yaxshi_foiz}%</Badge>
        <Badge tone="neutral">O‘tish bali: {mashq.otish_foizi}%</Badge>
        <Badge tone="forest">{mashq.urinishlar.length} ta urinish</Badge>
      </div>
      {mashq.urinishlar.map((attempt) => (
        <details key={attempt.id} className="rounded-xl border bg-white group" style={{ borderColor: 'var(--color-line)' }}>
          <summary className="list-none cursor-pointer px-3.5 py-3 flex items-center justify-between gap-3">
            <div className="flex flex-wrap items-center gap-2 min-w-0">
              <Badge tone={scoreTone(attempt.foiz, attempt.foiz >= mashq.otish_foizi)}>#{attempt.urinish_raqami} urinish</Badge>
              <span className="font-semibold text-sm" style={{ color: 'var(--color-ink)' }}>{attempt.togri_soni}/{attempt.jami_soni} · {attempt.foiz}%</span>
              <span className="text-xs" style={{ color: '#8A8371' }}>{formatDate(attempt.boshlangan_vaqt)}</span>
            </div>
            <ChevronDown size={17} className="shrink-0 transition-transform group-open:rotate-180" style={{ color: '#8A8371' }} />
          </summary>
          <div className="px-3.5 pb-3.5 border-t" style={{ borderColor: 'var(--color-line)' }}>
            <Answers answers={attempt.javoblar} />
          </div>
        </details>
      ))}
    </div>
  );
}

function ExtraResults({ dars }) {
  const hasWriting = dars.writing_natijalari?.length > 0;
  const hasSpeaking = dars.speaking_natijalari?.length > 0;
  if (!hasWriting && !hasSpeaking) return null;
  return (
    <div className="mt-4 grid grid-cols-1 xl:grid-cols-2 gap-3">
      {hasWriting && (
        <div className="rounded-xl border p-3.5" style={{ borderColor: 'var(--color-line)', background: '#FCFBF7' }}>
          <p className="font-semibold text-sm flex items-center gap-2 mb-3"><FileText size={16} /> Writing natijalari</p>
          <div className="space-y-3">
            {dars.writing_natijalari.map((result) => (
              <div key={result.id} className="text-sm border-t first:border-0 first:pt-0 pt-3" style={{ borderColor: 'var(--color-line)' }}>
                <div className="flex justify-between gap-2"><Badge tone={scoreTone(result.foiz)}>{result.foiz == null ? 'Baholanmoqda' : `${result.foiz}%`}</Badge><span className="text-xs" style={{ color: '#8A8371' }}>{formatDate(result.sana)}</span></div>
                <p className="font-medium mt-2">Topshiriq: {result.topshiriq}</p>
                <p className="mt-1 whitespace-pre-wrap"><span className="font-medium">Javob:</span> {result.javob}</p>
                {result.izoh && <p className="mt-1" style={{ color: '#6B6455' }}><span className="font-medium">AI izoh:</span> {result.izoh}</p>}
                {result.xatolar?.length > 0 && <p className="mt-1" style={{ color: 'var(--color-red)' }}><span className="font-medium">Xatolar:</span> {result.xatolar.map((x) => typeof x === 'string' ? x : JSON.stringify(x)).join('; ')}</p>}
              </div>
            ))}
          </div>
        </div>
      )}
      {hasSpeaking && (
        <div className="rounded-xl border p-3.5" style={{ borderColor: 'var(--color-line)', background: '#FCFBF7' }}>
          <p className="font-semibold text-sm flex items-center gap-2 mb-3"><Headphones size={16} /> Speaking natijalari</p>
          <div className="space-y-3">
            {dars.speaking_natijalari.map((result) => (
              <div key={result.id} className="text-sm border-t first:border-0 first:pt-0 pt-3" style={{ borderColor: 'var(--color-line)' }}>
                <div className="flex justify-between gap-2"><Badge tone={scoreTone(result.foiz)}>{result.foiz == null ? 'Baholanmoqda' : `${result.foiz}%`}</Badge><span className="text-xs" style={{ color: '#8A8371' }}>{formatDate(result.sana)}</span></div>
                <p className="font-medium mt-2">Topshiriq: {result.topshiriq}</p>
                {result.izoh && <p className="mt-1" style={{ color: '#6B6455' }}>{result.izoh}</p>}
                {result.audio_url && <audio controls preload="none" className="w-full mt-2" src={result.audio_url} />}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function OquvchiProgressPage() {
  const { oquvchiId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    getAdminOquvchiProgress(oquvchiId)
      .then(setData)
      .catch((err) => setError(err.response?.data?.detail || "Progressni yuklashda xatolik yuz berdi."))
      .finally(() => setLoading(false));
  }, [oquvchiId]);

  if (loading) {
    return <div className="space-y-4"><Skeleton className="h-8 w-52" /><Skeleton className="h-28 w-full" /><Skeleton className="h-52 w-full" /></div>;
  }

  if (error) {
    return <Card><EmptyState icon={CircleX} title="Ma’lumot ochilmadi" description={error} action={<Link to="/admin/oquvchilar" className="text-sm font-semibold" style={{ color: 'var(--color-forest)' }}>O‘quvchilarga qaytish</Link>} /></Card>;
  }

  const current = data?.xulosa?.joriy;
  return (
    <div className="animate-in pb-8">
      <Link to="/admin/oquvchilar" className="inline-flex items-center gap-1.5 text-sm mb-4 hover:underline" style={{ color: 'var(--color-forest)' }}>
        <ArrowLeft size={16} /> O‘quvchilarga qaytish
      </Link>

      <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl flex items-center justify-center" style={{ background: 'var(--color-paper-warm)', color: 'var(--color-forest)' }}><UserRound size={23} /></div>
            <div>
              <h1 className="font-display text-2xl font-bold" style={{ color: 'var(--color-ink)' }}>{data.oquvchi.full_name}</h1>
              <p className="text-sm" style={{ color: '#8A8371' }}>Login: {data.oquvchi.username}{data.oquvchi.filial ? ` · ${data.oquvchi.filial}` : ''}</p>
            </div>
          </div>
        </div>
        <Badge tone={data.oquvchi.faol ? 'success' : 'danger'}>{data.oquvchi.faol ? 'Faol o‘quvchi' : 'Nofaol o‘quvchi'}</Badge>
      </div>

      <Card className="p-5 mb-5" style={{ background: 'linear-gradient(135deg, rgba(27,75,67,0.06), rgba(8,99,117,0.08))' }}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-wider font-semibold mb-1" style={{ color: '#8A8371' }}>Hozir qayerga kelgan</p>
            {current ? (
              <>
                <h2 className="font-display text-xl font-bold" style={{ color: 'var(--color-ink)' }}>
                  {current.fan_nomi} · {cleanLevelName(current.daraja_nomi)} · {current.yakuniy_test ? 'Yakuniy test' : current.tugallangan ? 'Kurs tugallangan' : `${current.mavzu_raqami}-mavzu`}
                </h2>
                <p className="text-sm mt-1" style={{ color: '#6B6455' }}>{current.mavzu_nomi}</p>
              </>
            ) : <p className="font-semibold">Fan yoki daraja biriktirilmagan.</p>}
          </div>
          <div className="min-w-[220px]">
            <div className="flex justify-between text-xs mb-2"><span>Umumiy progress</span><strong>{data.xulosa.progress_foiz}%</strong></div>
            <ProgressBar value={data.xulosa.progress_foiz} />
            <p className="text-xs mt-2 text-right" style={{ color: '#8A8371' }}>{data.xulosa.tugatilgan_mavzu}/{data.xulosa.jami_mavzu} mavzu tugatilgan</p>
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-2 xl:grid-cols-4 gap-3 mb-7">
        <SummaryCard icon={BookOpen} label="Mavzular" value={`${data.xulosa.tugatilgan_mavzu}/${data.xulosa.jami_mavzu}`} sub="tugatilgan" />
        <SummaryCard icon={ListChecks} label="Urinishlar" value={data.xulosa.jami_urinishlar} sub="barcha testlar" />
        <SummaryCard icon={BarChart3} label="O‘rtacha" value={`${data.xulosa.ortacha_foiz}%`} />
        <SummaryCard icon={Target} label="Eng yaxshi" value={`${data.xulosa.eng_yaxshi_foiz}%`} sub={`Oxirgi faollik: ${formatDate(data.xulosa.oxirgi_faollik)}`} />
      </div>

      {!data.fanlar?.length ? (
        <Card><EmptyState icon={BookOpen} title="Fan biriktirilmagan" description="Bu o‘quvchiga hali fan va boshlang‘ich daraja tanlanmagan." /></Card>
      ) : (
        <div className="space-y-6">
          {data.fanlar.map((fan) => (
            <section key={`${fan.fan_id}-${fan.boshlangich_daraja}`}>
              <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-2 mb-3">
                <div><h2 className="font-display text-xl font-bold" style={{ color: 'var(--color-ink)' }}>{fan.fan_nomi}</h2><p className="text-sm" style={{ color: '#8A8371' }}>Boshlang‘ich daraja: {cleanLevelName(fan.boshlangich_daraja)}</p></div>
                <Badge tone="forest">{fan.tugatilgan_mavzu}/{fan.jami_mavzu} mavzu</Badge>
              </div>

              <div className="space-y-3">
                {fan.darajalar.map((level) => (
                  <details key={level.id} open={level.mavzular.some((m) => m.joriy)} className="group rounded-2xl border bg-white overflow-hidden" style={{ borderColor: 'var(--color-line)', boxShadow: 'var(--shadow-sm)' }}>
                    <summary className="list-none cursor-pointer p-4 sm:p-5 flex items-center justify-between gap-3">
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0" style={{ background: level.ochiq ? '#E4EFE6' : 'var(--color-paper-warm)', color: level.ochiq ? '#2F6E42' : '#8A8371' }}>
                          {level.ochiq ? <BookOpen size={18} /> : <LockKeyhole size={18} />}
                        </div>
                        <div className="min-w-0"><p className="font-display font-bold truncate" style={{ color: 'var(--color-ink)' }}>{cleanLevelName(level.nomi)}</p><p className="text-xs" style={{ color: '#8A8371' }}>{level.mavzular.filter((m) => m.otilgan).length}/{level.mavzular.length} mavzu · {level.ochiq ? 'Ochiq' : 'Yopiq'}</p></div>
                      </div>
                      <ChevronDown size={18} className="transition-transform group-open:rotate-180" style={{ color: '#8A8371' }} />
                    </summary>

                    <div className="border-t p-3 sm:p-4 space-y-3" style={{ borderColor: 'var(--color-line)', background: '#FCFBF7' }}>
                      {level.mavzular.map((topic) => (
                        <details key={topic.id} open={topic.joriy} className="group/topic rounded-xl border bg-white overflow-hidden" style={{ borderColor: topic.joriy ? 'var(--color-forest-light)' : 'var(--color-line)' }}>
                          <summary className="list-none cursor-pointer p-3.5 sm:p-4 flex items-center justify-between gap-3">
                            <div className="flex items-center gap-3 min-w-0">
                              <div className="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold shrink-0" style={{ background: topic.otilgan ? '#E4EFE6' : topic.ochiq ? 'var(--color-amber-light)' : 'var(--color-paper-warm)', color: topic.otilgan ? '#2F6E42' : topic.ochiq ? '#8A5A1A' : '#8A8371' }}>{topic.raqam}</div>
                              <div className="min-w-0"><p className="font-semibold truncate" style={{ color: 'var(--color-ink)' }}>{topic.nomi}</p><div className="flex flex-wrap gap-1.5 mt-1">{topic.joriy && <Badge tone="warning">Hozirgi mavzu</Badge>}<Badge tone={topic.otilgan ? 'success' : topic.ochiq ? 'warning' : 'neutral'}>{topic.otilgan ? 'Tugatilgan' : topic.ochiq ? 'Jarayonda' : 'Yopiq'}</Badge>{topic.jami_urinishlar > 0 && <Badge tone="forest">{topic.eng_yaxshi_foiz}% · {topic.jami_urinishlar} urinish</Badge>}</div></div>
                            </div>
                            <ChevronDown size={17} className="transition-transform group-open/topic:rotate-180 shrink-0" style={{ color: '#8A8371' }} />
                          </summary>

                          <div className="border-t p-3 sm:p-4 space-y-3" style={{ borderColor: 'var(--color-line)' }}>
                            {topic.darslar.map((dars) => (
                              <Card key={dars.id} className="p-4" style={{ boxShadow: 'none' }}>
                                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                                  <div><p className="font-semibold flex items-center gap-2" style={{ color: 'var(--color-ink)' }}><PlayCircle size={16} /> {dars.sarlavha}</p><p className="text-xs mt-1" style={{ color: '#8A8371' }}>Oxirgi ko‘rilgan: {formatDate(dars.oxirgi_korilgan)}</p></div>
                                  <Badge tone={dars.video_tugatilgan ? 'success' : 'neutral'}>{dars.video_tugatilgan ? 'Dars ko‘rilgan' : 'Dars tugatilmagan'}</Badge>
                                </div>
                                <Attempts mashq={dars.mashq} />
                                <ExtraResults dars={dars} />
                              </Card>
                            ))}
                            {!topic.darslar.length && <p className="text-sm" style={{ color: '#8A8371' }}>Bu mavzuda dars mavjud emas.</p>}
                          </div>
                        </details>
                      ))}

                      {(level.gate_test_natijalari.length > 0 || level.final_test_natijalari.length > 0) && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                          <Card className="p-3.5" style={{ boxShadow: 'none' }}><p className="font-semibold text-sm mb-2">Daraja ochish testi</p>{level.gate_test_natijalari.length ? level.gate_test_natijalari.map((r) => <div key={r.id} className="flex justify-between text-sm py-1"><span>#{r.urinish_raqami} · {formatDate(r.sana)}</span><Badge tone={r.otdi ? 'success' : 'danger'}>{r.foiz}%</Badge></div>) : <p className="text-xs" style={{ color: '#8A8371' }}>Natija yo‘q</p>}</Card>
                          <Card className="p-3.5" style={{ boxShadow: 'none' }}><p className="font-semibold text-sm mb-2">Yakuniy test</p>{level.final_test_natijalari.length ? level.final_test_natijalari.map((r) => <div key={r.id} className="flex justify-between text-sm py-1"><span>#{r.urinish_raqami} · {formatDate(r.sana)}</span><Badge tone={r.otdi ? 'success' : 'danger'}>{r.foiz}%</Badge></div>) : <p className="text-xs" style={{ color: '#8A8371' }}>Natija yo‘q</p>}</Card>
                        </div>
                      )}
                    </div>
                  </details>
                ))}
              </div>
            </section>
          ))}
        </div>
      )}
    </div>
  );
}
