import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  createAdminOquvchi,
  deleteAdminOquvchi,
  getAdminOquvchilar,
  getFanlar,
} from '../../api/admin';
import { Badge, Button, Card, EmptyState, IconButton, Input, Modal, Select, Skeleton } from '../../components/ui';
import { useToast } from '../../context/ToastContext';
import { BarChart3, BookOpen, GraduationCap, KeyRound, Plus, Search, Trash2, UserPlus } from 'lucide-react';
import { cleanLevelName } from '../../utils/course';

const emptyForm = {
  ism: '',
  familya: '',
  username: '',
  password: '',
  fan: '',
  daraja: '',
};

export default function OquvchilarPage() {
  const { showToast } = useToast();
  const navigate = useNavigate();
  const [oquvchilar, setOquvchilar] = useState([]);
  const [fanlar, setFanlar] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [qidiruv, setQidiruv] = useState('');
  const [error, setError] = useState('');
  const [form, setForm] = useState(emptyForm);

  const load = async () => {
    setLoading(true);
    try {
      const [studentsData, subjectsData] = await Promise.all([getAdminOquvchilar(), getFanlar()]);
      setOquvchilar(studentsData.results || studentsData);
      const allSubjects = subjectsData.results || subjectsData;
      const allowed = ['english', 'rus tili', 'koreys tili'];
      setFanlar(allSubjects.filter((fan) => allowed.includes(String(fan.nomi).toLowerCase())));
    } catch {
      showToast("Ma'lumotlarni yuklashda xatolik yuz berdi.", 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const tanlanganFan = fanlar.find((fan) => String(fan.id) === String(form.fan));
  const darajalar = tanlanganFan?.darajalar || [];

  const filtrlangan = useMemo(() => {
    const q = qidiruv.trim().toLowerCase();
    if (!q) return oquvchilar;
    return oquvchilar.filter((student) => (
      `${student.ism} ${student.familya} ${student.username} ${student.fan_nomi} ${student.daraja_nomi}`
        .toLowerCase()
        .includes(q)
    ));
  }, [oquvchilar, qidiruv]);

  const openCreateModal = () => {
    setForm(emptyForm);
    setError('');
    setModalOpen(true);
  };

  const handleFanChange = (fanId) => {
    setForm((current) => ({ ...current, fan: fanId, daraja: '' }));
  };

  const handleCreate = async (event) => {
    event.preventDefault();
    setError('');
    if (!form.fan || !form.daraja) {
      setError('Fan va darajani tanlash majburiy.');
      return;
    }

    setSaving(true);
    try {
      await createAdminOquvchi({
        ism: form.ism,
        familya: form.familya,
        username: form.username,
        password: form.password,
        daraja: Number(form.daraja),
      });
      setModalOpen(false);
      setForm(emptyForm);
      showToast("O'quvchi login, parol, fan va daraja bilan yaratildi.");
      load();
    } catch (err) {
      const data = err.response?.data;
      setError(
        data?.username?.[0]
        || data?.password?.[0]
        || data?.daraja?.[0]
        || data?.detail
        || "O'quvchini yaratishda xatolik yuz berdi."
      );
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (student) => {
    if (!confirm(`${student.ism || student.username} o'quvchisini o'chirasizmi?`)) return;
    try {
      await deleteAdminOquvchi(student.id);
      showToast("O'quvchi o'chirildi.");
      load();
    } catch {
      showToast("O'chirishda xatolik yuz berdi.", 'error');
    }
  };

  return (
    <div className="animate-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="font-display text-2xl font-bold mb-1" style={{ color: 'var(--color-ink)' }}>O'quvchilar</h1>
          <p className="text-sm" style={{ color: '#8A8371' }}>
            Admin o'quvchiga login, parol, fan va boshlang'ich darajani birga beradi.
          </p>
        </div>
        <Button onClick={openCreateModal} className="w-full sm:w-auto">
          <UserPlus size={16} /> O'quvchi yaratish
        </Button>
      </div>

      {oquvchilar.length > 0 && (
        <div className="relative mb-5 max-w-md">
          <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2" style={{ color: '#9C9584' }} />
          <input
            value={qidiruv}
            onChange={(event) => setQidiruv(event.target.value)}
            placeholder="Ism, login, fan yoki daraja..."
            className="w-full pl-10 pr-3.5 py-2.5 rounded-xl border text-sm outline-none"
            style={{ borderColor: 'var(--color-line)' }}
          />
        </div>
      )}

      {loading ? (
        <div className="space-y-3">{[1, 2, 3].map((item) => <Skeleton key={item} className="h-20 w-full" />)}</div>
      ) : filtrlangan.length === 0 ? (
        <Card>
          <EmptyState
            icon={GraduationCap}
            title={oquvchilar.length ? "O'quvchi topilmadi" : "Hozircha o'quvchi yo'q"}
            description={oquvchilar.length ? "Qidiruv so'zini o'zgartiring." : "Birinchi o'quvchini fan va daraja bilan yarating."}
            action={!oquvchilar.length ? <Button onClick={openCreateModal}><Plus size={16} /> Yaratish</Button> : null}
          />
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {filtrlangan.map((student, index) => (
            <Card key={student.id} className="p-5 animate-in-fast" style={{ animationDelay: `${index * 40}ms` }}>
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center font-display font-bold" style={{ background: 'var(--color-paper-warm)', color: 'var(--color-forest)' }}>
                      {(student.ism?.[0] || student.username?.[0] || '?').toUpperCase()}
                    </div>
                    <div className="min-w-0">
                      <p className="font-display font-bold truncate" style={{ color: 'var(--color-ink)' }}>
                        {student.ism} {student.familya}
                      </p>
                      <p className="text-xs flex items-center gap-1" style={{ color: '#8A8371' }}>
                        <KeyRound size={12} /> {student.username}
                      </p>
                    </div>
                  </div>
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge tone="forest"><BookOpen size={11} className="mr-1" />{student.fan_nomi || 'Fan tanlanmagan'}</Badge>
                    <Badge tone="success">{cleanLevelName(student.daraja_nomi) || 'Daraja tanlanmagan'}</Badge>
                  </div>
                </div>
                <IconButton icon={Trash2} tone="danger" title="O'chirish" onClick={() => handleDelete(student)} />
              </div>
              <button
                type="button"
                onClick={() => navigate(`/admin/oquvchilar/${student.id}/progress`)}
                className="mt-4 w-full inline-flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl border text-sm font-semibold transition-all hover:-translate-y-0.5"
                style={{ borderColor: 'var(--color-line)', color: 'var(--color-forest)', background: '#FCFBF7' }}
              >
                <BarChart3 size={16} /> Mavzular va natijalarni ko‘rish
              </button>
            </Card>
          ))}
        </div>
      )}

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Yangi o'quvchi yaratish"
        subtitle="Login, parol, fan va daraja majburiy tanlanadi."
        wide
      >
        <form onSubmit={handleCreate} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Input label="Ism" required value={form.ism} onChange={(event) => setForm({ ...form, ism: event.target.value })} />
            <Input label="Familya" required value={form.familya} onChange={(event) => setForm({ ...form, familya: event.target.value })} />
          </div>
          <Input label="Login" required value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} placeholder="masalan: aziza_01" />
          <Input label="Parol" type="text" required minLength={4} value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} placeholder="O'quvchiga beriladigan parol" />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t" style={{ borderColor: 'var(--color-line)' }}>
            <Select label="Fan" required value={form.fan} onChange={(event) => handleFanChange(event.target.value)}>
              <option value="">Fan tanlang</option>
              {fanlar.filter((fan) => fan.darajalar?.length).map((fan) => (
                <option key={fan.id} value={fan.id}>{fan.nomi}</option>
              ))}
            </Select>
            <Select label="Daraja" required disabled={!form.fan} value={form.daraja} onChange={(event) => setForm({ ...form, daraja: event.target.value })}>
              <option value="">Daraja tanlang</option>
              {darajalar.map((daraja) => <option key={daraja.id} value={daraja.id}>{cleanLevelName(daraja.nomi)}</option>)}
            </Select>
          </div>

          {fanlar.every((fan) => !fan.darajalar?.length) && (
            <p className="text-xs px-3 py-2.5 rounded-xl" style={{ background: 'var(--color-amber-light)', color: '#8A5A1A' }}>
              English, Rus tili va Koreys tili ma'lumotlarini bazaga joylash uchun backendda: py manage.py seed_languages
            </p>
          )}

          {error && <p className="text-sm px-3 py-2.5 rounded-xl" style={{ background: '#FBEAE8', color: 'var(--color-red)' }}>{error}</p>}

          <div className="flex flex-col-reverse sm:flex-row gap-2 pt-2">
            <Button type="button" variant="secondary" onClick={() => setModalOpen(false)} className="sm:flex-1">Bekor qilish</Button>
            <Button type="submit" loading={saving} className="sm:flex-1">{saving ? 'Yaratilmoqda...' : "O'quvchi yaratish"}</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
