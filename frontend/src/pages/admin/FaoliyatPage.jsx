import { useEffect, useMemo, useState } from 'react';
import { Activity, Search } from 'lucide-react';
import { getAdminFaoliyat } from '../../api/features';
import { Badge, Card, EmptyState, Skeleton } from '../../components/ui';

export default function FaoliyatPage() {
  const [items, setItems] = useState([]); const [loading, setLoading] = useState(true); const [q, setQ] = useState('');
  useEffect(() => { getAdminFaoliyat().then(setItems).finally(() => setLoading(false)); }, []);
  const filtered = useMemo(() => { const s = q.toLowerCase().trim(); return s ? items.filter(x => `${x.full_name} ${x.username} ${x.amal} ${x.tavsif} ${x.ip_manzil}`.toLowerCase().includes(s)) : items; }, [items, q]);
  return <div className="animate-in space-y-5"><div><h1 className="font-display text-2xl font-extrabold">O‘quvchilar faoliyati</h1><p className="text-sm mt-1" style={{ color: '#8A8371' }}>Kirish, dars, test, o‘yin va boshqa muhim amallar tarixi.</p></div><div className="relative max-w-lg"><Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2" /><input className="search-input" style={{ paddingLeft: 40 }} value={q} onChange={e => setQ(e.target.value)} placeholder="Ism, login, amal yoki IP..." /></div>{loading ? <Skeleton className="h-72" /> : !filtered.length ? <Card><EmptyState icon={Activity} title="Faoliyat topilmadi" description="Foydalanuvchilar amallari shu yerda ko‘rinadi." /></Card> : <div className="space-y-3">{filtered.map(x => <Card key={x.id} className="p-4"><div className="flex flex-col sm:flex-row gap-3 justify-between"><div><div className="flex flex-wrap gap-2 items-center"><p className="font-semibold">{x.full_name || x.username}</p><Badge tone="forest">{x.role}</Badge><Badge>{x.amal}</Badge></div><p className="text-sm mt-2" style={{ color: '#6F695C' }}>{x.tavsif || '—'}</p><p className="text-xs mt-2 break-all" style={{ color: '#9C9584' }}>IP: {x.ip_manzil || '—'} · {x.qurilma || 'Qurilma aniqlanmadi'}</p></div><p className="text-xs whitespace-nowrap" style={{ color: '#8A8371' }}>{new Date(x.created_at).toLocaleString('uz-UZ')}</p></div></Card>)}</div>}</div>;
}
