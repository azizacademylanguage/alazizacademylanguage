import { useEffect, useState } from 'react';
import { KeyRound, LogOut, MonitorSmartphone, RefreshCw, ShieldAlert, ShieldCheck, UserX } from 'lucide-react';
import { Badge, Button, Card, Input, Skeleton, StatCard } from '../../components/ui';
import { adminSessiyalarniBekorQilish, barchaQurilmalardanChiqish, getAdminXavfsizlik, getMeningXavfsizligim, parolAlmashtirish } from '../../api/platform';
import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const shortDevice = (ua = '') => {
  if (!ua) return 'Noma’lum qurilma';
  const browser = /Edg\//.test(ua) ? 'Edge' : /Chrome\//.test(ua) ? 'Chrome' : /Firefox\//.test(ua) ? 'Firefox' : /Safari\//.test(ua) ? 'Safari' : 'Brauzer';
  const os = /Windows/.test(ua) ? 'Windows' : /Android/.test(ua) ? 'Android' : /iPhone|iPad/.test(ua) ? 'iOS' : /Mac OS/.test(ua) ? 'macOS' : /Linux/.test(ua) ? 'Linux' : '';
  return `${browser}${os ? ` · ${os}` : ''}`;
};

export default function XavfsizlikPage() {
  const { user, logout } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const [mine, setMine] = useState(null);
  const [admin, setAdmin] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ eski_parol: '', yangi_parol: '', yangi_parol2: '' });

  const load = async () => {
    setLoading(true);
    try {
      const myData = await getMeningXavfsizligim();
      setMine(myData);
      if (user?.role === 'admin') setAdmin(await getAdminXavfsizlik());
    } catch (e) { showToast(e.response?.data?.detail || 'Xavfsizlik ma’lumotlari yuklanmadi.', 'danger'); }
    finally { setLoading(false); }
  };
  useEffect(() => { load(); }, []);

  const changePassword = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await parolAlmashtirish(form);
      showToast(res.detail || 'Parol almashtirildi.');
      logout();
      navigate('/login');
    } catch (e) { showToast(e.response?.data?.detail || 'Parol almashtirilmadi.', 'danger'); }
    finally { setSaving(false); }
  };

  const logoutAll = async () => {
    if (!window.confirm('Barcha qurilmalardagi sessiyalarni bekor qilasizmi?')) return;
    setSaving(true);
    try {
      await barchaQurilmalardanChiqish();
      logout();
      navigate('/login');
    } catch (e) { showToast(e.response?.data?.detail || 'Sessiyalar bekor qilinmadi.', 'danger'); setSaving(false); }
  };

  const revoke = async (userId) => {
    try {
      const res = await adminSessiyalarniBekorQilish(userId);
      showToast(res.detail);
      load();
    } catch (e) { showToast(e.response?.data?.detail || 'Sessiyalar bekor qilinmadi.', 'danger'); }
  };

  if (loading) return <div className="space-y-4"><Skeleton className="h-28" /><Skeleton className="h-72" /></div>;
  return <div className="animate-in space-y-6">
    <div><h1 className="font-display text-2xl font-extrabold" style={{ color: 'var(--color-ink)' }}>Xavfsizlik</h1><p className="text-sm mt-1" style={{ color: '#8A8371' }}>Parol, login tarixi va qurilmalardagi sessiyalarni boshqaring.</p></div>

    <div className="grid lg:grid-cols-2 gap-5">
      <Card className="p-5">
        <div className="section-heading"><KeyRound size={19} /><div><h2>Parolni almashtirish</h2><p>Yangi parol kamida 8 ta belgidan iborat bo‘lsin.</p></div></div>
        <form onSubmit={changePassword} className="space-y-4 mt-5">
          <Input type="password" label="Eski parol" required value={form.eski_parol} onChange={e => setForm({ ...form, eski_parol: e.target.value })} />
          <Input type="password" label="Yangi parol" required minLength={8} value={form.yangi_parol} onChange={e => setForm({ ...form, yangi_parol: e.target.value })} />
          <Input type="password" label="Yangi parolni takrorlang" required minLength={8} value={form.yangi_parol2} onChange={e => setForm({ ...form, yangi_parol2: e.target.value })} />
          <Button type="submit" loading={saving}><ShieldCheck size={16} /> Parolni almashtirish</Button>
        </form>
      </Card>

      <Card className="p-5">
        <div className="section-heading"><MonitorSmartphone size={19} /><div><h2>Barcha qurilmalar</h2><p>Telefon va kompyuterlardagi eski tokenlarni darhol bekor qiladi.</p></div></div>
        <div className="mt-5 p-4 rounded-xl" style={{ background: '#FFF7E8', border: '1px solid #F2D59B' }}><div className="flex gap-3"><ShieldAlert size={20} style={{ color: '#A36A13' }} /><div><p className="font-semibold text-sm">Hisobingizdan boshqa kishi foydalansa</p><p className="text-xs mt-1" style={{ color: '#80633B' }}>Bu tugma barcha access va refresh tokenlarni yaroqsiz qiladi. Siz ham qayta login qilasiz.</p></div></div></div>
        <Button variant="danger" className="mt-5" onClick={logoutAll} loading={saving}><LogOut size={16} /> Barcha qurilmalardan chiqish</Button>
      </Card>
    </div>

    <Card className="overflow-hidden">
      <div className="p-5 border-b flex items-center justify-between" style={{ borderColor: 'var(--color-line)' }}><div><h2 className="font-display font-bold">Mening kirish tarixim</h2><p className="text-xs mt-1" style={{ color: '#8A8371' }}>Oxirgi muvaffaqiyatli va xato login urinishlari.</p></div><Button variant="ghost" size="sm" onClick={load}><RefreshCw size={15} /> Yangilash</Button></div>
      <div className="divide-y" style={{ borderColor: 'var(--color-line)' }}>
        {(mine?.kirishlar || []).map(x => <div key={x.id} className="p-4 flex items-center justify-between gap-4"><div className="flex items-center gap-3 min-w-0"><div className={`security-dot ${x.muvaffaqiyatli ? 'is-success' : 'is-danger'}`} /><div className="min-w-0"><p className="font-semibold text-sm">{shortDevice(x.qurilma)}</p><p className="text-xs truncate" style={{ color: '#8A8371' }}>{x.ip_manzil || 'IP noma’lum'}</p></div></div><div className="text-right flex-shrink-0"><Badge tone={x.muvaffaqiyatli ? 'success' : 'danger'}>{x.muvaffaqiyatli ? 'Muvaffaqiyatli' : 'Xato'}</Badge><p className="text-[11px] mt-1" style={{ color: '#9C9584' }}>{new Date(x.created_at).toLocaleString('uz-UZ')}</p></div></div>)}
        {(mine?.kirishlar || []).length === 0 && <div className="p-10 text-center text-sm" style={{ color: '#8A8371' }}>Kirish tarixi hali yo‘q.</div>}
      </div>
    </Card>

    {user?.role === 'admin' && admin && <>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <StatCard label="Muvaffaqiyatli — 24 soat" value={admin.muvaffaqiyatli_24_soat} icon={ShieldCheck} accent="jungle" />
        <StatCard label="Xato login — 24 soat" value={admin.xato_24_soat} icon={ShieldAlert} accent="amber" />
        <StatCard label="Faol foydalanuvchi" value={admin.faol_foydalanuvchilar} icon={MonitorSmartphone} accent="teal" />
        <StatCard label="Nofaol foydalanuvchi" value={admin.nofaol_foydalanuvchilar} icon={UserX} accent="amethyst" />
      </div>
      <Card className="overflow-hidden">
        <div className="p-5 border-b" style={{ borderColor: 'var(--color-line)' }}><h2 className="font-display font-bold">Tizim kirish jurnali</h2></div>
        <div className="overflow-x-auto"><table className="w-full text-sm min-w-[820px]"><thead><tr className="text-left" style={{ background: '#F7F9F8', color: '#8A8371' }}><th className="p-3">Foydalanuvchi</th><th className="p-3">Rol</th><th className="p-3">Qurilma</th><th className="p-3">IP</th><th className="p-3">Holat</th><th className="p-3">Sana</th><th className="p-3"></th></tr></thead><tbody className="divide-y" style={{ borderColor: 'var(--color-line)' }}>{admin.kirishlar.map(x => <tr key={x.id}><td className="p-3"><p className="font-semibold">{x.full_name}</p><p className="text-xs" style={{ color: '#8A8371' }}>@{x.username}</p></td><td className="p-3">{x.role || '—'}</td><td className="p-3">{shortDevice(x.qurilma)}</td><td className="p-3 font-mono text-xs">{x.ip_manzil || '—'}</td><td className="p-3"><Badge tone={x.muvaffaqiyatli ? 'success' : 'danger'}>{x.muvaffaqiyatli ? 'Kirdi' : 'Xato'}</Badge></td><td className="p-3 text-xs">{new Date(x.created_at).toLocaleString('uz-UZ')}</td><td className="p-3">{x.user_id && x.user_id !== user.id && <Button size="sm" variant="danger" onClick={() => revoke(x.user_id)}><UserX size={14} /> Chiqarmoq</Button>}</td></tr>)}</tbody></table></div>
      </Card>
    </>}
  </div>;
}
