import { useEffect, useState } from 'react';
import { CalendarClock, CreditCard, ShieldCheck, TriangleAlert } from 'lucide-react';
import { Badge, Card, Skeleton } from '../../components/ui';
import { getTolovim } from '../../api/features';

export default function TolovimPage() {
  const [data, setData] = useState(null);
  useEffect(() => { getTolovim().then(setData); }, []);
  if (!data) return <div className="space-y-4"><Skeleton className="h-28" /><Skeleton className="h-64" /></div>;
  const active = data.holat === 'faol';
  return <div className="animate-in space-y-5">
    <div><h1 className="font-display text-2xl font-extrabold">To‘lov va foydalanish muddati</h1><p className="text-sm mt-1" style={{ color: '#8A8371' }}>Platformadan foydalanish holati va to‘lov tarixini ko‘ring.</p></div>
    <Card className="p-6" style={{ background: active ? '#F2FAF4' : '#FFF8EC' }}>
      <div className="flex flex-col sm:flex-row gap-4 sm:items-center justify-between"><div className="flex gap-4 items-center"><div className="w-14 h-14 rounded-2xl flex items-center justify-center" style={{ background: active ? '#DDEFE2' : '#FFE9C2' }}>{active ? <ShieldCheck size={26} /> : <TriangleAlert size={26} />}</div><div><Badge tone={active ? 'success' : 'warning'}>{active ? 'Faol' : 'Faol emas'}</Badge><h2 className="font-display text-xl font-bold mt-2">{data.xabar}</h2>{data.qolgan_kun !== null && <p className="text-sm mt-1" style={{ color: '#8A8371' }}>{data.qolgan_kun >= 0 ? `${data.qolgan_kun} kun qoldi` : `${Math.abs(data.qolgan_kun)} kun oldin tugagan`}</p>}</div></div>{data.tolov && <div className="text-left sm:text-right"><p className="text-xs" style={{ color: '#8A8371' }}>Tugash sanasi</p><p className="font-display text-xl font-bold">{data.tolov.tugash_sana}</p></div>}</div>
    </Card>
    <div className="grid sm:grid-cols-3 gap-4">{data.tolov && <><Card className="p-5"><CreditCard size={20} /><p className="text-xs mt-3" style={{ color: '#8A8371' }}>To‘langan</p><p className="font-display text-2xl font-extrabold">{Number(data.tolov.tolangan_summa).toLocaleString('uz-UZ')}</p></Card><Card className="p-5"><CreditCard size={20} /><p className="text-xs mt-3" style={{ color: '#8A8371' }}>Qolgan qarz</p><p className="font-display text-2xl font-extrabold">{Number(data.tolov.qolgan_summa).toLocaleString('uz-UZ')}</p></Card><Card className="p-5"><CalendarClock size={20} /><p className="text-xs mt-3" style={{ color: '#8A8371' }}>Holat</p><p className="font-display text-xl font-extrabold">{data.tolov.status_display}</p></Card></>}</div>
    <Card className="overflow-hidden"><div className="p-5 border-b" style={{ borderColor: 'var(--color-line)' }}><h2 className="font-display font-bold">To‘lov tarixi</h2></div><div className="overflow-x-auto"><table className="w-full text-sm"><thead><tr className="text-left" style={{ background: '#FAFCFB', color: '#8A8371' }}><th className="p-3">Muddat</th><th className="p-3">Summa</th><th className="p-3">To‘langan</th><th className="p-3">Holat</th></tr></thead><tbody>{data.tarix.map(x => <tr key={x.id} className="border-t" style={{ borderColor: 'var(--color-line)' }}><td className="p-3">{x.boshlanish_sana} — {x.tugash_sana}</td><td className="p-3">{Number(x.summa).toLocaleString('uz-UZ')}</td><td className="p-3">{Number(x.tolangan_summa).toLocaleString('uz-UZ')}</td><td className="p-3"><Badge tone={x.status === 'tolangan' || x.status === 'imtiyozli' ? 'success' : 'warning'}>{x.status_display}</Badge></td></tr>)}</tbody></table></div></Card>
  </div>;
}
