import { useEffect, useState } from 'react';
import { getKengaytirilganStatistika } from '../../api/adminExtra';
import { Card, Skeleton, StatCard, Badge } from '../../components/ui';
import { Activity, AlertTriangle, Award, CreditCard, Headphones, Mic2, PenLine, Users } from 'lucide-react';
import { BarChart, Bar, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, LineChart, Line } from 'recharts';

export default function KengaytirilganStatistikaPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => { getKengaytirilganStatistika().then(setData).finally(() => setLoading(false)); }, []);

  if (loading) return <div className="grid grid-cols-1 md:grid-cols-3 gap-4">{[1,2,3,4,5,6].map(i => <Skeleton key={i} className="h-28 w-full" />)}</div>;
  const kpi = data?.kpi || {};
  const averages = data?.ortachalar || {};

  return <div className="animate-in">
    <div className="mb-6"><h1 className="font-display text-2xl font-bold" style={{color:'var(--color-ink)'}}>Kuchli statistika</h1><p className="text-sm mt-1" style={{color:'var(--color-muted)'}}>Faollik, natija, to‘lov va filiallar holati bir joyda.</p></div>
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
      <StatCard label="Jami o‘quvchi" value={kpi.jami_oquvchi || 0} icon={Users} accent="teal" />
      <StatCard label="Bugun faol" value={kpi.bugun_faol || 0} icon={Activity} accent="jungle" />
      <StatCard label="7 kun faol emas" value={kpi['7_kun_faol_emas'] || 0} icon={AlertTriangle} accent="amethyst" />
      <StatCard label="Muddati tugagan" value={kpi.muddati_tugagan || 0} icon={CreditCard} accent="olive" />
      <StatCard label="5 kunda tugaydi" value={kpi['5_kunda_tugaydi'] || 0} icon={CreditCard} accent="teal" />
      <StatCard label="To'lanmagan" value={kpi.tolanmagan || 0} icon={AlertTriangle} accent="amethyst" />
      <StatCard label="Sertifikatlar" value={kpi.sertifikatlar || 0} icon={Award} accent="jungle" />
      <StatCard label="Yangi xaridlar" value={kpi.yangi_xaridlar || 0} icon={CreditCard} accent="olive" />
    </div>

    <div className="grid grid-cols-1 xl:grid-cols-2 gap-5 mb-6">
      <Card className="p-5"><h2 className="font-display font-bold mb-4">Ta’lim natijalari</h2><div className="grid grid-cols-2 gap-3">
        {[['Test', averages.test, Activity], ['Listening', averages.listening, Headphones], ['Speaking', averages.speaking, Mic2], ['Writing', averages.writing, PenLine]].map(([label, value, Icon]) => <div key={label} className="p-4 rounded-2xl" style={{background:'var(--color-paper-warm)'}}><Icon size={18} style={{color:'var(--color-teal)'}}/><p className="text-xs mt-2" style={{color:'var(--color-muted)'}}>{label}</p><p className="font-display text-2xl font-bold">{value || 0}%</p></div>)}
      </div></Card>
      <Card className="p-5"><h2 className="font-display font-bold mb-4">Oylik yangi o‘quvchilar</h2><ResponsiveContainer width="100%" height={230}><LineChart data={data?.oylik_qoshilish || []}><CartesianGrid strokeDasharray="3 3" stroke="var(--color-line)"/><XAxis dataKey="oy"/><YAxis/><Tooltip/><Line type="monotone" dataKey="yangi" stroke="var(--color-teal)" strokeWidth={3}/></LineChart></ResponsiveContainer></Card>
    </div>

    <div className="grid grid-cols-1 xl:grid-cols-2 gap-5 mb-6">
      <Card className="p-5"><h2 className="font-display font-bold mb-4">Filiallar taqqoslanishi</h2><ResponsiveContainer width="100%" height={280}><BarChart data={data?.filiallar || []}><CartesianGrid strokeDasharray="3 3" stroke="var(--color-line)"/><XAxis dataKey="filial"/><YAxis/><Tooltip/><Bar dataKey="oquvchilar" fill="var(--color-teal)" radius={[8,8,0,0]}/><Bar dataKey="ortacha" fill="var(--color-olive)" radius={[8,8,0,0]}/></BarChart></ResponsiveContainer></Card>
      <Card className="p-5"><h2 className="font-display font-bold mb-4">Top 10 reyting</h2><div className="space-y-2">{(data?.top_reyting || []).map(item => <div key={item.oquvchi_id} className="flex items-center gap-3 p-3 rounded-xl" style={{background:'var(--color-paper-warm)'}}><Badge tone={item.orin <= 3 ? 'success' : 'neutral'}>#{item.orin}</Badge><div className="flex-1 min-w-0"><p className="font-semibold truncate">{item.ism}</p><p className="text-xs" style={{color:'var(--color-muted)'}}>{item.filial || 'Filialsiz'}</p></div><b>{item.ball}</b></div>)}</div></Card>
    </div>

    <Card className="p-5"><h2 className="font-display font-bold mb-4">E’tibor talab qiladigan o‘quvchilar</h2><div className="overflow-x-auto"><table className="w-full text-sm"><thead><tr><th className="text-left py-2">O‘quvchi</th><th className="text-left">Login</th><th className="text-left">Filial</th><th className="text-left">Muddat</th></tr></thead><tbody>{(data?.ehtibor_talab || []).map(item => <tr key={item.id} className="border-t" style={{borderColor:'var(--color-line)'}}><td className="py-3">{item.ism} {item.familya}</td><td>{item.username}</td><td>{item.filial__nomi || '-'}</td><td>{item.tugash_sana || '-'}</td></tr>)}</tbody></table></div></Card>
  </div>;
}
