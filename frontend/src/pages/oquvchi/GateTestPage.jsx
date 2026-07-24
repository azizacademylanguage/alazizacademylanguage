import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getGateTest, topshirGateTest } from '../../api/gateTest';
import { Card, Button, ProgressBar, Skeleton } from '../../components/ui';
import { ChevronLeft, ChevronRight, Lock, CheckCircle2, XCircle, Coins } from 'lucide-react';

export default function GateTestPage() {
  const { darajaId } = useParams();
  const navigate = useNavigate();
  const [test, setTest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [javoblar, setJavoblar] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [natija, setNatija] = useState(null);

  useEffect(() => {
    getGateTest(darajaId)
      .then(setTest)
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
  }, [darajaId]);

  if (loading) {
    return (
      <div className="max-w-2xl space-y-4">
        <Skeleton className="h-6 w-1/2" />
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  if (notFound || !test) {
    return (
      <div className="max-w-lg mx-auto text-center py-16 animate-in">
        <div
          className="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-4"
          style={{ background: 'var(--color-paper-warm)' }}
        >
          <Lock size={24} style={{ color: 'var(--color-moss)' }} />
        </div>
        <p className="font-display font-bold text-base mb-1" style={{ color: 'var(--color-ink)' }}>
          Bu daraja uchun test topilmadi
        </p>
        <p className="text-sm mb-5" style={{ color: '#8A8371' }}>
          Nazoratchingiz yoki admin bilan bog'lanib, darajani qo'lda ochib berishini so'rang.
        </p>
        <Button variant="secondary" onClick={() => navigate(-1)}>Orqaga</Button>
      </div>
    );
  }

  const savol = test.savollar[currentIdx];
  const jamiSavol = test.savollar.length;
  const javobBerilganSoni = Object.keys(javoblar).length;

  const toggleJavob = (javobId) => setJavoblar({ ...javoblar, [savol.id]: [javobId] });

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const payload = test.savollar.map((s) => ({
        savol: s.id,
        tanlangan_javoblar: javoblar[s.id] || [],
      }));
      const result = await topshirGateTest(darajaId, payload);
      setNatija(result);
    } finally {
      setSubmitting(false);
    }
  };

  if (natija) {
    const otdi = natija.otdi;
    return (
      <div className="animate-in max-w-lg mx-auto text-center py-10">
        <div
          className="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 animate-pop"
          style={{ background: otdi ? '#E4EFE6' : '#FBEAE8' }}
        >
          {otdi
            ? <CheckCircle2 size={40} style={{ color: 'var(--color-forest)' }} />
            : <XCircle size={40} style={{ color: 'var(--color-red)' }} />}
        </div>
        <h1 className="font-display text-4xl font-extrabold mb-2 animate-in-fast stagger-1" style={{ color: 'var(--color-ink)' }}>
          {natija.foiz}%
        </h1>
        <p className="text-sm mb-2 animate-in-fast stagger-2" style={{ color: '#8A8371' }}>
          {natija.togri_soni} ta savoldan {natija.jami_soni} tasi to'g'ri javoblandi.
        </p>
        {otdi ? (
          <div className="flex items-center justify-center gap-1.5 text-sm font-semibold mb-8 animate-in-fast stagger-2" style={{ color: 'var(--color-amber-dark)' }}>
            <Coins size={15} /> +20 coin qo'shildi — daraja ochildi!
          </div>
        ) : (
          <p className="text-sm mb-8 animate-in-fast stagger-2" style={{ color: 'var(--color-red)' }}>
            O'tish balidan past. Qayta urinib ko'ring.
          </p>
        )}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 animate-in-fast stagger-3">
          {otdi ? (
            <Link to="/oquvchi/fanlarim" className="w-full sm:w-auto">
              <Button className="w-full justify-center">Fanlarimga qaytish</Button>
            </Link>
          ) : (
            <Button onClick={() => { setNatija(null); setJavoblar({}); setCurrentIdx(0); }} className="w-full sm:w-auto justify-center">
              Qayta urinish
            </Button>
          )}
          <Button variant="secondary" onClick={() => navigate('/oquvchi/fanlarim')} className="w-full sm:w-auto justify-center">
            Orqaga
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-in max-w-2xl">
      <Link to="/oquvchi/fanlarim" className="inline-flex items-center gap-1 text-sm mb-4 hover:underline press" style={{ color: 'var(--color-forest)' }}>
        <ChevronLeft size={15} /> Fanlarimga qaytish
      </Link>

      <div className="flex items-center gap-2 mb-1">
        <Lock size={16} style={{ color: 'var(--color-amber)' }} />
        <h1 className="font-display text-xl font-bold" style={{ color: 'var(--color-ink)' }}>{test.sarlavha}</h1>
      </div>
      <p className="text-sm mb-4" style={{ color: '#8A8371' }}>
        Bu test — keyingi darajani ochish uchun. Muvaffaqiyatli o'tsangiz, daraja avtomatik ochiladi.
      </p>

      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium tabular-nums" style={{ color: '#8A8371' }}>{currentIdx + 1} / {jamiSavol}</span>
      </div>
      <ProgressBar value={((currentIdx + 1) / jamiSavol) * 100} tone="amber" />

      <Card key={savol.id} className="mt-6 p-6 animate-slide">
        <p className="text-base font-medium mb-5" style={{ color: 'var(--color-ink)' }}>{savol.matn}</p>
        <div className="space-y-2">
          {savol.javoblar.map((j, jIdx) => {
            const tanlangan = (javoblar[savol.id] || []).includes(j.id);
            return (
              <button
                key={j.id}
                onClick={() => toggleJavob(j.id)}
                className="w-full flex items-center gap-3 px-4 py-3 rounded-xl border text-sm text-left transition-all press animate-in-fast"
                style={{
                  borderColor: tanlangan ? 'var(--color-forest)' : 'var(--color-line)',
                  background: tanlangan ? 'var(--color-paper-warm)' : 'white',
                  color: 'var(--color-ink)',
                  animationDelay: `${jIdx * 40}ms`,
                }}
              >
                <span
                  className="w-4 h-4 flex-shrink-0 rounded-full flex items-center justify-center"
                  style={{
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
      </Card>

      <div className="flex items-center justify-between mt-6 gap-3">
        <Button variant="secondary" onClick={() => setCurrentIdx((i) => Math.max(0, i - 1))} disabled={currentIdx === 0}>
          <ChevronLeft size={16} /> <span className="hidden sm:inline">Oldingi</span>
        </Button>
        <span className="text-xs font-medium" style={{ color: '#8A8371' }}>{javobBerilganSoni}/{jamiSavol} javob berildi</span>
        {currentIdx < jamiSavol - 1 ? (
          <Button onClick={() => setCurrentIdx((i) => Math.min(jamiSavol - 1, i + 1))}>
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
