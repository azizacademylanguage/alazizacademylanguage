import { useEffect, useMemo, useState } from 'react';
import { Clock3, Coins, RotateCcw, Trophy, Zap } from 'lucide-react';
import { Button, Card, ProgressBar, Skeleton } from '../../components/ui';
import { finishTezkorOyin, startTezkorOyin } from '../../api/features';

export default function TezkorOyiniPage() {
  const [game, setGame] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [seconds, setSeconds] = useState(90);
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const load = async () => {
    setLoading(true); setError(''); setIndex(0); setAnswers({}); setResult(null);
    try { const data = await startTezkorOyin(); setGame(data); setSeconds(data.vaqt_soniya || 90); }
    catch (e) { setGame(null); setError(e.response?.data?.detail || 'O‘yin yuklanmadi.'); }
    finally { setLoading(false); }
  };
  useEffect(() => { load(); }, []);

  const submit = async () => {
    if (!game || submitting || result) return;
    setSubmitting(true);
    try {
      const payload = game.savollar.map(q => ({ savol: q.id, javob: answers[q.id] || '' }));
      const data = await finishTezkorOyin(game.token, payload);
      setResult(data);
      window.dispatchEvent(new CustomEvent('coin-updated', { detail: data.balans }));
    } catch (e) { setError(e.response?.data?.detail || 'Natija saqlanmadi.'); }
    finally { setSubmitting(false); }
  };

  useEffect(() => {
    if (!game || result) return undefined;
    if (seconds <= 0) { submit(); return undefined; }
    const timer = window.setInterval(() => setSeconds(v => Math.max(0, v - 1)), 1000);
    return () => window.clearInterval(timer);
  }, [game, result, seconds]);

  const progress = useMemo(() => game ? ((index + 1) / game.savollar.length) * 100 : 0, [game, index]);
  if (loading) return <div className="space-y-4"><Skeleton className="h-28" /><Skeleton className="h-72" /></div>;
  if (!game) return <Card className="p-10 text-center"><Zap className="mx-auto mb-3" /><p className="font-bold">{error || 'O‘yin mavjud emas'}</p><Button variant="secondary" className="mt-4" onClick={load}><RotateCcw size={16} /> Qayta urinish</Button></Card>;
  if (result) return <div className="animate-in max-w-lg mx-auto py-10 text-center"><div className="w-20 h-20 rounded-full mx-auto flex items-center justify-center" style={{ background: '#FFF1D8' }}><Trophy size={38} /></div><h1 className="font-display text-4xl font-extrabold mt-5">{result.foiz}%</h1><p className="text-sm mt-2" style={{ color: '#8A8371' }}>{result.togri_soni}/{result.jami_soni} ta to‘g‘ri javob</p><Card className="p-5 mt-5"><div className="flex items-center justify-center gap-2 text-xl font-bold"><Coins size={22} /> +{result.berilgan_coin} coin</div><p className="text-sm mt-2" style={{ color: '#8A8371' }}>Yangi balans: {result.balans} coin</p></Card><Button className="mt-5" onClick={load}><RotateCcw size={16} /> Yana o‘ynash</Button></div>;

  const question = game.savollar[index];
  return <div className="animate-in max-w-2xl space-y-5">
    <section className="rounded-3xl p-6 text-white" style={{ background: 'linear-gradient(135deg, var(--color-forest), var(--color-teal))' }}><div className="flex flex-col sm:flex-row justify-between gap-4"><div><div className="flex items-center gap-2 text-xs font-bold tracking-widest"><Zap size={15} /> TEZKOR TARJIMA</div><h1 className="font-display text-3xl font-extrabold mt-2">90 soniyada 10 savol</h1><p className="text-sm mt-2 text-white/75">To‘g‘ri tarjimani tez tanlang. 10/10 natija uchun bonus coin beriladi.</p></div><div className="rounded-2xl px-4 py-3 bg-white/15 h-fit"><p className="text-xs text-white/70">Bugun qolgan</p><p className="font-display text-2xl font-bold">{game.qolgan_oyin} o‘yin</p></div></div></section>
    <div className="flex items-center justify-between"><span className="text-sm font-semibold">{index + 1}/{game.savollar.length}</span><span className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl font-bold" style={{ background: seconds < 20 ? '#FBEAE8' : '#FFF1D8' }}><Clock3 size={16} /> {seconds}s</span></div><ProgressBar value={progress} tone="amber" />
    <Card className="p-6"><p className="text-xs uppercase tracking-wider" style={{ color: '#8A8371' }}>{question.yonalish === 'chet_uz' ? 'O‘zbekcha tarjimasini toping' : 'Chet tilidagi tarjimasini toping'}</p><h2 className="font-display text-3xl font-extrabold mt-3 mb-6">{question.savol}</h2><div className="grid sm:grid-cols-2 gap-3">{question.variantlar.map(option => { const selected = answers[question.id] === option; return <button key={option} type="button" onClick={() => setAnswers({ ...answers, [question.id]: option })} className="p-4 rounded-xl border text-left font-semibold press" style={{ borderColor: selected ? 'var(--color-forest)' : 'var(--color-line)', background: selected ? 'var(--color-paper-warm)' : 'white' }}>{option}</button>; })}</div></Card>
    {error && <p className="text-sm font-semibold" style={{ color: 'var(--color-red)' }}>{error}</p>}
    <div className="flex justify-between"><Button variant="secondary" onClick={() => setIndex(v => Math.max(0, v - 1))} disabled={!index}>Oldingi</Button>{index < game.savollar.length - 1 ? <Button onClick={() => setIndex(v => v + 1)} disabled={!answers[question.id]}>Keyingi</Button> : <Button variant="amber" onClick={submit} loading={submitting}>Yakunlash</Button>}</div>
  </div>;
}
