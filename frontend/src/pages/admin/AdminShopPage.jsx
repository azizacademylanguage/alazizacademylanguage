import { useEffect, useState } from 'react';
import { getAdminShopMahsulotlari, createShopMahsulot, deleteShopMahsulot } from '../../api/coinShop';
import { Card, Button, Modal, Input, EmptyState, IconButton, Skeleton, Badge } from '../../components/ui';
import { Plus, Trash2, ShoppingBag, Coins } from 'lucide-react';

export default function AdminShopPage() {
  const [mahsulotlar, setMahsulotlar] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ nomi: '', tavsif: '', narx_coin: 50 });

  const load = () => getAdminShopMahsulotlari().then((r) => setMahsulotlar(r.results || r)).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await createShopMahsulot(form);
      setForm({ nomi: '', tavsif: '', narx_coin: 50 });
      setModalOpen(false);
      load();
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm("Mahsulotni o'chirishni tasdiqlaysizmi?")) return;
    await deleteShopMahsulot(id);
    load();
  };

  return (
    <div className="animate-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="font-display text-2xl font-bold mb-1" style={{ color: 'var(--color-ink)' }}>Do'kon boshqaruvi</h1>
          <p className="text-sm" style={{ color: '#8A8371' }}>O'quvchilar coin evaziga sotib oladigan mahsulotlar.</p>
        </div>
        <Button onClick={() => setModalOpen(true)} className="w-full sm:w-auto justify-center"><Plus size={16} /> Mahsulot qo'shish</Button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-36 w-full" />)}</div>
      ) : mahsulotlar.length === 0 ? (
        <Card><EmptyState icon={ShoppingBag} title="Hozircha mahsulot yo'q" description="Birinchi mahsulotni qo'shing." /></Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {mahsulotlar.map((m, idx) => (
            <Card key={m.id} className="animate-in-fast" style={{ animationDelay: `${idx * 50}ms` }}>
              <div className="p-5">
                <div className="flex items-start justify-between mb-3">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'var(--color-paper-warm)' }}>
                    <ShoppingBag size={17} style={{ color: 'var(--color-forest)' }} />
                  </div>
                  <IconButton icon={Trash2} tone="danger" onClick={() => handleDelete(m.id)} />
                </div>
                <p className="font-display font-bold text-sm mb-1" style={{ color: 'var(--color-ink)' }}>{m.nomi}</p>
                {m.tavsif && <p className="text-xs mb-3" style={{ color: '#8A8371' }}>{m.tavsif}</p>}
                <Badge tone="warning"><Coins size={11} className="inline -mt-0.5 mr-1" />{m.narx_coin} coin</Badge>
              </div>
            </Card>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Yangi mahsulot qo'shish">
        <form onSubmit={handleCreate} className="space-y-4">
          <Input label="Mahsulot nomi" required value={form.nomi} onChange={(e) => setForm({ ...form, nomi: e.target.value })} placeholder="masalan: Maxsus avatar" />
          <Input label="Tavsif (ixtiyoriy)" value={form.tavsif} onChange={(e) => setForm({ ...form, tavsif: e.target.value })} />
          <Input label="Narxi (coin)" type="number" required value={form.narx_coin} onChange={(e) => setForm({ ...form, narx_coin: e.target.value })} />
          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={saving}>{saving ? 'Saqlanmoqda...' : 'Saqlash'}</Button>
            <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>Bekor qilish</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
