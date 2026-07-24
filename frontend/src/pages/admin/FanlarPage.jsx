import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getFanlar, createFan, deleteFan } from '../../api/admin';
import { Card, Button, Modal, Input, EmptyState, IconButton, Skeleton } from '../../components/ui';
import { useToast } from '../../context/ToastContext';
import { Plus, Trash2, BookOpen, ChevronRight } from 'lucide-react';

export default function FanlarPage() {
  const { showToast } = useToast();
  const [fanlar, setFanlar] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [form, setForm] = useState({ nomi: '', tavsif: '' });

  const load = () => getFanlar().then((r) => setFanlar(r.results || r)).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setSaving(true);
    setErrorMsg('');
    try {
      await createFan(form);
      setForm({ nomi: '', tavsif: '' });
      setModalOpen(false);
      showToast('Fan qo\'shildi.');
      load();
    } catch (err) {
      setErrorMsg(err.response?.data?.nomi?.[0] || 'Xatolik yuz berdi.');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id, e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!confirm("Fanni va unga tegishli barcha darajalar/mavzular/darslarni o'chirishni tasdiqlaysizmi?")) return;
    try {
      await deleteFan(id);
      showToast('Fan o\'chirildi.');
      load();
    } catch {
      showToast("O'chirishda xatolik yuz berdi.", 'error');
    }
  };

  const gradients = [
    'linear-gradient(135deg, var(--color-forest) 0%, var(--color-forest-light) 100%)',
    'linear-gradient(135deg, var(--color-amber-dark) 0%, var(--color-amber) 100%)',
    'linear-gradient(135deg, var(--color-forest-light) 0%, var(--color-moss) 100%)',
  ];

  return (
    <div className="animate-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="font-display text-2xl font-bold mb-1" style={{ color: 'var(--color-ink)' }}>Ta'lim mazmuni</h1>
          <p className="text-sm" style={{ color: '#8A8371' }}>Fan → Daraja → Mavzu → Dars → Mashq</p>
        </div>
        <Button onClick={() => setModalOpen(true)} className="w-full sm:w-auto justify-center"><Plus size={16} /> Fan qo'shish</Button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-36 w-full" />)}
        </div>
      ) : fanlar.length === 0 ? (
        <Card><EmptyState icon={BookOpen} title="Hozircha fan yo'q" description="Birinchi fanni qo'shing, masalan: English, Matematika." /></Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {fanlar.map((f, idx) => (
            <Link key={f.id} to={`/admin/fanlar/${f.id}`} className="animate-in-fast" style={{ animationDelay: `${idx * 50}ms` }}>
              <Card hover className="h-full">
                <div className="p-5">
                  <div className="flex items-start justify-between mb-3">
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: gradients[idx % gradients.length] }}>
                      <BookOpen size={17} color="white" />
                    </div>
                    <IconButton icon={Trash2} tone="danger" onClick={(e) => handleDelete(f.id, e)} />
                  </div>
                  <p className="font-display font-bold text-sm mb-1" style={{ color: 'var(--color-ink)' }}>{f.nomi}</p>
                  {f.tavsif && <p className="text-xs mb-3 line-clamp-2" style={{ color: '#8A8371' }}>{f.tavsif}</p>}
                  <div className="flex items-center gap-1 text-xs font-medium pt-2" style={{ color: 'var(--color-forest)' }}>
                    Darajalarni ko'rish <ChevronRight size={13} />
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Yangi fan qo'shish">
        <form onSubmit={handleCreate} className="space-y-4">
          <Input label="Fan nomi" required value={form.nomi} onChange={(e) => setForm({ ...form, nomi: e.target.value })} placeholder="masalan: English" />
          <Input label="Tavsif (ixtiyoriy)" value={form.tavsif} onChange={(e) => setForm({ ...form, tavsif: e.target.value })} placeholder="Qisqacha tavsif" />
          {errorMsg && <div className="text-sm px-3 py-2.5 rounded-xl" style={{ background: '#FBEAE8', color: 'var(--color-red)' }}>{errorMsg}</div>}
          <div className="flex gap-2 pt-2">
            <Button type="submit" loading={saving}>{saving ? 'Saqlanmoqda...' : 'Saqlash'}</Button>
            <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>Bekor qilish</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
