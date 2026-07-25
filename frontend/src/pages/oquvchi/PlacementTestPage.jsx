import { useEffect, useState } from 'react';
import { BrainCircuit, ChevronLeft, ChevronRight, Clock3, ShieldAlert, Sparkles } from 'lucide-react';
import { Button, Card, ProgressBar, Skeleton } from '../../components/ui';
import { getPlacementTest, submitPlacementTest } from '../../api/features';
import useTestSecurity from '../../hooks/useTestSecurity';

export default function PlacementTestPage() {
  const [test, setTest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [answers, setAnswers] = useState({});
  const [index, setIndex] = useState(0);
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const security = useTestSecurity(test?.vaqt_chegarasi_daq || 25);

  useEffect(() => {
    getPlacementTest().then(setTest).catch(e => setError(e.response?.data?.detail || 'Placement test yuklanmadi.')).finally(() => setLoading(false));
  }, []);

  const submit = async () => {
    setSubmitting(true);
    try {
      const payload = test.savollar.map(q => ({ savol: q.id, tanlangan_javoblar: answers[q.id] ? [answers[q.id]] : [] }));
      setResult(await submitPlacementTest(test.fan.id, payload, security.getSecurityData()));
    } catch (e) { setError(e.response?.data?.detail || 'Test yuborilmadi.'); }
    finally { setSubmitting(false); }
  };

  useEffect(() => { if (security.timeExpired && test && !result && !submitting) submit(); }, [security.timeExpired]);

  if (loading) return <div className="space-y-4 max-w-2xl"><Skeleton className="h-20" /><Skeleton className="h-56" /></div>;
  if (error && !test) return <Card className="p-10 text-center"><BrainCircuit className="mx-auto mb-3" /><p className="font-bold">{error}</p><p className="text-sm mt-2" style={{ color: '#8A8371' }}>Admin Gate Test savollarini kiritgandan keyin ishlaydi.</p></Card>;
  if (result) return <div className="animate-in max-w-lg mx-auto py-10 text-center"><div className="w-20 h-20 rounded-full mx-auto flex items-center justify-center" style={{ background: '#E4EFE6' }}><Sparkles size={36} /></div><h1 className="font-display text-4xl font-extrabold mt-5">{result.foiz}%</h1><p className="mt-2 text-sm" style={{ color: '#8A8371' }}>{result.togri_soni}/{result.jami_soni} ta to‘g‘ri javob</p><Card className="p-5 mt-6"><p className="text-xs uppercase tracking-wider" style={{ color: '#8A8371' }}>Tavsiya etilgan daraja</p><p className="font-display text-2xl font-extrabold mt-2">{result.tavsiya_daraja?.nomi || '—'}</p><p className="text-sm mt-2" style={{ color: '#6F695C' }}>{result.xabar}</p></Card><Button className="mt-5" onClick={() => window.location.assign('/oquvchi/fanlarim')}>Darajalarimga qaytish</Button></div>;

  const question = test.savollar[index];
  return <div className="animate-in max-w-2xl space-y-5">
    <div className="flex flex-col sm:flex-row justify-between gap-3"><div><div className="flex items-center gap-2"><BrainCircuit size={19} /><h1 className="font-display text-2xl font-extrabold">Darajani aniqlash testi</h1></div><p className="text-sm mt-1" style={{ color: '#8A8371' }}>{test.fan.nomi} bo‘yicha bilim darajangiz aniqlanadi.</p></div><div className="flex gap-2"><span className="inline-flex items-center gap-1 px-3 py-2 rounded-xl text-sm font-semibold" style={{ background: '#FFF1D8' }}><Clock3 size={16} /> {security.formattedTime}</span><span className="inline-flex items-center gap-1 px-3 py-2 rounded-xl text-sm" style={{ background: security.focusLosses ? '#FBEAE8' : '#F1F5F3' }}><ShieldAlert size={16} /> {security.focusLosses}</span></div></div>
    <div><div className="flex justify-between text-xs mb-2" style={{ color: '#8A8371' }}><span>{index + 1}/{test.savollar.length}</span><span>{Object.keys(answers).length} ta javob</span></div><ProgressBar value={(index + 1) / test.savollar.length * 100} tone="amber" /></div>
    <Card className="p-6"><p className="font-semibold text-base mb-5">{question.matn}</p><div className="space-y-2">{question.javoblar.map(answer => { const selected = answers[question.id] === answer.id; return <button key={answer.id} type="button" onClick={() => setAnswers({ ...answers, [question.id]: answer.id })} className="w-full p-3.5 rounded-xl border text-left text-sm press" style={{ borderColor: selected ? 'var(--color-forest)' : 'var(--color-line)', background: selected ? 'var(--color-paper-warm)' : 'white' }}>{answer.matn}</button>; })}</div></Card>
    {error && <p className="text-sm font-semibold" style={{ color: 'var(--color-red)' }}>{error}</p>}
    <div className="flex justify-between gap-3"><Button variant="secondary" onClick={() => setIndex(v => Math.max(0, v - 1))} disabled={!index}><ChevronLeft size={16} /> Oldingi</Button>{index < test.savollar.length - 1 ? <Button onClick={() => setIndex(v => v + 1)}>Keyingi <ChevronRight size={16} /></Button> : <Button variant="amber" onClick={submit} loading={submitting}>Testni yakunlash</Button>}</div>
  </div>;
}
