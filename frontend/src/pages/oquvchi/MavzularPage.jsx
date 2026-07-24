import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getMavzular } from '../../api/oquvchi';
import { Badge, Button, Card, EmptyState, ProgressBar, Skeleton } from '../../components/ui';
import { CheckCircle2, ChevronLeft, Circle, Layers, Lock, PlayCircle, Trophy, Unlock } from 'lucide-react';

export default function MavzularPage() {
  const { darajaId } = useParams();
  const [mavzular, setMavzular] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = () => {
    setLoading(true);
    setError('');
    getMavzular(darajaId)
      .then(setMavzular)
      .catch((err) => setError(err.response?.data?.detail || "Mavzularni yuklab bo'lmadi."))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [darajaId]);

  const hammasiTugagan = mavzular.length > 0 && mavzular.every((mavzu) => mavzu.otilgan);

  return (
    <div className="animate-in">
      <Link to="/oquvchi/fanlarim" className="inline-flex items-center gap-1 text-sm mb-4 hover:underline press" style={{ color: 'var(--color-forest)' }}>
        <ChevronLeft size={15} /> Fanlarimga qaytish
      </Link>

      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-3 mb-8">
        <div>
          <h1 className="font-display text-2xl font-bold mb-1" style={{ color: 'var(--color-ink)' }}>Mavzular</h1>
          <p className="text-sm" style={{ color: '#8A8371' }}>Keyingi mavzu ochilishi uchun joriy mavzu testidan kamida 80% oling.</p>
        </div>
        {!loading && <Badge tone="forest">O'tish bali: 80%</Badge>}
      </div>

      {loading ? (
        <div className="space-y-4">{[1, 2, 3].map((item) => <Skeleton key={item} className="h-36 w-full" />)}</div>
      ) : error ? (
        <Card className="p-5">
          <p className="text-sm mb-4" style={{ color: 'var(--color-red)' }}>{error}</p>
          <Button variant="secondary" onClick={load}>Qayta yuklash</Button>
        </Card>
      ) : mavzular.length === 0 ? (
        <Card><EmptyState icon={Layers} title="Hozircha mavzu yo'q" description="Admin bu darajaga mavzular qo'shishi kerak." /></Card>
      ) : (
        <>
          <div className="space-y-4 mb-6">
            {mavzular.map((mavzu, index) => {
              const ochiq = mavzu.ochiq !== false;
              const score = Number(mavzu.eng_yaxshi_foiz || 0);
              const progress = mavzu.otilgan ? 100 : Math.min(score, 100);

              return (
                <Card
                  key={mavzu.id}
                  className="animate-in-fast overflow-hidden"
                  style={{ animationDelay: `${index * 60}ms`, opacity: ochiq ? 1 : 0.72 }}
                >
                  <div className="p-5">
                    <div className="flex items-start justify-between gap-3 mb-3">
                      <div className="flex items-start gap-3">
                        <div
                          className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
                          style={{ background: ochiq ? 'var(--color-paper-warm)' : '#EEECE6' }}
                        >
                          {ochiq
                            ? <Unlock size={16} style={{ color: 'var(--color-forest)' }} />
                            : <Lock size={16} style={{ color: '#8A8371' }} />}
                        </div>
                        <div>
                          <h3 className="font-display font-bold text-sm" style={{ color: 'var(--color-ink)' }}>
                            {index + 1}. {mavzu.nomi}
                          </h3>
                          <p className="text-xs mt-1" style={{ color: '#8A8371' }}>
                            {mavzu.otilgan
                              ? 'Test muvaffaqiyatli topshirilgan.'
                              : ochiq
                                ? 'Tushuntirishni o‘qing va testni bajaring.'
                                : mavzu.qulf_sababi}
                          </p>
                        </div>
                      </div>
                      <Badge tone={mavzu.otilgan ? 'success' : ochiq ? 'forest' : 'neutral'}>
                        {mavzu.otilgan ? 'Bajarildi' : ochiq ? 'Ochiq' : 'Qulflangan'}
                      </Badge>
                    </div>

                    {ochiq && (
                      <>
                        <div className="flex items-center justify-between text-xs mb-1.5" style={{ color: '#8A8371' }}>
                          <span>Eng yaxshi natija</span>
                          <span className="font-semibold">{score}% / 80%</span>
                        </div>
                        <ProgressBar value={progress} tone={mavzu.otilgan ? 'forest' : 'amber'} />

                        <div className="mt-4 space-y-2">
                          {mavzu.darslar.map((dars) => (
                            <Link
                              key={dars.id}
                              to={`/oquvchi/dars/${dars.id}`}
                              className="flex items-center justify-between px-3 py-2.5 rounded-xl text-sm transition-all press hover:shadow-sm"
                              style={{ background: 'var(--color-paper-warm)' }}
                            >
                              <span className="flex items-center gap-2.5" style={{ color: 'var(--color-ink)' }}>
                                {dars.testdan_otilgan
                                  ? <CheckCircle2 size={15} style={{ color: 'var(--color-forest)' }} />
                                  : <Circle size={15} style={{ color: '#B8B2A2' }} />}
                                <span>
                                  {dars.sarlavha}
                                  {dars.eng_yaxshi_foiz > 0 && (
                                    <span className="block text-[11px] mt-0.5" style={{ color: '#8A8371' }}>
                                      Test: {dars.eng_yaxshi_foiz}%
                                    </span>
                                  )}
                                </span>
                              </span>
                              <PlayCircle size={16} style={{ color: 'var(--color-forest-light)' }} />
                            </Link>
                          ))}
                          {mavzu.darslar.length === 0 && (
                            <p className="text-xs px-3 py-2.5 rounded-xl" style={{ background: '#F7F6F2', color: '#8A8371' }}>
                              Bu mavzuga hali dars qo'shilmagan.
                            </p>
                          )}
                        </div>
                      </>
                    )}
                  </div>
                </Card>
              );
            })}
          </div>

          {hammasiTugagan && (
            <Card
              className="p-6 text-center animate-pop"
              style={{ background: 'linear-gradient(135deg, var(--color-forest) 0%, var(--color-forest-dark) 100%)', border: 'none' }}
            >
              <Trophy size={28} color="var(--color-amber)" className="mx-auto mb-3" />
              <p className="font-display font-bold text-white text-base mb-1">Barcha mavzularni 80%+ bilan tugatdingiz!</p>
              <p className="text-white/70 text-sm mb-4">Endi yakuniy testni topshirishingiz mumkin.</p>
              <Link to={`/oquvchi/final-test/${darajaId}`}>
                <Button variant="amber">Yakuniy testni boshlash</Button>
              </Link>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
