import { useEffect, useState } from 'react';
import { getNatijalarim } from '../../api/oquvchi';
import { Card, Badge, EmptyState, Skeleton } from '../../components/ui';
import { ClipboardCheck } from 'lucide-react';

export default function NatijalarimPage() {
  const [natijalar, setNatijalar] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getNatijalarim().then(setNatijalar).finally(() => setLoading(false));
  }, []);

  const ortacha = natijalar.length > 0
    ? (natijalar.reduce((sum, n) => sum + parseFloat(n.foiz), 0) / natijalar.length).toFixed(1)
    : 0;

  return (
    <div className="animate-in">
      <h1 className="font-display text-2xl font-bold mb-1" style={{ color: 'var(--color-ink)' }}>Natijalarim</h1>
      <p className="text-sm mb-8" style={{ color: '#8A8371' }}>
        Jami {natijalar.length} ta urinish · O'rtacha natija: <strong style={{ color: 'var(--color-forest)' }}>{ortacha}%</strong>
      </p>

      {loading ? (
        <div className="space-y-2">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-16 w-full" />)}</div>
      ) : natijalar.length === 0 ? (
        <Card><EmptyState icon={ClipboardCheck} title="Hozircha natija yo'q" description="Birinchi mashqingizni yeching, natijalar shu yerda ko'rinadi." /></Card>
      ) : (
        <div className="space-y-2">
          {natijalar.map((n, idx) => (
            <Card key={n.id} className="flex items-center justify-between p-4 animate-in-fast" style={{ animationDelay: `${idx * 40}ms` }}>
              <div>
                <p className="text-sm font-medium mb-1" style={{ color: 'var(--color-ink)' }}>{n.mashq_sarlavha}</p>
                <p className="text-xs" style={{ color: '#8A8371' }}>
                  {new Date(n.boshlangan_vaqt).toLocaleDateString('uz-UZ')} · Urinish #{n.urinish_raqami}
                </p>
              </div>
              <Badge tone={n.foiz >= 70 ? 'success' : n.foiz >= 40 ? 'warning' : 'danger'}>
                {n.togri_soni}/{n.jami_soni} · {n.foiz}%
              </Badge>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
