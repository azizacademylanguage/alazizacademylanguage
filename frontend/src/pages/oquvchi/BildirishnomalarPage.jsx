import { useEffect, useState } from 'react';
import { Bell, CheckCheck, ExternalLink } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Badge, Button, Card, EmptyState, Skeleton } from '../../components/ui';
import { barchaBildirishnomalarniOqish, bildirishnomaOqish, getBildirishnomalarim } from '../../api/features';

const tones = { info: 'forest', success: 'success', warning: 'warning', danger: 'danger' };

export default function BildirishnomalarPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = () => getBildirishnomalarim().then(setData).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const markRead = async (item) => {
    if (!item.oqilgan) await bildirishnomaOqish(item.id);
    if (item.havola) window.location.assign(item.havola);
    else load();
  };

  const markAll = async () => { await barchaBildirishnomalarniOqish(); load(); };

  if (loading) return <div className="space-y-4"><Skeleton className="h-20" /><Skeleton className="h-28" /><Skeleton className="h-28" /></div>;
  const items = data?.natijalar || [];

  return <div className="animate-in space-y-5">
    <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-3">
      <div><h1 className="font-display text-2xl font-extrabold" style={{ color: 'var(--color-ink)' }}>Bildirishnomalar</h1><p className="text-sm mt-1" style={{ color: '#8A8371' }}>Yangi mavzu, sertifikat, to‘lov va admin xabarlarini shu yerda ko‘rasiz.</p></div>
      <Button variant="secondary" onClick={markAll} disabled={!data?.oqilmagan_soni}><CheckCheck size={17} /> Barchasini o‘qish</Button>
    </div>

    <Card className="p-4 flex items-center gap-3"><div className="w-11 h-11 rounded-xl flex items-center justify-center" style={{ background: 'var(--color-paper-warm)' }}><Bell size={20} style={{ color: 'var(--color-forest)' }} /></div><div><p className="text-xs" style={{ color: '#8A8371' }}>O‘qilmagan</p><p className="font-display text-2xl font-extrabold">{data?.oqilmagan_soni || 0}</p></div></Card>

    {!items.length ? <Card><EmptyState icon={Bell} title="Bildirishnoma yo‘q" description="Yangi xabarlar shu yerda paydo bo‘ladi." /></Card> : <div className="space-y-3">
      {items.map(item => <Card key={item.id} className={`p-5 ${item.oqilgan ? 'opacity-75' : ''}`}>
        <div className="flex items-start gap-4">
          <div className="w-3 h-3 mt-2 rounded-full flex-shrink-0" style={{ background: item.oqilgan ? '#D4D0C6' : 'var(--color-forest)' }} />
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2"><h2 className="font-display font-bold" style={{ color: 'var(--color-ink)' }}>{item.sarlavha}</h2><Badge tone={tones[item.tur] || 'neutral'}>{item.tur_display}</Badge>{!item.oqilgan && <Badge tone="warning">Yangi</Badge>}</div>
            <p className="text-sm mt-2 whitespace-pre-line" style={{ color: '#6F695C' }}>{item.matn}</p>
            <p className="text-xs mt-3" style={{ color: '#9C9584' }}>{new Date(item.created_at).toLocaleString('uz-UZ')}</p>
          </div>
          <button type="button" onClick={() => markRead(item)} className="press p-2 rounded-lg hover:bg-black/5" title={item.havola ? 'Ochish' : 'O‘qildi'}>{item.havola ? <ExternalLink size={18} /> : <CheckCheck size={18} />}</button>
        </div>
      </Card>)}
    </div>}
  </div>;
}
