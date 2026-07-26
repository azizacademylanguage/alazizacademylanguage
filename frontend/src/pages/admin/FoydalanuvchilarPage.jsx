import { useEffect, useMemo, useState } from 'react';
import { Edit3, KeyRound, Search, ShieldCheck, UsersRound } from 'lucide-react';
import { getAdminFoydalanuvchilar, updateAdminFoydalanuvchi } from '../../api/admin';
import { Badge, Button, Card, EmptyState, IconButton, Input, Modal, Select, Skeleton } from '../../components/ui';
import { useToast } from '../../context/ToastContext';

const firstErrorMessage = (data) => {
  if (!data) return '';
  if (typeof data === 'string') return data;
  if (Array.isArray(data)) return firstErrorMessage(data[0]);
  for (const value of Object.values(data)) {
    const found = firstErrorMessage(value);
    if (found) return found;
  }
  return '';
};


const addOneMonth = (isoDate) => {
  if (!isoDate) return '';
  const [year, month, day] = isoDate.split('-').map(Number);
  const targetMonth = month === 12 ? 1 : month + 1;
  const targetYear = month === 12 ? year + 1 : year;
  const lastDay = new Date(targetYear, targetMonth, 0).getDate();
  return `${targetYear}-${String(targetMonth).padStart(2, '0')}-${String(Math.min(day, lastDay)).padStart(2, '0')}`;
};

const roleTone = { admin: 'danger', nazoratchi: 'warning', oquvchi: 'success' };

export default function FoydalanuvchilarPage() {
  const { showToast } = useToast();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({});
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const data = await getAdminFoydalanuvchilar();
      setItems(data.results || data);
    } catch {
      showToast("Foydalanuvchilarni yuklashda xatolik yuz berdi.", 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return items;
    return items.filter((item) => `${item.username} ${item.ism} ${item.familya} ${item.role_nomi} ${item.filial_nomi}`.toLowerCase().includes(q));
  }, [items, query]);

  const openEdit = (item) => {
    setEditing(item);
    setError('');
    setForm({
      username: item.username || '',
      ism: item.ism || '',
      familya: item.familya || '',
      faol: Boolean(item.faol),
      password: '',
      boshlanish_sana: item.boshlanish_sana || '',
      tugash_sana: item.tugash_sana || '',
      tolov_holati: item.tolov_holati || 'tolangan',
    });
  };

  const submit = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError('');
    try {
      if (form.password && form.password.trim().toLowerCase() === form.username.trim().toLowerCase()) {
        setError("Parol login bilan bir xil bo'lishi mumkin emas.");
        setSaving(false);
        return;
      }
      const payload = { ...form };
      if (!payload.password) delete payload.password;
      if (editing.role !== 'oquvchi') {
        delete payload.boshlanish_sana;
        delete payload.tugash_sana;
        delete payload.tolov_holati;
      }
      await updateAdminFoydalanuvchi(editing.id, payload);
      showToast('Foydalanuvchi ma’lumotlari yangilandi.');
      setEditing(null);
      load();
    } catch (err) {
      setError(firstErrorMessage(err.response?.data) || 'Saqlashda xatolik yuz berdi.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="animate-in">
      <div className="mb-6">
        <h1 className="font-display text-2xl font-bold mb-1" style={{ color: 'var(--color-ink)' }}>Barcha foydalanuvchilar</h1>
        <p className="text-sm" style={{ color: 'var(--color-muted)' }}>Loginlar ko‘rinadi. Parollar xavfsiz xesh holida saqlanadi, shuning uchun joriy parolni ko‘rib bo‘lmaydi — admin yangi parol o‘rnatadi.</p>
      </div>

      <div className="relative mb-5 max-w-md">
        <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2" style={{ color: '#9C9584' }} />
        <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Login, ism, rol yoki filial..." className="w-full pl-10 pr-3.5 py-2.5 rounded-xl border text-sm outline-none" style={{ borderColor: 'var(--color-line)' }} />
      </div>

      {loading ? (
        <div className="space-y-3">{[1, 2, 3].map((item) => <Skeleton key={item} className="h-20 w-full" />)}</div>
      ) : filtered.length === 0 ? (
        <Card><EmptyState icon={UsersRound} title="Foydalanuvchi topilmadi" description="Qidiruv so‘zini o‘zgartiring." /></Card>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
          {filtered.map((item) => (
            <Card key={item.id} className="p-5">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <h2 className="font-display font-bold truncate">{item.ism} {item.familya}</h2>
                    <Badge tone={roleTone[item.role] || 'forest'}>{item.role_nomi}</Badge>
                  </div>
                  <p className="text-sm flex items-center gap-1.5"><KeyRound size={14} /> Login: <b>{item.username}</b></p>
                  <p className="text-xs mt-1 flex items-center gap-1.5" style={{ color: 'var(--color-muted)' }}><ShieldCheck size={13} /> Parol: himoyalangan</p>
                  {item.filial_nomi && <p className="text-xs mt-2" style={{ color: 'var(--color-muted)' }}>Filial: {item.filial_nomi}</p>}
                </div>
                <IconButton icon={Edit3} title="Login yoki parolni o‘zgartirish" onClick={() => openEdit(item)} />
              </div>
            </Card>
          ))}
        </div>
      )}

      <Modal open={Boolean(editing)} onClose={() => setEditing(null)} title="Foydalanuvchini tahrirlash" subtitle="Yangi parol yozilmasa, eski parol o‘zgarmaydi." wide>
        <form onSubmit={submit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Input label="Ism" value={form.ism || ''} onChange={(event) => setForm({ ...form, ism: event.target.value })} />
            <Input label="Familya" value={form.familya || ''} onChange={(event) => setForm({ ...form, familya: event.target.value })} />
          </div>
          <Input label="Login" required value={form.username || ''} onChange={(event) => setForm({ ...form, username: event.target.value })} />
          <Input label="Yangi parol" type="text" minLength={4} value={form.password || ''} onChange={(event) => setForm({ ...form, password: event.target.value })} placeholder="Bo‘sh qoldirilsa eski parol saqlanadi" />

          {editing?.role === 'oquvchi' && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t" style={{ borderColor: 'var(--color-line)' }}>
              <Input type="date" label="Boshlanish sanasi" value={form.boshlanish_sana || ''} onChange={(event) => { const value = event.target.value; setForm({ ...form, boshlanish_sana: value, tugash_sana: addOneMonth(value) }); }} />
              <Input type="date" label="Tugash sanasi" value={form.tugash_sana || ''} onChange={(event) => setForm({ ...form, tugash_sana: event.target.value })} />
              <Select label="To‘lov holati" value={form.tolov_holati || 'tolangan'} onChange={(event) => setForm({ ...form, tolov_holati: event.target.value })}>
                <option value="tolangan">To‘langan</option>
                <option value="tolanmagan">To‘lanmagan</option>
              </Select>
            </div>
          )}

          <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={Boolean(form.faol)} onChange={(event) => setForm({ ...form, faol: event.target.checked })} /> Faol foydalanuvchi</label>
          {error && <p className="text-sm px-3 py-2.5 rounded-xl" style={{ background: '#FBEAE8', color: 'var(--color-red)' }}>{error}</p>}
          <div className="flex flex-col-reverse sm:flex-row gap-2">
            <Button type="button" variant="secondary" onClick={() => setEditing(null)} className="sm:flex-1">Bekor qilish</Button>
            <Button type="submit" loading={saving} className="sm:flex-1">Saqlash</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
