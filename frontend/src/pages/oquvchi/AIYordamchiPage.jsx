import { useEffect, useMemo, useRef, useState } from 'react';
import { Bot, Send, Sparkles, Trash2, UserRound, TrendingUp, Target, BookOpenCheck } from 'lucide-react';
import { Card, Button, Skeleton, Badge } from '../../components/ui';
import { clearAIYordamchi, getAIYordamchi, sendAIYordamchi } from '../../api/platform';
import { useToast } from '../../context/ToastContext';

export default function AIYordamchiPage() {
  const { showToast } = useToast();
  const [data, setData] = useState(null);
  const [savol, setSavol] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);

  const load = () => {
    setLoading(true);
    getAIYordamchi()
      .then(setData)
      .catch((e) => showToast(e.response?.data?.detail || 'AI yordamchi yuklanmadi.', 'danger'))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [data?.xabarlar?.length]);

  const remaining = useMemo(() => {
    const used = (data?.xabarlar || []).filter(x => x.role === 'user' && new Date(x.created_at).toDateString() === new Date().toDateString()).length;
    return Math.max(0, (data?.kunlik_limit || 0) - used);
  }, [data]);

  const submit = async (text = savol) => {
    const clean = text.trim();
    if (!clean || sending) return;
    setSending(true);
    setSavol('');
    const temp = { id: `tmp-${Date.now()}`, role: 'user', matn: clean, created_at: new Date().toISOString() };
    setData(prev => ({ ...prev, xabarlar: [...(prev?.xabarlar || []), temp] }));
    try {
      const res = await sendAIYordamchi(clean);
      setData(prev => ({ ...prev, xabarlar: [...(prev?.xabarlar || []).filter(x => x.id !== temp.id), temp, res.xabar] }));
    } catch (e) {
      setData(prev => ({ ...prev, xabarlar: (prev?.xabarlar || []).filter(x => x.id !== temp.id) }));
      showToast(e.response?.data?.detail || 'AI javob bera olmadi.', 'danger');
    } finally {
      setSending(false);
    }
  };

  const clear = async () => {
    if (!window.confirm('AI suhbat tarixini tozalaysizmi?')) return;
    await clearAIYordamchi();
    setData(prev => ({ ...prev, xabarlar: [] }));
    showToast('Suhbat tarixi tozalandi.');
  };

  if (loading) {
    return <div className="space-y-4"><Skeleton className="h-28 w-full" /><Skeleton className="h-[520px] w-full" /></div>;
  }

  const context = data?.kontekst || {};
  return (
    <div className="animate-in space-y-5">
      <div className="dashboard-welcome">
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-2">
            <Badge tone={data?.faol ? 'success' : 'danger'}>{data?.faol ? 'AI faol' : 'AI o‘chirilgan'}</Badge>
            <span className="text-xs" style={{ color: '#8A8371' }}>Bugun yana {remaining} ta savol</span>
          </div>
          <h1 className="font-display text-2xl font-extrabold" style={{ color: 'var(--color-ink)' }}>Shaxsiy AI yordamchi</h1>
          <p className="text-sm mt-1 max-w-2xl" style={{ color: '#8A8371' }}>
            Natijalaringiz, xatolaringiz va o‘qiyotgan darajangiz asosida tushuntirish hamda shaxsiy reja beradi.
          </p>
        </div>
        <div className="welcome-orb"><Sparkles size={24} /></div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <Card className="p-4 flex items-center gap-3"><TrendingUp size={20} style={{ color: 'var(--color-teal)' }} /><div><p className="text-xs" style={{ color: '#8A8371' }}>O‘rtacha natija</p><p className="font-display font-extrabold text-xl">{Number(context.ortacha_foiz || 0).toFixed(1)}%</p></div></Card>
        <Card className="p-4 flex items-center gap-3"><BookOpenCheck size={20} style={{ color: 'var(--color-jungle)' }} /><div><p className="text-xs" style={{ color: '#8A8371' }}>Yo‘nalish</p><p className="font-display font-bold text-sm">{context.fan || '—'} · {context.daraja || '—'}</p></div></Card>
        <Card className="p-4 flex items-center gap-3"><Target size={20} style={{ color: 'var(--color-amethyst)' }} /><div><p className="text-xs" style={{ color: '#8A8371' }}>Jami urinish</p><p className="font-display font-extrabold text-xl">{context.jami_urinishlar || 0}</p></div></Card>
      </div>

      <Card className="overflow-hidden">
        <div className="flex items-center justify-between gap-3 p-4 border-b" style={{ borderColor: 'var(--color-line)' }}>
          <div className="flex items-center gap-2"><Bot size={20} style={{ color: 'var(--color-teal)' }} /><span className="font-display font-bold">AI bilan suhbat</span></div>
          {(data?.xabarlar || []).length > 0 && <Button variant="ghost" size="sm" onClick={clear}><Trash2 size={15} /> Tozalash</Button>}
        </div>

        <div className="ai-chat-scroll p-4 sm:p-5 space-y-4">
          {(data?.xabarlar || []).length === 0 ? (
            <div className="py-10 text-center">
              <div className="w-16 h-16 mx-auto rounded-2xl grid place-items-center mb-4" style={{ background: 'rgba(8,99,117,.08)', color: 'var(--color-teal)' }}><Bot size={30} /></div>
              <p className="font-display font-bold mb-1">Savolingizni yozing</p>
              <p className="text-sm" style={{ color: '#8A8371' }}>AI sizning shaxsiy natijalaringizni hisobga oladi.</p>
            </div>
          ) : (
            data.xabarlar.map((x) => (
              <div key={x.id} className={`flex gap-2.5 ${x.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {x.role !== 'user' && <div className="ai-avatar ai-avatar--bot"><Bot size={16} /></div>}
                <div className={`ai-bubble ${x.role === 'user' ? 'ai-bubble--user' : 'ai-bubble--bot'}`}>
                  <p className="whitespace-pre-wrap leading-6">{x.matn}</p>
                  <span>{new Date(x.created_at).toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
                {x.role === 'user' && <div className="ai-avatar ai-avatar--user"><UserRound size={16} /></div>}
              </div>
            ))
          )}
          {sending && <div className="flex gap-2.5"><div className="ai-avatar ai-avatar--bot"><Bot size={16} /></div><div className="ai-bubble ai-bubble--bot"><div className="typing-dots"><i /><i /><i /></div></div></div>}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 border-t" style={{ borderColor: 'var(--color-line)', background: '#FAFCFB' }}>
          <div className="flex flex-wrap gap-2 mb-3">
            {(data?.tezkor_savollar || []).map(q => <button key={q} onClick={() => submit(q)} className="quick-question">{q}</button>)}
          </div>
          <div className="flex gap-2">
            <textarea
              value={savol}
              onChange={e => setSavol(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit(); } }}
              disabled={!data?.faol || sending}
              className="flex-1 min-h-[48px] max-h-32 px-4 py-3 rounded-xl border outline-none resize-none text-sm"
              style={{ borderColor: 'var(--color-line)' }}
              placeholder="Mavzu, xato yoki o‘quv reja haqida so‘rang..."
            />
            <Button onClick={() => submit()} disabled={!savol.trim() || !data?.faol} loading={sending} className="self-end h-12"><Send size={17} /><span className="hidden sm:inline">Yuborish</span></Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
