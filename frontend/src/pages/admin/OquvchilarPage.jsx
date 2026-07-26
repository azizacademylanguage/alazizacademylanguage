import { useEffect, useMemo, useState } from 'react';
import {
  createAdminOquvchi,
  deleteAdminOquvchi,
  getAdminOquvchilar,
  updateAdminOquvchi,
  getFanlar,
} from '../../api/admin';
import { Badge, Button, Card, EmptyState, IconButton, Input, Modal, Select, Skeleton } from '../../components/ui';
import { useToast } from '../../context/ToastContext';
import { BookOpen, CheckCircle2, GraduationCap, KeyRound, Plus, Search, Trash2, UserPlus } from 'lucide-react';
import { cleanLevelName } from '../../utils/course';


const firstErrorMessage = (data) => {
  if (!data) return '';
  if (typeof data === 'string') return data;
  if (Array.isArray(data)) return firstErrorMessage(data[0]);
  if (typeof data === 'object') {
    for (const value of Object.values(data)) {
      const message = firstErrorMessage(value);
      if (message) return message;
    }
  }
  return '';
};


const addOneMonth = (isoDate) => {
  if (!isoDate) return '';
  const [year, month, day] = isoDate.split('-').map(Number);
  const targetMonth = month === 12 ? 1 : month + 1;
  const targetYear = month === 12 ? year + 1 : year;
  const lastDay = new Date(targetYear, targetMonth, 0).getDate();
  const safeDay = Math.min(day, lastDay);
  return `${targetYear}-${String(targetMonth).padStart(2, '0')}-${String(safeDay).padStart(2, '0')}`;
};

const now = new Date();
const today = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 10);

const emptyForm = {
  ism: '',
  familya: '',
  username: '',
  password: '',
  fan: '',
  daraja: '',
  boshlanish_sana: today,
  tugash_sana: addOneMonth(today),
  tolov_holati: 'tolangan',
  muddat_bloklash: true,
};

export default function OquvchilarPage() {
  const { showToast } = useToast();
  const [oquvchilar, setOquvchilar] = useState([]);
  const [fanlar, setFanlar] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [payingId, setPayingId] = useState(null);
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
      setFanlar(allSubjects);
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
    if (!form.password) {
      setError('Parol majburiy.');
      return;
    }
    if (form.username.trim().toLowerCase() === form.password.trim().toLowerCase()) {
      setError("Parol login bilan bir xil bo'lishi mumkin emas.");
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
        boshlanish_sana: form.boshlanish_sana || null,
        tugash_sana: form.tugash_sana || null,
        tolov_holati: form.tolov_holati,
        muddat_bloklash: form.muddat_bloklash,
      });
      setModalOpen(false);
      setForm(emptyForm);
      showToast("O'quvchi login, parol, fan va daraja bilan yaratildi.");
      load();
    } catch (err) {
      const data = err.response?.data;
      const status = err.response?.status;
      setError(
        firstErrorMessage(data)
        || (status === 500
          ? "Server bazasida xatolik bor. Yangi backend versiyasini Railway'ga deploy qiling."
          : "O'quvchini yaratishda xatolik yuz berdi.")
      );
    } finally {
      setSaving(false);
    }
  };


  const handleMarkPaid = async (student) => {
    setPayingId(student.id);
    try {
      await updateAdminOquvchi(student.id, { tolov_holati: 'tolangan' });
      showToast(`${student.ism || student.username} uchun to'lov holati "To'langan" qilindi.`);
      await load();
    } catch (err) {
      showToast(firstErrorMessage(err.response?.data) || "To'lov holatini yangilashda xatolik yuz berdi.", 'error');
    } finally {
      setPayingId(null);
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
                    <Badge tone={student.obuna_holati === 'faol' ? 'success' : student.obuna_holati === 'tugamoqda' ? 'warning' : 'danger'}>{student.obuna_holati || 'faol'}{student.qolgan_kun !== null && student.qolgan_kun !== undefined ? ` · ${student.qolgan_kun} kun` : ''}</Badge>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row items-end sm:items-center gap-2">
                  {student.tolov_holati !== 'tolangan' && (
                    <Button size="sm" onClick={() => handleMarkPaid(student)} loading={payingId === student.id}>
                      <CheckCircle2 size={14} /> To'landi
                    </Button>
                  )}
                  <IconButton icon={Trash2} tone="danger" title="O'chirish" onClick={() => handleDelete(student)} />
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Yangi o'quvchi yaratish"
        subtitle="Ism-familiya takrorlanishi mumkin. Login noyob. Login va parolni admin alohida belgilaydi."
        wide
      >
        <form onSubmit={handleCreate} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Input label="Ism" required value={form.ism} onChange={(event) => setForm({ ...form, ism: event.target.value })} />
            <Input label="Familya" required value={form.familya} onChange={(event) => setForm({ ...form, familya: event.target.value })} />
          </div>
          <Input label="Login" required value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} placeholder="masalan: aziza_01" />
          <Input label="Parol" type="text" required minLength={4} value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} placeholder="Login bilan bir xil bo‘lmagan parol" />

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


          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t" style={{ borderColor: 'var(--color-line)' }}>
            <div className="rounded-xl border px-3.5 py-2.5" style={{ borderColor: 'var(--color-line)', background: 'var(--color-paper-warm)' }}>
              <p className="text-xs mb-1" style={{ color: 'var(--color-muted)' }}>Tarif</p>
              <p className="text-sm font-semibold" style={{ color: 'var(--color-ink)' }}>Yagona tarif</p>
            </div>
            <Select label="To'lov holati" value={form.tolov_holati} onChange={(event) => setForm({ ...form, tolov_holati: event.target.value })}>
              <option value="tolangan">To'langan</option>
              <option value="tolanmagan">To'lanmagan</option>
            </Select>
            <Input type="date" label="Boshlanish sanasi" value={form.boshlanish_sana} onChange={(event) => { const value = event.target.value; setForm({ ...form, boshlanish_sana: value, tugash_sana: addOneMonth(value) }); }} />
            <Input type="date" label="Tugash sanasi" value={form.tugash_sana} onChange={(event) => setForm({ ...form, tugash_sana: event.target.value })} />
          </div>
          <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={form.muddat_bloklash} onChange={(event) => setForm({ ...form, muddat_bloklash: event.target.checked })} /> Muddat tugaganda darslarni qulflash</label>

          {fanlar.every((fan) => !fan.darajalar?.length) && (
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 px-3 py-2.5 rounded-xl" style={{ background: 'var(--color-amber-light)', color: '#8A5A1A' }}>
              <p className="text-xs">Fanlar hali backenddan kelmadi. Railway yangi deployni tugatgach ro'yxatni qayta yuklang.</p>
              <button type="button" onClick={load} className="text-xs font-semibold underline underline-offset-2 shrink-0">Qayta yuklash</button>
            </div>
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
