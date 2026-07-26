import { useEffect, useState } from 'react';
import { getNazoratchilar, createNazoratchi, deleteNazoratchi, getFiliallar } from '../../api/admin';
import { Card, Button, Modal, Input, Select, Badge, EmptyState, IconButton, Skeleton } from '../../components/ui';
import { useToast } from '../../context/ToastContext';
import { Plus, Trash2, Users } from 'lucide-react';

export default function NazoratchilarPage() {
  const { showToast } = useToast();
  const [nazoratchilar, setNazoratchilar] = useState([]);
  const [filiallar, setFiliallar] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [form, setForm] = useState({ username: '', password: '', ism: '', familya: '', filial: '' });

  const load = async () => {
    setLoading(true);
    const [nazoratchiResult, filialResult] = await Promise.allSettled([
      getNazoratchilar(),
      getFiliallar(),
    ]);

    if (nazoratchiResult.status === 'fulfilled') {
      const data = nazoratchiResult.value;
      setNazoratchilar(data.results || data);
    } else {
      setNazoratchilar([]);
      showToast('Nazoratchilar ro\'yxatini yuklab bo\'lmadi. Sahifani yangilang.', 'error');
    }

    if (filialResult.status === 'fulfilled') {
      const data = filialResult.value;
      setFiliallar(data.results || data);
    } else {
      setFiliallar([]);
      showToast('Filiallar ro\'yxatini yuklab bo\'lmadi.', 'error');
    }

    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    if (form.username.trim().toLowerCase() === form.password.trim().toLowerCase()) {
      setErrorMsg("Parol login bilan bir xil bo'lishi mumkin emas.");
      return;
    }
    setSaving(true);
    try {
      await createNazoratchi(form);
      setForm({ username: '', password: '', ism: '', familya: '', filial: '' });
      setModalOpen(false);
      showToast('Nazoratchi qo\'shildi.');
      load();
    } catch (err) {
      setErrorMsg(err.response?.data?.password?.[0] || err.response?.data?.username?.[0] || 'Xatolik yuz berdi. Ma\'lumotlarni tekshiring.');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm("Nazoratchini o'chirishni tasdiqlaysizmi?")) return;
    try {
      await deleteNazoratchi(id);
      showToast('Nazoratchi o\'chirildi.');
      load();
    } catch {
      showToast("O'chirishda xatolik yuz berdi.", 'error');
    }
  };

  return (
    <div className="animate-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="font-display text-2xl font-bold mb-1" style={{ color: 'var(--color-ink)' }}>Nazoratchilar</h1>
          <p className="text-sm" style={{ color: '#8A8371' }}>Har bir nazoratchi bitta filialga biriktiriladi.</p>
        </div>
        <Button onClick={() => setModalOpen(true)} disabled={filiallar.length === 0} className="w-full sm:w-auto justify-center">
          <Plus size={16} /> Nazoratchi qo'shish
        </Button>
      </div>

      {filiallar.length === 0 && !loading && (
        <div className="mb-6 text-sm px-4 py-3 rounded-xl animate-pop" style={{ background: 'var(--color-amber-light)', color: '#8A5A1A' }}>
          Avval "Filiallar" bo'limidan kamida bitta filial qo'shing.
        </div>
      )}

      {loading ? (
        <div className="space-y-2">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-14 w-full" />)}</div>
      ) : nazoratchilar.length === 0 ? (
        <Card>
          <EmptyState
            icon={Users}
            title="Hozircha nazoratchi yo'q"
            description="Filial uchun nazoratchi qo'shib, unga login-parol bering."
          />
        </Card>
      ) : (
        <Card className="p-0 overflow-hidden">
          <div className="hidden sm:block overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left border-b" style={{ borderColor: 'var(--color-line)' }}>
                  <th className="py-3 px-5 font-medium" style={{ color: '#8A8371' }}>Ism familya</th>
                  <th className="py-3 px-5 font-medium" style={{ color: '#8A8371' }}>Login</th>
                  <th className="py-3 px-5 font-medium" style={{ color: '#8A8371' }}>Filial</th>
                  <th className="py-3 px-5 font-medium" style={{ color: '#8A8371' }}>O'quvchilar</th>
                  <th className="py-3 px-5"></th>
                </tr>
              </thead>
              <tbody>
                {nazoratchilar.map((n, idx) => (
                  <tr key={n.id} className="border-b last:border-0 animate-in-fast" style={{ borderColor: 'var(--color-line)', animationDelay: `${idx * 30}ms` }}>
                    <td className="py-3 px-5 font-medium" style={{ color: 'var(--color-ink)' }}>{n.ism} {n.familya}</td>
                    <td className="py-3 px-5" style={{ color: '#8A8371' }}>{n.username}</td>
                    <td className="py-3 px-5"><Badge tone="forest">{n.filial_nomi}</Badge></td>
                    <td className="py-3 px-5" style={{ color: 'var(--color-ink)' }}>{n.oquvchilar_soni}</td>
                    <td className="py-3 px-5 text-right">
                      <IconButton icon={Trash2} tone="danger" onClick={() => handleDelete(n.id)} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="sm:hidden divide-y" style={{ borderColor: 'var(--color-line)' }}>
            {nazoratchilar.map((n, idx) => (
              <div key={n.id} className="p-4 animate-in-fast" style={{ animationDelay: `${idx * 30}ms` }}>
                <div className="flex items-center justify-between mb-1.5">
                  <p className="font-medium text-sm" style={{ color: 'var(--color-ink)' }}>{n.ism} {n.familya}</p>
                  <IconButton icon={Trash2} tone="danger" onClick={() => handleDelete(n.id)} />
                </div>
                <p className="text-xs mb-2" style={{ color: '#8A8371' }}>{n.username}</p>
                <div className="flex items-center gap-2">
                  <Badge tone="forest">{n.filial_nomi}</Badge>
                  <span className="text-xs" style={{ color: '#8A8371' }}>{n.oquvchilar_soni} o'quvchi</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Yangi nazoratchi qo'shish">
        <form onSubmit={handleCreate} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <Input label="Ism" required value={form.ism} onChange={(e) => setForm({ ...form, ism: e.target.value })} />
            <Input label="Familya" required value={form.familya} onChange={(e) => setForm({ ...form, familya: e.target.value })} />
          </div>
          <Input label="Login" required value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} placeholder="masalan: nazoratchi_aziz" />
          <Input label="Parol" required type="text" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="Kamida 8 belgi" />
          <Select label="Filial" required value={form.filial} onChange={(e) => setForm({ ...form, filial: e.target.value })}>
            <option value="">Filialni tanlang</option>
            {filiallar.map((f) => <option key={f.id} value={f.id}>{f.nomi}</option>)}
          </Select>

          {errorMsg && (
            <div className="text-sm px-3 py-2.5 rounded-xl animate-pop" style={{ background: '#FBEAE8', color: 'var(--color-red)' }}>
              {errorMsg}
            </div>
          )}

          <div className="flex gap-2 pt-2">
            <Button type="submit" loading={saving}>{saving ? 'Saqlanmoqda...' : 'Saqlash'}</Button>
            <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>Bekor qilish</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
