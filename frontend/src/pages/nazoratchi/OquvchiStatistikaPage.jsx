import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getOquvchiStatistika, coinBerish } from '../../api/nazoratchi';
import { Card, Badge, EmptyState, Skeleton, Button, Modal, Input } from '../../components/ui';
import { ChevronLeft, ClipboardCheck, Coins, Plus } from 'lucide-react';

export default function OquvchiStatistikaPage() {
  const { oquvchiId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [coinModal, setCoinModal] = useState(false);
  const [coinForm, setCoinForm] = useState({ miqdor: 10, izoh: '' });
  const [saving, setSaving] = useState(false);
  const [muvaffaqiyat, setMuvaffaqiyat] = useState('');

  useEffect(() => {
    getOquvchiStatistika(oquvchiId).then(setData).finally(() => setLoading(false));
  }, [oquvchiId]);

  const handleCoinBerish = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await coinBerish(oquvchiId, parseInt(coinForm.miqdor, 10), coinForm.izoh);
      setMuvaffaqiyat(`${coinForm.miqdor} coin berildi!`);
      setCoinModal(false);
      setCoinForm({ miqdor: 10, izoh: '' });
      setTimeout(() => setMuvaffaqiyat(''), 3000);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-2xl space-y-4">
        <Skeleton className="h-8 w-1/2" />
        <div className="grid grid-cols-2 gap-4 max-w-md">
          <Skeleton className="h-20" /><Skeleton className="h-20" />
        </div>
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  return (
    <div className="animate-in">
      <Link to="/nazoratchi/oquvchilar" className="inline-flex items-center gap-1 text-sm mb-4 hover:underline press" style={{ color: 'var(--color-forest)' }}>
        <ChevronLeft size={15} /> O'quvchilarga qaytish
      </Link>

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-8">
        <div>
          <h1 className="font-display text-2xl font-bold mb-1" style={{ color: 'var(--color-ink)' }}>{data?.oquvchi}</h1>
          <p className="text-sm" style={{ color: '#8A8371' }}>Barcha mashq natijalari tarixi</p>
        </div>
        <Button variant="amber" onClick={() => setCoinModal(true)} className="w-full sm:w-auto justify-center">
          <Coins size={15} /> Coin berish
        </Button>
      </div>

      {muvaffaqiyat && (
        <div className="mb-4 text-sm px-3 py-2.5 rounded-xl animate-pop flex items-center gap-2" style={{ background: '#E4EFE6', color: '#2F6E42' }}>
          <Coins size={14} /> {muvaffaqiyat}
        </div>
      )}

      <div className="grid grid-cols-2 gap-4 mb-8 max-w-md">
        <Card className="p-5 animate-in-fast">
          <p className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: '#9C9584' }}>Jami urinishlar</p>
          <p className="font-display text-3xl font-extrabold" style={{ color: 'var(--color-ink)' }}>{data?.jami_urinishlar}</p>
        </Card>
        <Card className="p-5 animate-in-fast stagger-1">
          <p className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: '#9C9584' }}>O'rtacha natija</p>
          <p className="font-display text-3xl font-extrabold" style={{ color: 'var(--color-forest)' }}>{data?.ortacha_foiz}%</p>
        </Card>
      </div>

      {data?.natijalar?.length === 0 ? (
        <Card><EmptyState icon={ClipboardCheck} title="Hozircha natija yo'q" description="O'quvchi hali birorta mashq topshirmagan." /></Card>
      ) : (
        <Card className="p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left border-b" style={{ borderColor: 'var(--color-line)' }}>
                  <th className="py-3 px-5 font-medium" style={{ color: '#8A8371' }}>Mashq</th>
                  <th className="py-3 px-5 font-medium" style={{ color: '#8A8371' }}>Natija</th>
                  <th className="py-3 px-5 font-medium" style={{ color: '#8A8371' }}>Urinish</th>
                  <th className="py-3 px-5 font-medium" style={{ color: '#8A8371' }}>Sana</th>
                </tr>
              </thead>
              <tbody>
                {data.natijalar.map((n, idx) => (
                  <tr key={n.id} className="border-b last:border-0 animate-in-fast" style={{ borderColor: 'var(--color-line)', animationDelay: `${idx * 30}ms` }}>
                    <td className="py-3 px-5 font-medium" style={{ color: 'var(--color-ink)' }}>{n.mashq_sarlavha}</td>
                    <td className="py-3 px-5">
                      <Badge tone={n.foiz >= 70 ? 'success' : n.foiz >= 40 ? 'warning' : 'danger'}>
                        {n.togri_soni}/{n.jami_soni} · {n.foiz}%
                      </Badge>
                    </td>
                    <td className="py-3 px-5" style={{ color: '#8A8371' }}>#{n.urinish_raqami}</td>
                    <td className="py-3 px-5" style={{ color: '#8A8371' }}>{new Date(n.boshlangan_vaqt).toLocaleDateString('uz-UZ')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      <Modal open={coinModal} onClose={() => setCoinModal(false)} title="Coin berish" subtitle="O'quvchini rag'batlantirish uchun qo'lda coin bering.">
        <form onSubmit={handleCoinBerish} className="space-y-4">
          <Input label="Miqdor" type="number" required value={coinForm.miqdor} onChange={(e) => setCoinForm({ ...coinForm, miqdor: e.target.value })} />
          <Input label="Izoh (ixtiyoriy)" value={coinForm.izoh} onChange={(e) => setCoinForm({ ...coinForm, izoh: e.target.value })} placeholder="masalan: Faol qatnashgani uchun" />
          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={saving}><Plus size={15} /> {saving ? 'Berilmoqda...' : 'Berish'}</Button>
            <Button type="button" variant="secondary" onClick={() => setCoinModal(false)}>Bekor qilish</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
