import { useEffect, useState } from 'react';
import { Activity, AlertTriangle, Award, BrainCircuit, ClipboardCheck, MessageSquareWarning, TrendingUp, Users } from 'lucide-react';
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Badge, Card, Select, Skeleton, StatCard } from '../../components/ui';
import { getKuchliAnalitika } from '../../api/platform';
import { getFiliallar } from '../../api/admin';
import { useToast } from '../../context/ToastContext';

export default function KuchliAnalitikaPage() {
  const { showToast } = useToast();
  const [data, setData] = useState(null);
  const [filiallar, setFiliallar] = useState([]);
  const [filters, setFilters] = useState({ kunlar: 30, filial: '' });
  const [loading, setLoading] = useState(true);

  useEffect(() => { getFiliallar().then(r => setFiliallar(r.results || r || [])).catch(() => {}); }, []);
  useEffect(() => {
    setLoading(true);
    getKuchliAnalitika(filters)
      .then(setData)
      .catch(e => showToast(e.response?.data?.detail || 'Analitika yuklanmadi.', 'danger'))
      .finally(() => setLoading(false));
  }, [filters.kunlar, filters.filial]);

  const u = data?.umumiy || {};
  return (
    <div className="animate-in space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-extrabold" style={{ color: 'var(--color-ink)' }}>Kuchli analitika</h1>
          <p className="text-sm mt-1" style={{ color: '#8A8371' }}>Xavf guruhidagi o‘quvchilar, qiyin mavzular va real o‘quv faolligi.</p>
        </div>
        <div className="grid grid-cols-2 gap-2 min-w-[300px]">
          <Select value={filters.kunlar} onChange={e => setFilters({ ...filters, kunlar: e.target.value })}>
            <option value="7">Oxirgi 7 kun</option><option value="30">Oxirgi 30 kun</option><option value="90">Oxirgi 90 kun</option><option value="365">Oxirgi 1 yil</option>
          </Select>
          <Select value={filters.filial} onChange={e => setFilters({ ...filters, filial: e.target.value })}>
            <option value="">Barcha filiallar</option>{filiallar.map(f => <option key={f.id} value={f.id}>{f.nomi}</option>)}
          </Select>
        </div>
      </div>

      {loading ? <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">{[1,2,3,4,5,6,7,8].map(x => <Skeleton key={x} className="h-28" />)}</div> : <>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <StatCard label="O‘quvchilar" value={u.oquvchilar || 0} icon={Users} accent="forest" />
          <StatCard label="Faol — 7 kun" value={u.faol_7_kun || 0} icon={Activity} accent="teal" />
          <StatCard label="O‘rtacha natija" value={`${u.ortacha_foiz || 0}%`} icon={TrendingUp} accent="jungle" />
          <StatCard label="Test urinishlari" value={u.urinishlar || 0} icon={ClipboardCheck} accent="moss" />
          <StatCard label="Sertifikatlar" value={u.sertifikatlar || 0} icon={Award} accent="olive" />
          <StatCard label="Writing / Speaking" value={`${u.writing_ortacha || 0}% / ${u.speaking_ortacha || 0}%`} icon={BrainCircuit} accent="amethyst" />
          <StatCard label="Ochiq murojaat" value={u.ochiq_murojaatlar || 0} icon={MessageSquareWarning} accent="amber" />
          <StatCard label="Xavf guruhi" value={u.xavf_guruhi || 0} icon={AlertTriangle} accent="amber" />
        </div>

        <Card className="p-5">
          <h2 className="font-display font-bold mb-4">Kunlik test faolligi</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data?.kunlik_faollik || []} margin={{ left: -20, right: 8 }}>
                <defs><linearGradient id="activityFill" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="var(--color-teal)" stopOpacity={0.28}/><stop offset="95%" stopColor="var(--color-teal)" stopOpacity={0}/></linearGradient></defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,.07)" />
                <XAxis dataKey="sana" tickFormatter={v => new Date(v).toLocaleDateString('uz-UZ', { day: '2-digit', month: '2-digit' })} fontSize={11} />
                <YAxis allowDecimals={false} fontSize={11} />
                <Tooltip labelFormatter={v => new Date(v).toLocaleDateString('uz-UZ')} formatter={(v, n) => [v, n === 'urinishlar' ? 'Urinishlar' : n]} />
                <Area type="monotone" dataKey="urinishlar" stroke="var(--color-teal)" fill="url(#activityFill)" strokeWidth={2.5} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <div className="grid lg:grid-cols-2 gap-5">
          <Card className="p-5 overflow-hidden">
            <h2 className="font-display font-bold mb-4">Eng qiyin mavzular</h2>
            <div className="space-y-3">
              {(data?.qiyin_mavzular || []).length === 0 ? <p className="text-sm" style={{ color: '#8A8371' }}>Hozircha ma’lumot yetarli emas.</p> : data.qiyin_mavzular.map((x, i) => (
                <div key={`${x.fan}-${x.mavzu}`} className="analytics-row">
                  <div className="analytics-rank">{i + 1}</div>
                  <div className="min-w-0 flex-1"><p className="font-semibold text-sm truncate">{x.mavzu}</p><p className="text-xs" style={{ color: '#8A8371' }}>{x.fan} · {x.urinishlar} urinish</p></div>
                  <Badge tone={x.ortacha < 50 ? 'danger' : x.ortacha < 70 ? 'warning' : 'success'}>{x.ortacha}%</Badge>
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-5 overflow-hidden">
            <h2 className="font-display font-bold mb-4">Eng ko‘p xato qilingan savollar</h2>
            <div className="space-y-3">
              {(data?.kop_xato_savollar || []).length === 0 ? <p className="text-sm" style={{ color: '#8A8371' }}>Hozircha xato statistikasi yo‘q.</p> : data.kop_xato_savollar.map((x, i) => (
                <div key={`${x.savol}-${i}`} className="analytics-row items-start">
                  <div className="analytics-rank analytics-rank--danger">{x.xatolar}</div>
                  <div className="min-w-0 flex-1"><p className="font-semibold text-sm line-clamp-2">{x.savol}</p><p className="text-xs mt-1" style={{ color: '#8A8371' }}>{x.dars}</p></div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <Card className="overflow-hidden">
          <div className="p-5 border-b" style={{ borderColor: 'var(--color-line)' }}><h2 className="font-display font-bold">Xavf guruhidagi o‘quvchilar</h2><p className="text-xs mt-1" style={{ color: '#8A8371' }}>7 kun faol bo‘lmagan yoki natijasi past o‘quvchilar.</p></div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm min-w-[760px]">
              <thead><tr className="text-left" style={{ background: '#F7F9F8', color: '#8A8371' }}><th className="p-3">O‘quvchi</th><th className="p-3">Filial</th><th className="p-3">O‘rtacha</th><th className="p-3">Urinish</th><th className="p-3">Oxirgi faollik</th><th className="p-3">Sabab</th></tr></thead>
              <tbody className="divide-y" style={{ borderColor: 'var(--color-line)' }}>
                {(data?.xavf_guruhi || []).map(x => <tr key={x.id}><td className="p-3"><p className="font-semibold">{x.full_name}</p><p className="text-xs" style={{ color: '#8A8371' }}>@{x.username}</p></td><td className="p-3">{x.filial || '—'}</td><td className="p-3"><Badge tone={x.ortacha < 50 ? 'danger' : 'warning'}>{x.ortacha}%</Badge></td><td className="p-3">{x.urinishlar}</td><td className="p-3 text-xs">{x.oxirgi_faollik ? new Date(x.oxirgi_faollik).toLocaleDateString('uz-UZ') : 'Faollik yo‘q'}</td><td className="p-3"><div className="flex flex-wrap gap-1">{x.sabablar.map(s => <Badge key={s} tone={x.xavf_darajasi === 'yuqori' ? 'danger' : 'warning'}>{s}</Badge>)}</div></td></tr>)}
                {(data?.xavf_guruhi || []).length === 0 && <tr><td colSpan="6" className="p-10 text-center" style={{ color: '#8A8371' }}>Xavf guruhidagi o‘quvchi topilmadi.</td></tr>}
              </tbody>
            </table>
          </div>
        </Card>

        <Card className="overflow-hidden">
          <div className="p-5 border-b" style={{ borderColor: 'var(--color-line)' }}><h2 className="font-display font-bold">Filiallar natijasi</h2></div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 p-4">
            {(data?.filiallar || []).map(f => <div key={f.id} className="p-4 rounded-xl border" style={{ borderColor: 'var(--color-line)', background: '#FAFCFB' }}><div className="flex items-center justify-between"><p className="font-display font-bold">{f.nomi}</p><Badge tone={f.ortacha >= 80 ? 'success' : f.ortacha >= 60 ? 'warning' : 'danger'}>{f.ortacha}%</Badge></div><div className="grid grid-cols-3 gap-2 mt-4 text-center"><div><strong>{f.oquvchilar}</strong><span>O‘quvchi</span></div><div><strong>{f.urinishlar}</strong><span>Urinish</span></div><div><strong>{f.sertifikatlar}</strong><span>Sertifikat</span></div></div></div>)}
          </div>
        </Card>
      </>}
    </div>
  );
}
