import { useEffect, useState } from 'react';
import { Activity, Flame } from 'lucide-react';
import { Badge, Card, EmptyState, Skeleton } from '../../components/ui';
import { getFaoliyatim } from '../../api/features';

const labels = {
  kirish: 'Kirish', dars_korildi: 'Dars ko‘rildi', dars_progress: 'Dars progressi',
  mashq_boshlandi: 'Mashq boshlandi', mashq_yakunlandi: 'Mashq yakunlandi',
  gate_test_boshlandi: 'Daraja testi boshlandi', gate_test_yakunlandi: 'Daraja testi yakunlandi',
  final_test_boshlandi: 'Yakuniy test boshlandi', final_test_yakunlandi: 'Yakuniy test yakunlandi',
  tezkor_oyin_boshlandi: 'O‘yin boshlandi', tezkor_oyin_yakunlandi: 'O‘yin yakunlandi',
};

export default function FaoliyatimPage() {
  const [data, setData] = useState(null);
  useEffect(() => { getFaoliyatim().then(setData); }, []);
  if (!data) return <div className="space-y-4"><Skeleton className="h-24" /><Skeleton className="h-64" /></div>;
  return <div className="animate-in space-y-5">
    <div><h1 className="font-display text-2xl font-extrabold">Faoliyatim</h1><p className="text-sm mt-1" style={{ color: '#8A8371' }}>Platformadagi o‘qish, test va o‘yin tarixingiz.</p></div>
    <Card className="p-5 flex items-center gap-4"><div className="w-12 h-12 rounded-xl flex items-center justify-center" style={{ background: '#FFF1D8' }}><Flame size={23} style={{ color: '#B36B00' }} /></div><div><p className="text-xs" style={{ color: '#8A8371' }}>Ketma-ket faollik</p><p className="font-display text-3xl font-extrabold">{data.streak} kun</p></div></Card>
    <Card className="overflow-hidden">
      {!data.natijalar.length ? <EmptyState icon={Activity} title="Faoliyat topilmadi" description="Darslar va testlardan foydalanganingizda tarix paydo bo‘ladi." /> : <div className="divide-y" style={{ borderColor: 'var(--color-line)' }}>{data.natijalar.map(item => <div key={item.id} className="p-4 flex items-start gap-3"><div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'var(--color-paper-warm)' }}><Activity size={17} /></div><div className="flex-1"><div className="flex flex-wrap items-center gap-2"><p className="font-semibold text-sm">{labels[item.amal] || item.amal}</p><Badge tone="neutral">{new Date(item.created_at).toLocaleDateString('uz-UZ')}</Badge></div><p className="text-sm mt-1" style={{ color: '#8A8371' }}>{item.tavsif || '—'}</p><p className="text-xs mt-1" style={{ color: '#9C9584' }}>{new Date(item.created_at).toLocaleTimeString('uz-UZ')}</p></div></div>)}</div>}
    </Card>
  </div>;
}
