import { useEffect, useState } from 'react';
import { Flame, LockKeyhole, Trophy } from 'lucide-react';
import { Badge, Card, Skeleton } from '../../components/ui';
import { getYutuqlarim } from '../../api/features';

export default function YutuqlarimPage() {
  const [data, setData] = useState(null);
  useEffect(() => { getYutuqlarim().then(setData); }, []);
  if (!data) return <div className="grid sm:grid-cols-2 gap-4"><Skeleton className="h-36" /><Skeleton className="h-36" /></div>;
  const owned = data.yutuqlar.filter(x => x.olingan).length;
  return <div className="animate-in space-y-5">
    <div><h1 className="font-display text-2xl font-extrabold" style={{ color: 'var(--color-ink)' }}>Yutuqlarim</h1><p className="text-sm mt-1" style={{ color: '#8A8371' }}>Testlar, sertifikatlar va faollik orqali medallar va coin oling.</p></div>
    <div className="grid sm:grid-cols-3 gap-4">
      <Card className="p-5"><Trophy size={20} /><p className="text-xs mt-3" style={{ color: '#8A8371' }}>Olingan yutuqlar</p><p className="font-display text-3xl font-extrabold">{owned}/{data.yutuqlar.length}</p></Card>
      <Card className="p-5"><Flame size={20} /><p className="text-xs mt-3" style={{ color: '#8A8371' }}>Faollik seriyasi</p><p className="font-display text-3xl font-extrabold">{data.streak} kun</p></Card>
      <Card className="p-5"><span className="text-2xl">🪙</span><p className="text-xs mt-3" style={{ color: '#8A8371' }}>Yutuq mukofotlari</p><p className="font-display text-3xl font-extrabold">{data.yutuqlar.filter(x => x.olingan).reduce((a, b) => a + b.coin_mukofot, 0)}</p></Card>
    </div>
    <div className="grid md:grid-cols-2 gap-4">
      {data.yutuqlar.map(item => <Card key={item.id} className={`p-5 relative overflow-hidden ${item.olingan ? '' : 'opacity-70'}`}>
        <div className="flex gap-4"><div className="w-14 h-14 rounded-2xl flex items-center justify-center text-3xl" style={{ background: item.olingan ? '#E4EFE6' : '#F1EFE9' }}>{item.olingan ? item.icon : <LockKeyhole size={22} />}</div><div className="flex-1"><div className="flex items-center gap-2"><h2 className="font-display font-bold">{item.nomi}</h2><Badge tone={item.olingan ? 'success' : 'neutral'}>{item.olingan ? 'Olindi' : 'Qulflangan'}</Badge></div><p className="text-sm mt-1" style={{ color: '#8A8371' }}>{item.tavsif}</p><p className="text-xs font-semibold mt-3" style={{ color: 'var(--color-forest)' }}>+{item.coin_mukofot} coin</p>{item.olingan_at && <p className="text-xs mt-1" style={{ color: '#9C9584' }}>{new Date(item.olingan_at).toLocaleString('uz-UZ')}</p>}</div></div>
      </Card>)}
    </div>
  </div>;
}
