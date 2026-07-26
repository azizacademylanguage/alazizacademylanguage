import { useState } from 'react';
import { topshirWriting } from '../api/writingSpeaking';
import { Card, Button } from './ui';
import { PenLine, CheckCircle2, AlertCircle } from 'lucide-react';

export default function WritingTask({ topshiriq }) {
  const [matn, setMatn] = useState('');
  const [natija, setNatija] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const sozSoni = matn.trim() ? matn.trim().split(/\s+/).length : 0;
  const yetarli = sozSoni >= topshiriq.minimal_soz_soni;

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const result = await topshirWriting(topshiriq.id, matn);
      setNatija(result);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Card className="p-5 animate-in-fast">
      <div className="flex items-center gap-2 mb-3">
        <PenLine size={16} style={{ color: 'var(--color-forest)' }} />
        <h3 className="font-display font-bold text-sm" style={{ color: 'var(--color-ink)' }}>Writing mashqi</h3>
      </div>
      <p className="text-sm mb-4" style={{ color: 'var(--color-ink)' }}>{topshiriq.matn}</p>

      {natija ? (
        <div className="animate-pop">
          <div className="flex items-center gap-2 mb-3">
            <div
              className="w-9 h-9 rounded-full flex items-center justify-center"
              style={{ background: natija.ai_foiz >= 60 ? '#E4EFE6' : 'var(--color-amber-light)' }}
            >
              {natija.ai_foiz >= 60
                ? <CheckCircle2 size={18} style={{ color: 'var(--color-forest)' }} />
                : <AlertCircle size={18} style={{ color: 'var(--color-amber-dark)' }} />}
            </div>
            <span className="font-display text-xl font-bold" style={{ color: 'var(--color-ink)' }}>{natija.ai_foiz}%</span>
          </div>
          {natija.ai_izoh && (
            <p className="text-sm mb-2 p-3 rounded-xl" style={{ background: 'var(--color-paper-warm)', color: 'var(--color-ink)' }}>
              {natija.ai_izoh}
            </p>
          )}

          {natija.baholash_tafsiloti && Object.keys(natija.baholash_tafsiloti).length > 0 && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 my-3">
              {[['Grammatika','grammatika'], ['Lug‘at','lugat_boyligi'], ['Tuzilish','tuzilish'], ['Hajm','hajm']].map(([label,key]) => (
                <div key={key} className="p-2.5 rounded-xl text-center" style={{background:'var(--color-paper-warm)'}}><p className="text-[11px]" style={{color:'var(--color-muted)'}}>{label}</p><b>{natija.baholash_tafsiloti[key] ?? 0}%</b></div>
              ))}
            </div>
          )}

          {natija.ai_xatolar?.length > 0 && (
            <div className="space-y-1">
              <p className="text-xs font-semibold" style={{ color: '#8A8371' }}>Topilgan xatolar:</p>
              {natija.ai_xatolar.map((x, i) => (
                <p key={i} className="text-xs px-2 py-1 rounded" style={{ background: '#FBEAE8', color: 'var(--color-red)' }}>{x}</p>
              ))}
            </div>
          )}
          {natija.baholash_tafsiloti?.tavsiyalar?.length > 0 && <div className="mt-3"><p className="text-xs font-semibold mb-1">Tavsiyalar:</p>{natija.baholash_tafsiloti.tavsiyalar.map((x,i)=><p key={i} className="text-xs">• {x}</p>)}</div>}
        </div>
      ) : (
        <>
          <textarea
            rows={5}
            value={matn}
            onChange={(e) => setMatn(e.target.value)}
            placeholder="Javobingizni shu yerga yozing..."
            className="w-full px-3.5 py-2.5 rounded-xl border text-sm transition-all"
            style={{ borderColor: 'var(--color-line)' }}
          />
          <div className="flex items-center justify-between mt-2">
            <span className="text-xs" style={{ color: yetarli ? 'var(--color-forest)' : '#8A8371' }}>
              {sozSoni} / {topshiriq.minimal_soz_soni} so'z
            </span>
            <Button size="sm" onClick={handleSubmit} disabled={!yetarli || submitting}>
              {submitting ? 'Tekshirilmoqda...' : 'Topshirish'}
            </Button>
          </div>
        </>
      )}
    </Card>
  );
}
