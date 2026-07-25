import { useEffect, useMemo, useState } from 'react';
import { Bell, Plus, Search, Trash2 } from 'lucide-react';
import { createBildirishnoma, deleteBildirishnoma, getAdminBildirishnomalar, updateBildirishnoma } from '../../api/features';
import { getAdminOquvchilar, getFanlar } from '../../api/admin';
import { Badge, Button, Card, EmptyState, Input, Modal, Select, Skeleton, Textarea } from '../../components/ui';
import { useToast } from '../../context/ToastContext';

const emptyForm = { sarlavha: '', matn: '', tur: 'info', target_turi: 'all', target_user: '', target_fan: '', target_daraja: '', havola: '', tugash_sana: '' };
const tones = { info: 'forest', success: 'success', warning: 'warning', danger: 'danger' };

export default function BildirishnomalarPage() {
  const { showToast } = useToast();
  const [items, setItems] = useState([]);
  const [students, setStudents] = useState([]);
  const [fanlar, setFanlar] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [modal, setModal] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [query, setQuery] = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const [notifications, studentData, fanData] = await Promise.all([getAdminBildirishnomalar(), getAdminOquvchilar(), getFanlar()]);
      setItems(notifications);
      setStudents(studentData.results || studentData);
      setFanlar(fanData.results || fanData);
    } catch (e) { showToast(e.response?.data?.detail || 'Ma’lumotlar yuklanmadi.', 'danger'); }
    finally { setLoading(false); }
  };
  useEffect(() => { load(); }, []);

  const selectedFan = fanlar.find(x => String(x.id) === String(form.target_fan));
  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return q ? items.filter(x => `${x.sarlavha} ${x.matn} ${x.target_display} ${x.target_user_ism}`.toLowerCase().includes(q)) : items;
  }, [items, query]);

  const submit = async (e) => {
    e.preventDefault(); setSaving(true);
    try {
      await createBildirishnoma({
        ...form,
        target_user: form.target_turi === 'user' ? form.target_user : null,
        target_fan: form.target_turi === 'fan' ? form.target_fan : null,
        target_daraja: form.target_turi === 'daraja' ? form.target_daraja : null,
        tugash_sana: form.tugash_sana || null,
      });
      setModal(false); setForm(emptyForm); showToast('Bildirishnoma yuborildi.'); load();
    } catch (err) { showToast(err.response?.data?.detail || 'Bildirishnoma yuborilmadi.', 'danger'); }
    finally { setSaving(false); }
  };

  const toggle = async (item) => {
    try { await updateBildirishnoma(item.id, { faol: !item.faol }); showToast(item.faol ? 'Bildirishnoma o‘chirildi.' : 'Bildirishnoma faollashtirildi.'); load(); }
    catch { showToast('Holat o‘zgarmadi.', 'danger'); }
  };
  const remove = async (item) => {
    if (!confirm(`“${item.sarlavha}” bildirishnomasini o‘chirasizmi?`)) return;
    try { await deleteBildirishnoma(item.id); showToast('Bildirishnoma o‘chirildi.'); load(); }
    catch { showToast('O‘chirishda xato.', 'danger'); }
  };

  return <div className="animate-in space-y-5">
    <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-3">
      <div><h1 className="font-display text-2xl font-extrabold">Bildirishnomalar</h1><p className="text-sm mt-1" style={{ color: '#8A8371' }}>Barcha o‘quvchilarga yoki tanlangan fan, daraja va o‘quvchiga xabar yuboring.</p></div>
      <Button onClick={() => { setForm(emptyForm); setModal(true); }}><Plus size={17} /> Yangi xabar</Button>
    </div>
    <div className="relative max-w-lg"><Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2" style={{ color: '#9C9584' }} /><input className="search-input" style={{ paddingLeft: 40 }} value={query} onChange={e => setQuery(e.target.value)} placeholder="Xabar yoki qabul qiluvchi bo‘yicha qidirish..." /></div>
    {loading ? <div className="space-y-3"><Skeleton className="h-28" /><Skeleton className="h-28" /></div> : !filtered.length ? <Card><EmptyState icon={Bell} title="Bildirishnoma yo‘q" description="Birinchi xabarni yuboring." /></Card> : <div className="space-y-3">
      {filtered.map(item => <Card key={item.id} className={`p-5 ${item.faol ? '' : 'opacity-60'}`}>
        <div className="flex flex-col sm:flex-row sm:items-start gap-4 justify-between"><div className="min-w-0"><div className="flex flex-wrap gap-2 items-center"><h2 className="font-display font-bold">{item.sarlavha}</h2><Badge tone={tones[item.tur] || 'neutral'}>{item.tur_display}</Badge><Badge tone={item.faol ? 'success' : 'neutral'}>{item.faol ? 'Faol' : 'O‘chirilgan'}</Badge></div><p className="text-sm mt-2 whitespace-pre-line" style={{ color: '#6F695C' }}>{item.matn}</p><div className="flex flex-wrap gap-3 mt-3 text-xs" style={{ color: '#8A8371' }}><span>Qabul qiluvchi: {item.target_display}{item.target_user_ism ? ` — ${item.target_user_ism}` : ''}{item.target_fan_nomi ? ` — ${item.target_fan_nomi}` : ''}{item.target_daraja_nomi ? ` — ${item.target_daraja_nomi}` : ''}</span><span>O‘qilgan: {item.oqilganlar_soni}</span><span>{new Date(item.created_at).toLocaleString('uz-UZ')}</span></div></div><div className="flex gap-2 flex-shrink-0"><Button size="sm" variant="secondary" onClick={() => toggle(item)}>{item.faol ? 'O‘chirish' : 'Yoqish'}</Button><Button size="sm" variant="danger" onClick={() => remove(item)}><Trash2 size={15} /></Button></div></div>
      </Card>)}
    </div>}

    <Modal open={modal} onClose={() => setModal(false)} title="Yangi bildirishnoma" subtitle="Xabar sayt ichidagi bildirishnomalar bo‘limida ko‘rinadi." wide>
      <form onSubmit={submit} className="space-y-4">
        <Input label="Sarlavha" required value={form.sarlavha} onChange={e => setForm({ ...form, sarlavha: e.target.value })} />
        <Textarea label="Xabar matni" required rows={4} value={form.matn} onChange={e => setForm({ ...form, matn: e.target.value })} />
        <div className="grid sm:grid-cols-2 gap-3"><Select label="Xabar turi" value={form.tur} onChange={e => setForm({ ...form, tur: e.target.value })}><option value="info">Ma’lumot</option><option value="success">Muvaffaqiyat</option><option value="warning">Ogohlantirish</option><option value="danger">Muhim</option></Select><Select label="Qabul qiluvchi" value={form.target_turi} onChange={e => setForm({ ...form, target_turi: e.target.value, target_user: '', target_fan: '', target_daraja: '' })}><option value="all">Barcha o‘quvchilar</option><option value="user">Bitta o‘quvchi</option><option value="fan">Fan bo‘yicha</option><option value="daraja">Daraja bo‘yicha</option></Select></div>
        {form.target_turi === 'user' && <Select label="O‘quvchi" required value={form.target_user} onChange={e => setForm({ ...form, target_user: e.target.value })}><option value="">Tanlang</option>{students.map(x => <option key={x.id} value={x.id}>{x.ism} {x.familya} ({x.username})</option>)}</Select>}
        {(form.target_turi === 'fan' || form.target_turi === 'daraja') && <Select label="Fan" required value={form.target_fan} onChange={e => setForm({ ...form, target_fan: e.target.value, target_daraja: '' })}><option value="">Tanlang</option>{fanlar.map(x => <option key={x.id} value={x.id}>{x.nomi}</option>)}</Select>}
        {form.target_turi === 'daraja' && <Select label="Daraja" required value={form.target_daraja} onChange={e => setForm({ ...form, target_daraja: e.target.value })}><option value="">Tanlang</option>{(selectedFan?.darajalar || []).map(x => <option key={x.id} value={x.id}>{x.nomi}</option>)}</Select>}
        <Input label="Ochilganda o‘tadigan ichki havola" hint="Masalan: /oquvchi/sertifikatlarim" value={form.havola} onChange={e => setForm({ ...form, havola: e.target.value })} />
        <Input type="datetime-local" label="Tugash vaqti (ixtiyoriy)" value={form.tugash_sana} onChange={e => setForm({ ...form, tugash_sana: e.target.value })} />
        <div className="flex justify-end gap-2"><Button variant="secondary" onClick={() => setModal(false)}>Bekor qilish</Button><Button type="submit" loading={saving}>Yuborish</Button></div>
      </form>
    </Modal>
  </div>;
}
