import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  getGateTestlar, createGateTest, getGateTestBatafsil, createGateTestSavol, createGateTestJavob, deleteGateTestSavol,
  getFinalTestlar, createFinalTest, getFinalTestBatafsil, createFinalTestSavol, createFinalTestJavob, deleteFinalTestSavol,
} from '../../api/adminExtra';
import { Card, Button, Modal, Input, Select, Badge, EmptyState, IconButton, Skeleton } from '../../components/ui';
import { ChevronLeft, Plus, Trash2, ShieldCheck, Trophy } from 'lucide-react';

function TestBlok({ turi, daraja, test, onYaratildi, onSavolQoshildi }) {
  const isGate = turi === 'gate';
  const [savolModal, setSavolModal] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    matn: '', javoblar: [{ matn: '', togri: true }, { matn: '', togri: false }],
  });

  const updateJavob = (idx, key, value) => {
    const copy = [...form.javoblar];
    if (key === 'togri') copy.forEach((j, i) => { j.togri = i === idx; });
    else copy[idx][key] = value;
    setForm({ ...form, javoblar: copy });
  };
  const addJavob = () => setForm({ ...form, javoblar: [...form.javoblar, { matn: '', togri: false }] });
  const removeJavob = (idx) => setForm({ ...form, javoblar: form.javoblar.filter((_, i) => i !== idx) });

  const handleCreateTest = async () => {
    if (isGate) await createGateTest({ daraja: daraja.id, sarlavha: `${daraja.nomi} - Gate Test` });
    else await createFinalTest({ daraja: daraja.id, sarlavha: `${daraja.nomi} - Yakuniy test`, otish_bali_foiz: 70 });
    onYaratildi();
  };

  const handleCreateSavol = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const savol = isGate
        ? await createGateTestSavol({ gate_test: test.id, matn: form.matn, tartib: (test.savollar?.length || 0) + 1 })
        : await createFinalTestSavol({ final_test: test.id, matn: form.matn, tartib: (test.savollar?.length || 0) + 1 });

      for (const j of form.javoblar) {
        if (j.matn.trim()) {
          if (isGate) await createGateTestJavob({ savol: savol.id, matn: j.matn, togri: j.togri });
          else await createFinalTestJavob({ savol: savol.id, matn: j.matn, togri: j.togri });
        }
      }
      setForm({ matn: '', javoblar: [{ matn: '', togri: true }, { matn: '', togri: false }] });
      setSavolModal(false);
      onSavolQoshildi();
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteSavol = async (id) => {
    if (!confirm("Savolni o'chirishni tasdiqlaysizmi?")) return;
    if (isGate) await deleteGateTestSavol(id);
    else await deleteFinalTestSavol(id);
    onSavolQoshildi();
  };

  return (
    <Card className="p-5">
      <div className="flex items-center gap-2 mb-1">
        {isGate ? <ShieldCheck size={16} style={{ color: 'var(--color-forest)' }} /> : <Trophy size={16} style={{ color: 'var(--color-amber)' }} />}
        <h3 className="font-display font-bold text-sm" style={{ color: 'var(--color-ink)' }}>
          {isGate ? 'Gate Test' : 'Final Test'}
        </h3>
      </div>
      <p className="text-xs mb-4" style={{ color: '#8A8371' }}>
        {isGate
          ? "Keyingi darajaga o'tish uchun kirish testi."
          : "Darajani to'liq tugatgach yakuniy test, o'tsa sertifikat beriladi."}
      </p>

      {!test ? (
        <Button size="sm" onClick={handleCreateTest}>
          <Plus size={14} /> {isGate ? 'Gate Test' : 'Final Test'} yaratish
        </Button>
      ) : (
        <>
          <div className="flex items-center justify-between mb-3">
            <Badge tone={test.savollar?.length >= 5 ? 'success' : 'warning'}>{test.savollar?.length || 0} ta savol</Badge>
            <Button size="sm" variant="secondary" onClick={() => setSavolModal(true)}>
              <Plus size={13} /> Savol qo'shish
            </Button>
          </div>

          {test.savollar?.length > 0 && (
            <div className="space-y-1.5">
              {test.savollar.map((s, idx) => (
                <div key={s.id} className="flex items-start justify-between px-3 py-2 rounded-lg text-xs" style={{ background: 'var(--color-paper-warm)' }}>
                  <div className="flex-1">
                    <p className="font-medium mb-1" style={{ color: 'var(--color-ink)' }}>{idx + 1}. {s.matn}</p>
                    <div className="flex flex-wrap gap-1">
                      {s.javoblar?.map((j) => <Badge key={j.id} tone={j.togri ? 'success' : 'neutral'}>{j.matn}</Badge>)}
                    </div>
                  </div>
                  <IconButton icon={Trash2} tone="danger" size={12} onClick={() => handleDeleteSavol(s.id)} />
                </div>
              ))}
            </div>
          )}
        </>
      )}

      <Modal open={savolModal} onClose={() => setSavolModal(false)} title="Yangi savol qo'shish">
        <form onSubmit={handleCreateSavol} className="space-y-4">
          <Input label="Savol matni" required value={form.matn} onChange={(e) => setForm({ ...form, matn: e.target.value })} />
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--color-ink)' }}>Javob variantlari</label>
            <div className="space-y-2">
              {form.javoblar.map((j, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <input type="radio" checked={j.togri} onChange={(e) => updateJavob(idx, 'togri', e.target.checked)} />
                  <input
                    type="text" value={j.matn} onChange={(e) => updateJavob(idx, 'matn', e.target.value)}
                    placeholder={`Variant ${idx + 1}`} className="flex-1 px-3 py-1.5 rounded-lg border text-sm"
                    style={{ borderColor: 'var(--color-line)' }}
                  />
                  {form.javoblar.length > 2 && <IconButton icon={Trash2} tone="danger" onClick={() => removeJavob(idx)} />}
                </div>
              ))}
            </div>
            <button type="button" onClick={addJavob} className="text-xs font-semibold mt-2 press" style={{ color: 'var(--color-forest)' }}>
              + Variant qo'shish
            </button>
          </div>
          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={saving}>{saving ? 'Saqlanmoqda...' : 'Saqlash'}</Button>
            <Button type="button" variant="secondary" onClick={() => setSavolModal(false)}>Bekor qilish</Button>
          </div>
        </form>
      </Modal>
    </Card>
  );
}

