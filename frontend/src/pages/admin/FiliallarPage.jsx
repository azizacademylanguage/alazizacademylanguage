import { useEffect, useState } from 'react';
import { getFiliallar, createFilial, deleteFilial } from '../../api/admin';
import { Card, Button, Modal, Input, EmptyState, IconButton, Skeleton } from '../../components/ui';
import { useToast } from '../../context/ToastContext';
import { Plus, Trash2, Building2 } from 'lucide-react';

export default function FiliallarPage() {
  const { showToast } = useToast();
  const [filiallar, setFiliallar] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState({ nomi: '', manzil: '' });
  const [saving, setSaving] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const load = () => getFiliallar().then((r) => setFiliallar(r.results || r)).finally(() => setLoading(false));

  useEffect(() => { load(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setSaving(true);
    setErrorMsg('');
    try {
      await createFilial(form);
      setForm({ nomi: '', manzil: '' });
      setModalOpen(false);
      showToast('Filial qo\'shildi.');
      load();
    } catch (err) {
      setErrorMsg(err.response?.data?.nomi?.[0] || 'Xatolik yuz berdi.');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm("Filialni o'chirishni tasdiqlaysizmi?")) return;
    try {
      await deleteFilial(id);
      showToast('Filial o\'chirildi.');
      load();
    } catch {
      showToast("O'chirishda xatolik yuz berdi.", 'error');
    }
  };

  return (
    <div className="animate-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="font-display text-2xl font-bold mb-1" style={{ color: 'var(--color-ink)' }}>Filiallar</h1>
          <p className="text-sm" style={{ color: '#8A8371' }}>Tashkilotingizning barcha filiallari.</p>
        </div>
        <Button onClick={() => setModalOpen(true)} className="w-full sm:w-auto justify-center">
          <Plus size={16} /> Filial qo'shish
        </Button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-32 w-full" />)}
        </div>
      ) : filiallar.length === 0 ? (
        <Card>
          <EmptyState
            icon={Building2}
            title="Hozircha filial yo'q"
            description="Birinchi filialni qo'shib, nazoratchilar biriktirishni boshlang."
            action={<Button onClick={() => setModalOpen(true)}><Plus size={16} /> Filial qo'shish</Button>}
          />
        </Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filiallar.map((f, idx) => (
            <Card key={f.id} className="animate-in-fast hover-lift" style={{ animationDelay: `${idx * 50}ms` }}>
              <div className="p-5">
                <div className="flex items-start justify-between mb-3">
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center"
                    style={{ background: 'linear-gradient(135deg, var(--color-forest) 0%, var(--color-forest-light) 100%)' }}
                  >
                    <Building2 size={17} color="white" />
                  </div>
                  <IconButton icon={Trash2} tone="danger" onClick={() => handleDelete(f.id)} />
                </div>
                <p className="font-display font-bold text-sm mb-0.5" style={{ color: 'var(--color-ink)' }}>{f.nomi}</p>
                {f.manzil && <p className="text-xs mb-3" style={{ color: '#8A8371' }}>{f.manzil}</p>}
                <div className="flex gap-4 text-xs pt-3 border-t" style={{ borderColor: 'var(--color-line)', color: '#8A8371' }}>
                  <span>{f.nazoratchilar_soni} nazoratchi</span>
                  <span>{f.oquvchilar_soni} o'quvchi</span>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Yangi filial qo'shish">
        <form onSubmit={handleCreate} className="space-y-4">
          <Input label="Filial nomi" required value={form.nomi} onChange={(e) => setForm({ ...form, nomi: e.target.value })} placeholder="masalan: Chilonzor filiali" />
          <Input label="Manzil (ixtiyoriy)" value={form.manzil} onChange={(e) => setForm({ ...form, manzil: e.target.value })} placeholder="Toshkent, Chilonzor tumani" />
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
