import { useEffect, useState } from 'react';
import { getAmalLoglari } from '../../api/adminExtra';
import { Card, EmptyState, Skeleton, Badge } from '../../components/ui';
import { FileClock } from 'lucide-react';

const AMAL_RANGLAR = {
  oquvchi_yaratildi: 'success',
  fan_biriktirildi: 'forest',
  coin_berildi: 'warning',
  csv_export: 'neutral',
  csv_import: 'neutral',
};

export default function AmalLoglariPage() {
  const [loglar, setLoglar] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAmalLoglari().then(setLoglar).finally(() => setLoading(false));
  }, []);

  return (
    <div className="animate-in">
      <h1 className="font-display text-2xl font-bold mb-1" style={{ color: 'var(--color-ink)' }}>Amal loglari</h1>
      <p className="text-sm mb-8" style={{ color: '#8A8371' }}>Admin va nazoratchilar tomonidan bajarilgan so'nggi 100 ta amal.</p>

      {loading ? (
        <div className="space-y-2">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-14 w-full" />)}</div>
      ) : loglar.length === 0 ? (
        <Card><EmptyState icon={FileClock} title="Hozircha log yo'q" description="Amallar bajarilgach shu yerda ko'rinadi." /></Card>
      ) : (
        <Card className="p-0 overflow-hidden">
          <div className="divide-y" style={{ borderColor: 'var(--color-line)' }}>
            {loglar.map((log, idx) => (
              <div key={log.id} className="flex items-start justify-between p-4 animate-in-fast" style={{ animationDelay: `${idx * 20}ms` }}>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <span className="text-sm font-medium" style={{ color: 'var(--color-ink)' }}>{log.foydalanuvchi_ism}</span>
                    <Badge tone={AMAL_RANGLAR[log.amal] || 'neutral'}>{log.amal}</Badge>
                    {log.nishon_ism && <span className="text-xs" style={{ color: '#8A8371' }}>→ {log.nishon_ism}</span>}
                  </div>
                  {log.tavsif && <p className="text-xs" style={{ color: '#8A8371' }}>{log.tavsif}</p>}
                  {(log.obyekt_turi || log.ip_manzil) && <p className="text-[11px] mt-1" style={{color:'var(--color-muted)'}}>{log.obyekt_turi ? `${log.obyekt_turi} #${log.obyekt_id || '-'}` : ''}{log.ip_manzil ? ` · IP: ${log.ip_manzil}` : ''}</p>}
                </div>
                <span className="text-xs whitespace-nowrap ml-3" style={{ color: '#9C9584' }}>
                  {new Date(log.created_at).toLocaleString('uz-UZ', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
