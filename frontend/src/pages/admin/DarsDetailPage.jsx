import { useEffect, useState, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getDarsBatafsil, uploadDarsMedia, getMashqBatafsil, createSavolTo, createJavobTo, deleteSavolTo } from '../../api/admin_dars';
import { Card, Button, Modal, Input, Select, Badge, EmptyState, IconButton, Skeleton } from '../../components/ui';
import { ChevronLeft, Upload, Plus, Trash2, Video, Music, ListChecks } from 'lucide-react';

export default function DarsDetailPage() {
  const { darsId } = useParams();
  const [dars, setDars] = useState(null);
  const [mashq, setMashq] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState({ video: false, audio: false });
  const videoRef = useRef();
  const audioRef = useRef();

  const [savolModal, setSavolModal] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savolForm, setSavolForm] = useState({
    matn: '', tur: 'single', togri_matn_javob: '',
    javoblar: [{ matn: '', togri: true }, { matn: '', togri: false }],
  });

  const load = async () => {
    const d = await getDarsBatafsil(darsId);
    setDars(d);
    if (d.mashq_id) {
      const m = await getMashqBatafsil(d.mashq_id);
      setMashq(m);
    }
    setLoading(false);
  };

  useEffect(() => { load(); }, [darsId]);

  const handleUpload = async (field, file) => {
    if (!file) return;
    setUploading((u) => ({ ...u, [field]: true }));
    const formData = new FormData();
    formData.append(field, file);
    try {
      await uploadDarsMedia(darsId, formData);
      load();
    } finally {
      setUploading((u) => ({ ...u, [field]: false }));
    }
  };

  const updateJavobField = (idx, key, value) => {
    const copy = [...savolForm.javoblar];
    if (key === 'togri' && savolForm.tur === 'single') {
      copy.forEach((j, i) => { j.togri = i === idx; });
    } else {
      copy[idx][key] = value;
    }
    setSavolForm({ ...savolForm, javoblar: copy });
  };

  const addJavobField = () => setSavolForm({ ...savolForm, javoblar: [...savolForm.javoblar, { matn: '', togri: false }] });
  const removeJavobField = (idx) => setSavolForm({ ...savolForm, javoblar: savolForm.javoblar.filter((_, i) => i !== idx) });

  const handleCreateSavol = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const savol = await createSavolTo({
        mashq: dars.mashq_id,
        matn: savolForm.matn,
        tur: savolForm.tur,
        togri_matn_javob: savolForm.tur === 'text' ? savolForm.togri_matn_javob : '',
        tartib: (mashq?.savollar?.length || 0) + 1,
      });
      if (savolForm.tur !== 'text') {
        for (const j of savolForm.javoblar) {
          if (j.matn.trim()) await createJavobTo({ savol: savol.id, matn: j.matn, togri: j.togri });
        }
      }
      setSavolForm({ matn: '', tur: 'single', togri_matn_javob: '', javoblar: [{ matn: '', togri: true }, { matn: '', togri: false }] });
      setSavolModal(false);
      load();
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteSavol = async (id) => {
    if (!confirm("Savolni o'chirishni tasdiqlaysizmi?")) return;
    await deleteSavolTo(id);
    load();
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-6 w-32" />
        <Skeleton className="h-8 w-64" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Skeleton className="h-48" /><Skeleton className="h-48" />
        </div>
      </div>
    );
  }
  if (!dars) return <p className="text-sm" style={{ color: '#8A8371' }}>Dars topilmadi.</p>;

  const savollarSoni = mashq?.savollar?.length || 0;

  return (
    <div className="animate-in">
      <Link to={`/admin/fanlar`} className="inline-flex items-center gap-1 text-sm mb-4 hover:underline press" style={{ color: 'var(--color-forest)' }}>
        <ChevronLeft size={15} /> Fanlarga qaytish
      </Link>

      <h1 className="font-display text-2xl font-bold mb-1" style={{ color: 'var(--color-ink)' }}>{dars.sarlavha}</h1>
      <p className="text-sm mb-8" style={{ color: '#8A8371' }}>{dars.tushuntirish_matn ? dars.tushuntirish_matn.slice(0, 100) + '...' : 'Tavsif kiritilmagan'}</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <Card className="p-5 animate-in-fast">
          <div className="flex items-center gap-2 mb-3">
            <Video size={16} style={{ color: 'var(--color-forest)' }} />
            <h3 className="font-display font-bold text-sm" style={{ color: 'var(--color-ink)' }}>Video dars</h3>
          </div>
          {dars.video ? (
            <video src={dars.video} controls className="w-full rounded-xl mb-3" style={{ maxHeight: 200 }} />
          ) : (
            <p className="text-xs mb-3" style={{ color: '#8A8371' }}>Video hali yuklanmagan.</p>
          )}
          <input ref={videoRef} type="file" accept="video/*" hidden onChange={(e) => handleUpload('video', e.target.files[0])} />
          <Button variant="secondary" onClick={() => videoRef.current.click()} disabled={uploading.video}>
            <Upload size={14} /> {uploading.video ? 'Yuklanmoqda...' : dars.video ? 'Videoni almashtirish' : 'Video yuklash'}
          </Button>
        </Card>

        <Card className="p-5 animate-in-fast stagger-1">
          <div className="flex items-center gap-2 mb-3">
            <Music size={16} style={{ color: 'var(--color-forest)' }} />
            <h3 className="font-display font-bold text-sm" style={{ color: 'var(--color-ink)' }}>Audio dars</h3>
          </div>
          {dars.audio ? (
            <audio src={dars.audio} controls className="w-full mb-3" />
          ) : (
            <p className="text-xs mb-3" style={{ color: '#8A8371' }}>Audio hali yuklanmagan.</p>
          )}
          <input ref={audioRef} type="file" accept="audio/*" hidden onChange={(e) => handleUpload('audio', e.target.files[0])} />
          <Button variant="secondary" onClick={() => audioRef.current.click()} disabled={uploading.audio}>
            <Upload size={14} /> {uploading.audio ? 'Yuklanmoqda...' : dars.audio ? 'Audioni almashtirish' : 'Audio yuklash'}
          </Button>
        </Card>
      </div>

      <Card className="mb-6 p-5 animate-in-fast stagger-2">
        <h3 className="font-display font-bold text-sm mb-2" style={{ color: 'var(--color-ink)' }}>Misollar</h3>
        <p className="text-sm whitespace-pre-line" style={{ color: '#6B6455' }}>{dars.misollar || 'Kiritilmagan.'}</p>
      </Card>

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div className="flex items-center gap-2 flex-wrap">
          <ListChecks size={16} style={{ color: 'var(--color-forest)' }} />
          <h2 className="font-display font-bold text-base" style={{ color: 'var(--color-ink)' }}>Mashq savollari</h2>
          <Badge tone={savollarSoni >= 40 ? 'success' : 'warning'}>{savollarSoni} / 40</Badge>
        </div>
        <Button onClick={() => setSavolModal(true)} className="w-full sm:w-auto justify-center"><Plus size={16} /> Savol qo'shish</Button>
      </div>

      {savollarSoni === 0 ? (
        <Card><EmptyState icon={ListChecks} title="Hozircha savol yo'q" description="Bu darsga tegishli mashq uchun kamida 40 ta savol qo'shish tavsiya etiladi." /></Card>
      ) : (
        <div className="space-y-2">
          {mashq.savollar.map((s, idx) => (
            <Card key={s.id} className="flex items-start justify-between p-4 animate-in-fast" style={{ animationDelay: `${idx * 25}ms` }}>
              <div className="flex-1">
                <p className="text-sm font-medium mb-1.5" style={{ color: 'var(--color-ink)' }}>{idx + 1}. {s.matn}</p>
                {s.tur === 'text' ? (
                  <Badge tone="neutral">Matn kiritish</Badge>
                ) : (
                  <div className="flex flex-wrap gap-1.5">
                    {s.javoblar.map((j) => (
                      <Badge key={j.id} tone={j.togri ? 'success' : 'neutral'}>{j.matn}</Badge>
                    ))}
                  </div>
                )}
              </div>
              <IconButton icon={Trash2} tone="danger" onClick={() => handleDeleteSavol(s.id)} />
            </Card>
          ))}
        </div>
      )}

      <Modal open={savolModal} onClose={() => setSavolModal(false)} title="Yangi savol qo'shish" wide>
        <form onSubmit={handleCreateSavol} className="space-y-4">
          <Input label="Savol matni" required value={savolForm.matn} onChange={(e) => setSavolForm({ ...savolForm, matn: e.target.value })} placeholder="masalan: She ___ to school every day." />
          <Select label="Savol turi" value={savolForm.tur} onChange={(e) => setSavolForm({ ...savolForm, tur: e.target.value })}>
            <option value="single">Bitta to'g'ri javob</option>
            <option value="multiple">Ko'p to'g'ri javob</option>
            <option value="text">Matn kiritish</option>
          </Select>

          {savolForm.tur === 'text' ? (
            <Input label="To'g'ri javob" required value={savolForm.togri_matn_javob} onChange={(e) => setSavolForm({ ...savolForm, togri_matn_javob: e.target.value })} placeholder="masalan: live" />
          ) : (
            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--color-ink)' }}>Javob variantlari</label>
              <div className="space-y-2">
                {savolForm.javoblar.map((j, idx) => (
                  <div key={idx} className="flex items-center gap-2">
                    <input
                      type={savolForm.tur === 'single' ? 'radio' : 'checkbox'}
                      checked={j.togri}
                      onChange={(e) => updateJavobField(idx, 'togri', e.target.checked)}
                    />
                    <input
                      type="text"
                      value={j.matn}
                      onChange={(e) => updateJavobField(idx, 'matn', e.target.value)}
                      placeholder={`Variant ${idx + 1}`}
                      className="flex-1 px-3 py-1.5 rounded-lg border text-sm"
                      style={{ borderColor: 'var(--color-line)' }}
                    />
                    {savolForm.javoblar.length > 2 && (
                      <IconButton icon={Trash2} tone="danger" onClick={() => removeJavobField(idx)} />
                    )}
                  </div>
                ))}
              </div>
              <button type="button" onClick={addJavobField} className="text-xs font-semibold mt-2 press" style={{ color: 'var(--color-forest)' }}>
                + Variant qo'shish
              </button>
            </div>
          )}

          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={saving}>{saving ? 'Saqlanmoqda...' : 'Saqlash'}</Button>
            <Button type="button" variant="secondary" onClick={() => setSavolModal(false)}>Bekor qilish</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
