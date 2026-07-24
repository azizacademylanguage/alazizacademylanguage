import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  getFan, createDaraja, deleteDaraja, createMavzu, deleteMavzu,
  createDars, deleteDars, createMashq
} from '../../api/admin';
import { Card, Button, Modal, Input, EmptyState, IconButton, Skeleton } from '../../components/ui';
import { Plus, Trash2, ChevronLeft, ChevronDown, ChevronUp, Layers, FileText, ListChecks, ShieldCheck } from 'lucide-react';

export default function FanDetailPage() {
  const { fanId } = useParams();
  const navigate = useNavigate();
  const [fan, setFan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [openDaraja, setOpenDaraja] = useState(null);
  const [openMavzu, setOpenMavzu] = useState(null);

  const [darajaModal, setDarajaModal] = useState(false);
  const [mavzuModal, setMavzuModal] = useState({ open: false, darajaId: null });
  const [darsModal, setDarsModal] = useState({ open: false, mavzuId: null });

  const [darajaForm, setDarajaForm] = useState({ nomi: '', tartib: 0 });
  const [mavzuForm, setMavzuForm] = useState({ nomi: '', tartib: 0 });
  const [darsForm, setDarsForm] = useState({ sarlavha: '', tushuntirish_matn: '', misollar: '', tartib: 0 });
  const [saving, setSaving] = useState(false);

  const load = () => getFan(fanId).then(setFan).finally(() => setLoading(false));
  useEffect(() => { load(); }, [fanId]);

  const handleCreateDaraja = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await createDaraja({ ...darajaForm, fan: fanId });
      setDarajaForm({ nomi: '', tartib: 0 });
      setDarajaModal(false);
      load();
    } finally { setSaving(false); }
  };

  const handleCreateMavzu = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await createMavzu({ ...mavzuForm, daraja: mavzuModal.darajaId });
      setMavzuForm({ nomi: '', tartib: 0 });
      setMavzuModal({ open: false, darajaId: null });
      load();
    } finally { setSaving(false); }
  };

  const handleCreateDars = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const dars = await createDars({ ...darsForm, mavzu: darsModal.mavzuId });
      await createMashq({ dars: dars.id, sarlavha: `${darsForm.sarlavha} - Mashq`, otish_bali_foiz: 80 });
      setDarsForm({ sarlavha: '', tushuntirish_matn: '', misollar: '', tartib: 0 });
      setDarsModal({ open: false, mavzuId: null });
      load();
    } finally { setSaving(false); }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-6 w-32" />
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-20 w-full" />
      </div>
    );
  }
  if (!fan) return <p className="text-sm" style={{ color: '#8A8371' }}>Fan topilmadi.</p>;

  return (
    <div className="animate-in">
      <Link to="/admin/fanlar" className="inline-flex items-center gap-1 text-sm mb-4 hover:underline press" style={{ color: 'var(--color-forest)' }}>
        <ChevronLeft size={15} /> Fanlarga qaytish
      </Link>

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="font-display text-2xl font-bold mb-1" style={{ color: 'var(--color-ink)' }}>{fan.nomi}</h1>
          <p className="text-sm" style={{ color: '#8A8371' }}>{fan.darajalar?.length || 0} ta daraja</p>
        </div>
        <Button onClick={() => setDarajaModal(true)} className="w-full sm:w-auto justify-center"><Plus size={16} /> Daraja qo'shish</Button>
      </div>

      {fan.darajalar?.length === 0 ? (
        <Card><EmptyState icon={Layers} title="Hozircha daraja yo'q" description="Masalan: Beginner, Intermediate, Advanced." /></Card>
      ) : (
        <div className="space-y-3">
          {fan.darajalar.map((daraja, idx) => (
            <Card key={daraja.id} className="p-0 overflow-hidden animate-in-fast" style={{ animationDelay: `${idx * 50}ms` }}>
              <button
                onClick={() => setOpenDaraja(openDaraja === daraja.id ? null : daraja.id)}
                className="w-full flex items-center justify-between px-5 py-4 text-left transition-colors hover:bg-[var(--color-paper-warm)]/40"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: 'var(--color-paper-warm)' }}>
                    <Layers size={15} style={{ color: 'var(--color-forest)' }} />
                  </div>
                  <div>
                    <p className="font-display font-bold text-sm" style={{ color: 'var(--color-ink)' }}>{daraja.nomi}</p>
                    <p className="text-xs" style={{ color: '#8A8371' }}>{daraja.mavzular?.length || 0} ta mavzu</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <IconButton
                    icon={Trash2} tone="danger"
                    onClick={async (e) => {
                      e.stopPropagation();
                      if (confirm("Darajani o'chirishni tasdiqlaysizmi?")) { await deleteDaraja(daraja.id); load(); }
                    }}
                  />
                  <ChevronDown size={16} className="transition-transform" style={{ transform: openDaraja === daraja.id ? 'rotate(180deg)' : 'none' }} />
                </div>
              </button>

              {openDaraja === daraja.id && (
                <div className="px-5 pb-5 border-t animate-fade" style={{ borderColor: 'var(--color-line)' }}>
                  <div className="flex flex-wrap justify-end gap-2 pt-4 mb-2">
                    <Link to={`/admin/darajalar/${daraja.id}/testlar`}>
                      <Button variant="ghost" size="sm"><ShieldCheck size={14} /> Gate/Final Test</Button>
                    </Link>
                    <Button variant="secondary" size="sm" onClick={() => setMavzuModal({ open: true, darajaId: daraja.id })}>
                      <Plus size={14} /> Mavzu qo'shish
                    </Button>
                  </div>

                  {daraja.mavzular?.length === 0 ? (
                    <p className="text-sm py-6 text-center" style={{ color: '#8A8371' }}>Hozircha mavzu yo'q.</p>
                  ) : (
                    <div className="space-y-2">
                      {daraja.mavzular.map((mavzu) => (
                        <div key={mavzu.id} className="rounded-xl border" style={{ borderColor: 'var(--color-line)' }}>
                          <button
                            onClick={() => setOpenMavzu(openMavzu === mavzu.id ? null : mavzu.id)}
                            className="w-full flex items-center justify-between px-4 py-3 text-left"
                          >
                            <div className="flex items-center gap-2.5">
                              <FileText size={14} style={{ color: 'var(--color-forest-light)' }} />
                              <span className="text-sm font-medium" style={{ color: 'var(--color-ink)' }}>{mavzu.nomi}</span>
                              <span className="text-xs" style={{ color: '#8A8371' }}>({mavzu.darslar?.length || 0} dars)</span>
                            </div>
                            <div className="flex items-center gap-3">
                              <IconButton
                                icon={Trash2} tone="danger" size={13}
                                onClick={async (e) => {
                                  e.stopPropagation();
                                  if (confirm("Mavzuni o'chirishni tasdiqlaysizmi?")) { await deleteMavzu(mavzu.id); load(); }
                                }}
                              />
                              <ChevronDown size={14} className="transition-transform" style={{ transform: openMavzu === mavzu.id ? 'rotate(180deg)' : 'none' }} />
                            </div>
                          </button>

                          {openMavzu === mavzu.id && (
                            <div className="px-4 pb-4 border-t animate-fade" style={{ borderColor: 'var(--color-line)' }}>
                              <div className="flex justify-end pt-3 mb-2">
                                <button
                                  onClick={() => setDarsModal({ open: true, mavzuId: mavzu.id })}
                                  className="text-xs font-semibold flex items-center gap-1 press"
                                  style={{ color: 'var(--color-forest)' }}
                                >
                                  <Plus size={13} /> Dars qo'shish
                                </button>
                              </div>
                              {mavzu.darslar?.length === 0 ? (
                                <p className="text-xs py-3 text-center" style={{ color: '#8A8371' }}>Hozircha dars yo'q.</p>
                              ) : (
                                <ul className="space-y-1.5">
                                  {mavzu.darslar.map((dars) => (
                                    <li
                                      key={dars.id}
                                      onClick={() => navigate(`/admin/darslar/${dars.id}`)}
                                      className="flex items-center justify-between px-3 py-2 rounded-lg text-xs cursor-pointer transition-all press hover:shadow-sm"
                                      style={{ background: 'var(--color-paper-warm)' }}
                                    >
                                      <span className="flex items-center gap-2" style={{ color: 'var(--color-ink)' }}>
                                        <ListChecks size={12} /> {dars.sarlavha}
                                      </span>
                                      <IconButton
                                        icon={Trash2} tone="danger" size={12}
                                        onClick={async (e) => {
                                          e.stopPropagation();
                                          if (confirm("Darsni o'chirishni tasdiqlaysizmi?")) { await deleteDars(dars.id); load(); }
                                        }}
                                      />
                                    </li>
                                  ))}
                                </ul>
                              )}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </Card>
          ))}
        </div>
      )}

      <Modal open={darajaModal} onClose={() => setDarajaModal(false)} title="Yangi daraja qo'shish">
        <form onSubmit={handleCreateDaraja} className="space-y-4">
          <Input label="Daraja nomi" required value={darajaForm.nomi} onChange={(e) => setDarajaForm({ ...darajaForm, nomi: e.target.value })} placeholder="masalan: Beginner" />
          <Input label="Tartib raqami" type="number" value={darajaForm.tartib} onChange={(e) => setDarajaForm({ ...darajaForm, tartib: e.target.value })} />
          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={saving}>{saving ? 'Saqlanmoqda...' : 'Saqlash'}</Button>
            <Button type="button" variant="secondary" onClick={() => setDarajaModal(false)}>Bekor qilish</Button>
          </div>
        </form>
      </Modal>

      <Modal open={mavzuModal.open} onClose={() => setMavzuModal({ open: false, darajaId: null })} title="Yangi mavzu qo'shish">
        <form onSubmit={handleCreateMavzu} className="space-y-4">
          <Input label="Mavzu nomi" required value={mavzuForm.nomi} onChange={(e) => setMavzuForm({ ...mavzuForm, nomi: e.target.value })} placeholder="masalan: Present Simple" />
          <Input label="Tartib raqami" type="number" value={mavzuForm.tartib} onChange={(e) => setMavzuForm({ ...mavzuForm, tartib: e.target.value })} />
          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={saving}>{saving ? 'Saqlanmoqda...' : 'Saqlash'}</Button>
            <Button type="button" variant="secondary" onClick={() => setMavzuModal({ open: false, darajaId: null })}>Bekor qilish</Button>
          </div>
        </form>
      </Modal>

      <Modal open={darsModal.open} onClose={() => setDarsModal({ open: false, mavzuId: null })} title="Yangi dars qo'shish" wide>
        <form onSubmit={handleCreateDars} className="space-y-4">
          <Input label="Dars sarlavhasi" required value={darsForm.sarlavha} onChange={(e) => setDarsForm({ ...darsForm, sarlavha: e.target.value })} placeholder="masalan: Lesson 1: Affirmative sentences" />
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--color-ink)' }}>Tushuntirish matni</label>
            <textarea
              rows={4}
              value={darsForm.tushuntirish_matn}
              onChange={(e) => setDarsForm({ ...darsForm, tushuntirish_matn: e.target.value })}
              className="w-full px-3.5 py-2.5 rounded-xl border text-sm transition-all"
              style={{ borderColor: 'var(--color-line)' }}
              placeholder="Chuqur va tushunarli tushuntirish..."
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--color-ink)' }}>Misollar</label>
            <textarea
              rows={3}
              value={darsForm.misollar}
              onChange={(e) => setDarsForm({ ...darsForm, misollar: e.target.value })}
              className="w-full px-3.5 py-2.5 rounded-xl border text-sm transition-all"
              style={{ borderColor: 'var(--color-line)' }}
              placeholder="Har bir misolni yangi qatordan yozing"
            />
          </div>
          <p className="text-xs" style={{ color: '#8A8371' }}>
            Video/audio faylni dars yaratilgandan so'ng "Dars tafsiloti" sahifasidan yuklashingiz mumkin. Mashq (40 talik test) ham avtomatik yaratiladi.
          </p>
          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={saving}>{saving ? 'Saqlanmoqda...' : 'Saqlash'}</Button>
            <Button type="button" variant="secondary" onClick={() => setDarsModal({ open: false, mavzuId: null })}>Bekor qilish</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
