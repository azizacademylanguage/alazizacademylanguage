import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getOquvchilar, createOquvchi, deleteOquvchi, biriktirFan, getFanlarRoyxati } from '../../api/nazoratchi';
import { Card, Button, Modal, Input, Select, Badge, EmptyState, IconButton, Skeleton } from '../../components/ui';
import { useToast } from '../../context/ToastContext';
import { Plus, Trash2, ChevronRight, BookPlus, Users, Sparkles, Search } from 'lucide-react';

export default function OquvchilarPage() {
  const { showToast } = useToast();
  const [oquvchilar, setOquvchilar] = useState([]);
  const [fanlar, setFanlar] = useState([]);
  const [loading, setLoading] = useState(true);
  const [qidiruv, setQidiruv] = useState('');

  const [modalOpen, setModalOpen] = useState(false);
  const [fanModal, setFanModal] = useState({ open: false, oquvchi: null });
  const [saving, setSaving] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [fanErrorMsg, setFanErrorMsg] = useState('');
  const [form, setForm] = useState({ username: '', password: '', ism: '', familya: '', daraja: '' });
  const [selectedDaraja, setSelectedDaraja] = useState('');

  const load = () => {
    setLoading(true);
    Promise.all([getOquvchilar(), getFanlarRoyxati()])
      .then(([o, f]) => {
        setOquvchilar(o.results || o);
        setFanlar(f.results || f);
      })
      .catch(() => showToast("Ma'lumotlarni yuklashda xatolik yuz berdi.", 'error'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const filtrlangan = oquvchilar.filter((o) => {
    const q = qidiruv.toLowerCase();
    return `${o.ism} ${o.familya} ${o.username}`.toLowerCase().includes(q);
  });

  const handleCreate = async (e) => {
    e.preventDefault();
    setSaving(true);
    setErrorMsg('');
    try {
      const { daraja, ...oquvchiData } = form;
      const yangiOquvchi = await createOquvchi(oquvchiData);
      if (daraja) {
        await biriktirFan(yangiOquvchi.id, daraja);
      }
      setForm({ username: '', password: '', ism: '', familya: '', daraja: '' });
      setModalOpen(false);
      showToast("O'quvchi muvaffaqiyatli qo'shildi.");
      load();
    } catch (err) {
      setErrorMsg(
        err.response?.data?.username?.[0]
        || err.response?.data?.detail
        || "Xatolik yuz berdi. Iltimos qayta urinib ko'ring."
      );
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm("O'quvchini o'chirishni tasdiqlaysizmi?")) return;
    try {
      await deleteOquvchi(id);
      showToast("O'quvchi o'chirildi.");
      load();
    } catch {
      showToast("O'chirishda xatolik yuz berdi.", 'error');
    }
  };

  const openFanModal = (oquvchi) => {
    setFanErrorMsg('');
    setSelectedDaraja('');
    setFanModal({ open: true, oquvchi });
  };

  const handleBiriktir = async (e) => {
    e.preventDefault();
    setFanErrorMsg('');

    if (!selectedDaraja) {
      setFanErrorMsg('Iltimos, fan va darajani tanlang.');
      return;
    }

    setSaving(true);
    try {
      await biriktirFan(fanModal.oquvchi.id, selectedDaraja);
      setFanModal({ open: false, oquvchi: null });
      setSelectedDaraja('');
      showToast('Fan muvaffaqiyatli biriktirildi.');
      load();
    } catch (err) {
      setFanErrorMsg(err.response?.data?.detail || 'Fan biriktirishda xatolik yuz berdi.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="animate-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="font-display text-2xl font-bold mb-1" style={{ color: 'var(--color-ink)' }}>O'quvchilarim</h1>
          <p className="text-sm" style={{ color: '#8A8371' }}>Siz yaratgan barcha o'quvchilar.</p>
        </div>
        <Button onClick={() => setModalOpen(true)} className="w-full sm:w-auto justify-center">
          <Plus size={16} /> O'quvchi qo'shish
        </Button>
      </div>

      {oquvchilar.length > 0 && (
        <div className="relative mb-6 max-w-sm">
          <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2" style={{ color: '#9C9584' }} />
          <input
            value={qidiruv}
            onChange={(e) => setQidiruv(e.target.value)}
            placeholder="Ism yoki login bo'yicha qidirish..."
            className="w-full pl-10 pr-3.5 py-2.5 rounded-xl border text-sm outline-none transition-all"
            style={{ borderColor: 'var(--color-line)' }}
          />
        </div>
      )}

      {loading ? (
        <div className="space-y-2">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-14 w-full" />)}
        </div>
      ) : oquvchilar.length === 0 ? (
        <Card>
          <EmptyState
            icon={Users}
            title="Hozircha o'quvchi yo'q"
            description="Birinchi o'quvchini qo'shing — unga darhol fan va daraja ham biriktirishingiz mumkin."
            action={<Button onClick={() => setModalOpen(true)}><Plus size={16} /> O'quvchi qo'shish</Button>}
          />
        </Card>
      ) : filtrlangan.length === 0 ? (
        <Card><EmptyState icon={Search} title="Hech narsa topilmadi" description="Boshqa kalit so'z bilan qidirib ko'ring." /></Card>
      ) : (
        <Card className="p-0 overflow-hidden">
          <div className="hidden sm:block overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left border-b" style={{ borderColor: 'var(--color-line)' }}>
                  <th className="py-3 px-5 font-medium" style={{ color: '#8A8371' }}>Ism familya</th>
                  <th className="py-3 px-5 font-medium" style={{ color: '#8A8371' }}>Login</th>
                  <th className="py-3 px-5"></th>
                </tr>
              </thead>
              <tbody>
                {filtrlangan.map((o, idx) => (
                  <tr
                    key={o.id}
                    className="border-b last:border-0 animate-in-fast hover:bg-[var(--color-paper-warm)]/40 transition-colors"
                    style={{ borderColor: 'var(--color-line)', animationDelay: `${idx * 30}ms` }}
                  >
                    <td className="py-3 px-5">
                      <Link to={`/nazoratchi/oquvchilar/${o.id}`} className="flex items-center gap-2.5 font-medium hover:underline" style={{ color: 'var(--color-ink)' }}>
                        <div className="w-8 h-8 rounded-full flex items-center justify-center font-display font-bold text-xs" style={{ background: 'var(--color-paper-warm)', color: 'var(--color-forest)' }}>
                          {o.ism?.[0]?.toUpperCase() || '?'}
                        </div>
                        {o.ism} {o.familya}
                      </Link>
                    </td>
                    <td className="py-3 px-5" style={{ color: '#8A8371' }}>{o.username}</td>
                    <td className="py-3 px-5 text-right">
                      <div className="flex items-center justify-end gap-3">
                        <button
                          type="button"
                          onClick={() => openFanModal(o)}
                          className="text-xs font-semibold flex items-center gap-1 press"
                          style={{ color: 'var(--color-forest)' }}
                        >
                          <BookPlus size={13} /> Fan biriktirish
                        </button>
                        <Link to={`/nazoratchi/oquvchilar/${o.id}`}><ChevronRight size={15} className="text-gray-300" /></Link>
                        <IconButton icon={Trash2} tone="danger" onClick={() => handleDelete(o.id)} />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="sm:hidden divide-y" style={{ borderColor: 'var(--color-line)' }}>
            {filtrlangan.map((o, idx) => (
              <div key={o.id} className="p-4 animate-in-fast" style={{ animationDelay: `${idx * 30}ms` }}>
                <div className="flex items-center justify-between mb-2">
                  <Link to={`/nazoratchi/oquvchilar/${o.id}`} className="flex items-center gap-2.5 font-medium" style={{ color: 'var(--color-ink)' }}>
                    <div className="w-8 h-8 rounded-full flex items-center justify-center font-display font-bold text-xs" style={{ background: 'var(--color-paper-warm)', color: 'var(--color-forest)' }}>
                      {o.ism?.[0]?.toUpperCase() || '?'}
                    </div>
                    <div>
                      <p>{o.ism} {o.familya}</p>
                      <p className="text-xs font-normal" style={{ color: '#8A8371' }}>{o.username}</p>
                    </div>
                  </Link>
                  <IconButton icon={Trash2} tone="danger" onClick={() => handleDelete(o.id)} />
                </div>
                <button type="button" onClick={() => openFanModal(o)} className="text-xs font-semibold flex items-center gap-1 press mt-2" style={{ color: 'var(--color-forest)' }}>
                  <BookPlus size={13} /> Fan biriktirish
                </button>
              </div>
            ))}
          </div>
        </Card>
      )}

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Yangi o'quvchi qo'shish"
        subtitle="Login ma'lumotlari va (ixtiyoriy) fan/daraja birga biriktiriladi."
        wide
      >
        <form onSubmit={handleCreate} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <Input label="Ism" required value={form.ism} onChange={(e) => setForm({ ...form, ism: e.target.value })} />
            <Input label="Familya" required value={form.familya} onChange={(e) => setForm({ ...form, familya: e.target.value })} />
          </div>
          <Input label="Login" required value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} placeholder="masalan: oquvchi_malika" />
          <Input label="Parol" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="Kamida 8 belgi" />

          <div className="pt-1 border-t" style={{ borderColor: 'var(--color-line)' }}>
            <div className="flex items-center gap-1.5 mt-4 mb-2">
              <Sparkles size={14} style={{ color: 'var(--color-amber)' }} />
              <p className="text-sm font-semibold" style={{ color: 'var(--color-ink)' }}>Fan va daraja (ixtiyoriy)</p>
            </div>
            {fanlar.every((f) => !f.darajalar?.length) ? (
              <p className="text-xs px-3 py-2 rounded-xl" style={{ background: 'var(--color-amber-light)', color: '#8A5A1A' }}>
                Hozircha hech qaysi fanga daraja qo'shilmagan. Admin bilan bog'lanib, avval daraja (masalan Beginner) qo'shdiring.
              </p>
            ) : (
              <Select value={form.daraja} onChange={(e) => setForm({ ...form, daraja: e.target.value })}>
                <option value="">Keyinroq biriktiraman</option>
                {fanlar.filter((fan) => fan.darajalar?.length > 0).map((fan) => (
                  <optgroup key={fan.id} label={fan.nomi}>
                    {fan.darajalar?.map((d) => (
                      <option key={d.id} value={d.id}>{d.nomi}</option>
                    ))}
                  </optgroup>
                ))}
              </Select>
            )}
          </div>

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

      <Modal
        open={fanModal.open}
        onClose={() => setFanModal({ open: false, oquvchi: null })}
        title={`${fanModal.oquvchi?.ism || ''} ${fanModal.oquvchi?.familya || ''}ga fan biriktirish`}
      >
        {fanlar.every((f) => !f.darajalar?.length) ? (
          <div>
            <p className="text-sm px-3 py-2.5 rounded-xl mb-4" style={{ background: 'var(--color-amber-light)', color: '#8A5A1A' }}>
              Hozircha hech qaysi fanga daraja qo'shilmagan. Admin bilan bog'lanib, avval daraja (masalan Beginner) qo'shdiring.
            </p>
            <Button type="button" variant="secondary" onClick={() => setFanModal({ open: false, oquvchi: null })}>Yopish</Button>
          </div>
        ) : (
          <form onSubmit={handleBiriktir} className="space-y-4">
            <Select label="Fan va daraja" required value={selectedDaraja} onChange={(e) => setSelectedDaraja(e.target.value)} error={fanErrorMsg}>
              <option value="">Tanlang</option>
              {fanlar.filter((fan) => fan.darajalar?.length > 0).map((fan) => (
                <optgroup key={fan.id} label={fan.nomi}>
                  {fan.darajalar?.map((d) => (
                    <option key={d.id} value={d.id}>{d.nomi}</option>
                  ))}
                </optgroup>
              ))}
            </Select>

            <div className="flex gap-2 pt-2">
              <Button type="submit" loading={saving}>{saving ? 'Biriktirilmoqda...' : 'Biriktirish'}</Button>
              <Button type="button" variant="secondary" onClick={() => setFanModal({ open: false, oquvchi: null })}>Bekor qilish</Button>
            </div>
          </form>
        )}
      </Modal>
    </div>
  );
}
