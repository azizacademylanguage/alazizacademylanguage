import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getMashq, topshirMashq } from '../../api/oquvchi';
import { Card, Button, ProgressBar, Skeleton } from '../../components/ui';
import { ChevronLeft, ChevronRight, CheckCircle2 } from 'lucide-react';

export default function MashqPage() {
  const { mashqId } = useParams();
  const navigate = useNavigate();
  const [mashq, setMashq] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [javoblar, setJavoblar] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [natija, setNatija] = useState(null);
  const [direction, setDirection] = useState('forward');

  useEffect(() => {
    getMashq(mashqId).then(setMashq).finally(() => setLoading(false));
  }, [mashqId]);

  if (loading) {
    return (
      <div className="max-w-2xl space-y-4">
        <Skeleton className="h-6 w-1/2" />
        <Skeleton className="h-2 w-full" />
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }
  if (!mashq) return <p className="text-sm" style={{ color: '#8A8371' }}>Mashq topilmadi.</p>;

  const savol = mashq.savollar[currentIdx];
  const jamiSavol = mashq.savollar.length;
  const javobBerilganSoni = Object.keys(javoblar).length;

  const toggleSingle = (javobId) => setJavoblar({ ...javoblar, [savol.id]: [javobId] });

  const toggleMultiple = (javobId) => {
    const current = javoblar[savol.id] || [];
    if (current.includes(javobId)) {
      setJavoblar({ ...javoblar, [savol.id]: current.filter((id) => id !== javobId) });
    } else {
      setJavoblar({ ...javoblar, [savol.id]: [...current, javobId] });
    }
  };

  const setTextAnswer = (value) => setJavoblar({ ...javoblar, [savol.id]: value });

  const goNext = () => { setDirection('forward'); setCurrentIdx((i) => Math.min(jamiSavol - 1, i + 1)); };
  const goPrev = () => { setDirection('backward'); setCurrentIdx((i) => Math.max(0, i - 1)); };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const payload = mashq.savollar.map((s) => {
        if (s.tur === 'text') return { savol: s.id, matn_javob: javoblar[s.id] || '' };
        return { savol: s.id, tanlangan_javoblar: javoblar[s.id] || [] };
      });
      const result = await topshirMashq(mashqId, payload);
      setNatija(result);
    } finally {
      setSubmitting(false);
    }
  };

  if (natija) {
    const foiz = parseFloat(natija.foiz);
    const otdi = natija.otdi ?? foiz >= 80;
    const circumference = 2 * Math.PI * 46;
    const offset = circumference - (foiz / 100) * circumference;

    return (
      <div className="animate-in max-w-lg mx-auto text-center py-10">
        <div className="relative w-32 h-32 mx-auto mb-6 animate-pop">
          <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
            <circle cx="50" cy="50" r="46" fill="none" stroke="var(--color-paper-warm)" strokeWidth="7" />
            <circle
              cx="50" cy="50" r="46" fill="none"
              stroke={otdi ? 'var(--color-forest)' : 'var(--color-amber)'}
              strokeWidth="7" strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              style={{ transition: 'stroke-dashoffset 1s cubic-bezier(0.16, 1, 0.3, 1)' }}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <CheckCircle2 size={40} style={{ color: otdi ? 'var(--color-forest)' : 'var(--color-amber)' }} />
          </div>
        </div>
        <h1 className="font-display text-4xl font-extrabold mb-2 animate-in-fast stagger-1" style={{ color: 'var(--color-ink)' }}>{natija.foiz}%</h1>
        <p className="text-sm mb-3 animate-in-fast stagger-2" style={{ color: '#8A8371' }}>
          {natija.togri_soni} ta savoldan {natija.jami_soni} tasi to'g'ri javoblandi.
        </p>
        <div
          className="text-sm font-semibold px-4 py-3 rounded-xl mb-7 animate-in-fast stagger-2"
          style={{
            background: otdi ? '#E4EFE6' : 'var(--color-amber-light)',
            color: otdi ? '#2F6E42' : '#8A5A1A',
          }}
        >
          {natija.xabar || (otdi ? "Testdan o'tdingiz." : "Keyingi mavzu ochilishi uchun kamida 80% oling.")}
        </div>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 animate-in-fast stagger-3">
          <Button variant="secondary" onClick={() => navigate(-1)} className="w-full sm:w-auto justify-center">Darsga qaytish</Button>
          {natija.daraja_id && (
            <Link to={`/oquvchi/mavzular/${natija.daraja_id}`} className="w-full sm:w-auto">
              <Button variant={natija.keyingi_mavzu_ochildi ? 'amber' : 'primary'} className="w-full justify-center">
                {natija.keyingi_mavzu_ochildi ? "Keyingi mavzuga o'tish" : "Mavzularni ko'rish"}
              </Button>
            </Link>
          )}
          <Link to="/oquvchi/natijalarim" className="w-full sm:w-auto">
            <Button className="w-full justify-center">Barcha natijalarim</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-in max-w-2xl">
      <button onClick={() => navigate(-1)} className="inline-flex items-center gap-1 text-sm mb-4 hover:underline press" style={{ color: 'var(--color-forest)' }}>
        <ChevronLeft size={15} /> Orqaga
      </button>

      <div className="flex items-center justify-between mb-2">
        <div>
          <h1 className="font-display text-xl font-bold" style={{ color: 'var(--color-ink)' }}>{mashq.sarlavha}</h1>
          <p className="text-xs mt-1" style={{ color: '#8A8371' }}>Keyingi mavzu uchun kamida 80% kerak.</p>
        </div>
        <span className="text-sm font-medium tabular-nums" style={{ color: '#8A8371' }}>{currentIdx + 1} / {jamiSavol}</span>
      </div>
      <ProgressBar value={((currentIdx + 1) / jamiSavol) * 100} tone="amber" />

      <Card key={savol.id} className={`mt-6 p-6 ${direction === 'forward' ? 'animate-slide' : 'animate-in-fast'}`}>
        <p className="text-base font-medium mb-5" style={{ color: 'var(--color-ink)' }}>{savol.matn}</p>

        {savol.tur === 'text' ? (
          <input
            type="text"
            value={javoblar[savol.id] || ''}
            onChange={(e) => setTextAnswer(e.target.value)}
            placeholder="Javobingizni yozing..."
            className="w-full px-4 py-2.5 rounded-xl border text-sm transition-all"
            style={{ borderColor: 'var(--color-line)' }}
          />
        ) : (
          <div className="space-y-2">
            {savol.javoblar.map((j, jIdx) => {
              const tanlangan = (javoblar[savol.id] || []).includes(j.id);
              return (
                <button
                  key={j.id}
                  onClick={() => (savol.tur === 'single' ? toggleSingle(j.id) : toggleMultiple(j.id))}
                  className="w-full flex items-center gap-3 px-4 py-3 rounded-xl border text-sm text-left transition-all press animate-in-fast"
                  style={{
                    borderColor: tanlangan ? 'var(--color-forest)' : 'var(--color-line)',
                    background: tanlangan ? 'var(--color-paper-warm)' : 'white',
                    color: 'var(--color-ink)',
                    animationDelay: `${jIdx * 40}ms`,
                    boxShadow: tanlangan ? '0 2px 8px rgba(27,75,67,0.1)' : 'none',
                  }}
                >
                  <span
                    className="w-4 h-4 flex-shrink-0 flex items-center justify-center transition-all"
                    style={{
                      borderRadius: savol.tur === 'single' ? '50%' : '4px',
                      border: `2px solid ${tanlangan ? 'var(--color-forest)' : '#C9C3B4'}`,
                      background: tanlangan ? 'var(--color-forest)' : 'transparent',
                    }}
                  >
                    {tanlangan && <span className="animate-pop" style={{ width: 6, height: 6, borderRadius: '50%', background: 'white' }} />}
                  </span>
                  {j.matn}
                </button>
              );
            })}
          </div>
        )}
      </Card>

      <div className="flex items-center justify-between mt-6 gap-3">
        <Button variant="secondary" onClick={goPrev} disabled={currentIdx === 0}>
          <ChevronLeft size={16} /> <span className="hidden sm:inline">Oldingi</span>
        </Button>

        <span className="text-xs font-medium" style={{ color: '#8A8371' }}>{javobBerilganSoni}/{jamiSavol} javob berildi</span>

        {currentIdx < jamiSavol - 1 ? (
          <Button onClick={goNext}>
            <span className="hidden sm:inline">Keyingi</span> <ChevronRight size={16} />
          </Button>
        ) : (
          <Button variant="amber" onClick={handleSubmit} disabled={submitting}>
            {submitting ? 'Yuborilmoqda...' : 'Yakunlash'}
          </Button>
        )}
      </div>
    </div>
  );
}