export default function DarajaTestlarPage() {
  const { darajaId } = useParams();
  const [daraja, setDaraja] = useState({ id: darajaId, nomi: '...' });
  const [gateTest, setGateTest] = useState(null);
  const [finalTest, setFinalTest] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    const gateTestlar = await getGateTestlar();
    const gt = (gateTestlar.results || gateTestlar).find((g) => String(g.daraja) === String(darajaId));
    if (gt) {
      const full = await getGateTestBatafsil(gt.id);
      setGateTest(full);
      setDaraja({ id: darajaId, nomi: full.daraja_nomi });
    } else {
      setGateTest(null);
    }

    const finalTestlar = await getFinalTestlar();
    const ft = (finalTestlar.results || finalTestlar).find((f) => String(f.daraja) === String(darajaId));
    if (ft) {
      const full = await getFinalTestBatafsil(ft.id);
      setFinalTest(full);
      setDaraja({ id: darajaId, nomi: full.daraja_nomi });
    } else {
      setFinalTest(null);
    }
    setLoading(false);
  };

  useEffect(() => { load(); }, [darajaId]);

  if (loading) {
    return (
      <div className="space-y-4 max-w-2xl">
        <Skeleton className="h-6 w-32" />
        <Skeleton className="h-48 w-full" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  return (
    <div className="animate-in max-w-2xl">
      <Link to="/admin/fanlar" className="inline-flex items-center gap-1 text-sm mb-4 hover:underline press" style={{ color: 'var(--color-forest)' }}>
        <ChevronLeft size={15} /> Fanlarga qaytish
      </Link>

      <h1 className="font-display text-2xl font-bold mb-1" style={{ color: 'var(--color-ink)' }}>{daraja.nomi} — Testlar</h1>
      <p className="text-sm mb-8" style={{ color: '#8A8371' }}>Gate Test va Final Test savollarini shu yerdan boshqaring.</p>

      <div className="space-y-4">
        <TestBlok turi="gate" daraja={daraja} test={gateTest} onYaratildi={load} onSavolQoshildi={load} />
        <TestBlok turi="final" daraja={daraja} test={finalTest} onYaratildi={load} onSavolQoshildi={load} />
      </div>
    </div>
  );
}
