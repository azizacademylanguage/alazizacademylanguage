import { useEffect, useState } from 'react';
import { Headphones, MessageCircle, Search, Send } from 'lucide-react';
import { Badge, Button, Card, EmptyState, Input, Modal, Select, Skeleton, Textarea } from '../../components/ui';
import { getAdminMurojaatlar, replyAdminMurojaat, updateAdminMurojaat } from '../../api/platform';
import { useToast } from '../../context/ToastContext';

const STATUS_TONE = { yangi: 'warning', korilmoqda: 'forest', javob_berildi: 'success', yopildi: 'neutral' };
const PRIORITY_TONE = { past: 'neutral', oddiy: 'forest', yuqori: 'warning', shoshilinch: 'danger' };

export default function MurojaatlarPage() {
  const { showToast } = useToast();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ status: '', kategoriya: '', q: '' });
  const [selected, setSelected] = useState(null);
  const [reply, setReply] = useState('');
  const [saving, setSaving] = useState(false);

  const load = () => {
    setLoading(true);
    getAdminMurojaatlar(filters)
      .then(setItems)
      .catch(e => showToast(e.response?.data?.detail || 'Murojaatlar yuklanmadi.', 'danger'))
      .finally(() => setLoading(false));
  };
  useEffect(() => { const t = setTimeout(load, 250); return () => clearTimeout(t); }, [filters.status, filters.kategoriya, filters.q]);

  const syncItem = (updated) => {
    setSelected(updated);
    setItems(prev => prev.map(x => x.id === updated.id ? updated : x));
  };

  const changeState = async (field, value) => {
    if (!selected) return;
    setSaving(true);
    try {
      const updated = await updateAdminMurojaat(selected.id, { [field]: value });
      syncItem(updated);
      showToast('Murojaat holati yangilandi.');
    } catch (e) { showToast(e.response?.data?.detail || 'Holat yangilanmadi.', 'danger'); }
    finally { setSaving(false); }
  };

  const sendReply = async () => {
    if (!reply.trim() || !selected) return;
    setSaving(true);
    try {
      const updated = await replyAdminMurojaat(selected.id, reply);
      syncItem(updated);
      setReply('');
      showToast('Javob o‘quvchiga yuborildi.');
    } catch (e) { showToast(e.response?.data?.detail || 'Javob yuborilmadi.', 'danger'); }
    finally { setSaving(false); }
  };

  const counts = items.reduce((a, x) => { a[x.status] = (a[x.status] || 0) + 1; return a; }, {});
  return (
    <div className="animate-in space-y-5">
      <div>
        <h1 className="font-display text-2xl font-extrabold" style={{ color: 'var(--color-ink)' }}>Murojaatlar markazi</h1>
        <p className="text-sm mt-1" style={{ color: '#8A8371' }}>O‘quvchilar savollarini ko‘ring, javob bering va statusini boshqaring.</p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[['yangi','Yangi'],['korilmoqda','Ko‘rilmoqda'],['javob_berildi','Javob berildi'],['yopildi','Yopildi']].map(([v,l]) => <Card key={v} className="p-4"><p className="text-xs" style={{ color: '#8A8371' }}>{l}</p><p className="font-display text-2xl font-extrabold mt-1">{counts[v] || 0}</p></Card>)}
      </div>

      <Card className="p-4">
        <div className="grid md:grid-cols-[1fr_180px_190px] gap-3">
          <div className="relative"><Search size={16} className="absolute left-3 top-3" style={{ color: '#9C9584' }} /><input value={filters.q} onChange={e => setFilters({ ...filters, q: e.target.value })} className="w-full pl-9 pr-3 py-2.5 rounded-xl border text-sm outline-none" style={{ borderColor: 'var(--color-line)' }} placeholder="Kod, sarlavha yoki o‘quvchi..." /></div>
          <Select value={filters.status} onChange={e => setFilters({ ...filters, status: e.target.value })}><option value="">Barcha statuslar</option><option value="yangi">Yangi</option><option value="korilmoqda">Ko‘rilmoqda</option><option value="javob_berildi">Javob berildi</option><option value="yopildi">Yopildi</option></Select>
          <Select value={filters.kategoriya} onChange={e => setFilters({ ...filters, kategoriya: e.target.value })}><option value="">Barcha kategoriyalar</option><option value="texnik">Texnik muammo</option><option value="dars">Dars savoli</option><option value="test">Test yoki natija</option><option value="sertifikat">Sertifikat</option><option value="hisob">Hisob va xavfsizlik</option><option value="taklif">Taklif</option><option value="boshqa">Boshqa</option></Select>
        </div>
      </Card>

      {loading ? <div className="space-y-3"><Skeleton className="h-24" /><Skeleton className="h-24" /></div> : items.length === 0 ? <Card><EmptyState icon={Headphones} title="Murojaat topilmadi" description="Tanlangan filtrlarga mos murojaat yo‘q." /></Card> : <div className="grid gap-3">
        {items.map(item => <button key={item.id} className="text-left w-full" onClick={() => setSelected(item)}><Card hover className="p-4 sm:p-5"><div className="flex items-start justify-between gap-4"><div className="min-w-0 flex-1"><div className="flex gap-2 flex-wrap mb-2"><Badge tone={STATUS_TONE[item.status]}>{item.status_display}</Badge><Badge tone={PRIORITY_TONE[item.ustuvorlik]}>{item.ustuvorlik_display}</Badge><span className="text-xs font-mono" style={{ color: '#8A8371' }}>{item.kod}</span></div><h3 className="font-display font-bold truncate">{item.sarlavha}</h3><p className="text-sm mt-1 line-clamp-2" style={{ color: '#8A8371' }}>{item.matn}</p><p className="text-xs mt-3" style={{ color: '#9C9584' }}>{item.foydalanuvchi_ism} · @{item.username} {item.filial_nomi ? `· ${item.filial_nomi}` : ''}</p></div><div className="text-right flex-shrink-0"><div className="flex items-center gap-1 text-xs" style={{ color: '#8A8371' }}><MessageCircle size={14} /> {item.javoblar_soni}</div><p className="text-[11px] mt-2" style={{ color: '#9C9584' }}>{new Date(item.updated_at).toLocaleString('uz-UZ', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })}</p></div></div></Card></button>)}
      </div>}

      <Modal open={!!selected} onClose={() => setSelected(null)} title={selected?.sarlavha || 'Murojaat'} subtitle={selected ? `${selected.kod} · ${selected.foydalanuvchi_ism} (@${selected.username})` : ''} wide>
        {selected && <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <Select label="Status" value={selected.status} disabled={saving} onChange={e => changeState('status', e.target.value)}><option value="yangi">Yangi</option><option value="korilmoqda">Ko‘rib chiqilmoqda</option><option value="javob_berildi">Javob berildi</option><option value="yopildi">Yopildi</option></Select>
            <Select label="Ustuvorlik" value={selected.ustuvorlik} disabled={saving} onChange={e => changeState('ustuvorlik', e.target.value)}><option value="past">Past</option><option value="oddiy">Oddiy</option><option value="yuqori">Yuqori</option><option value="shoshilinch">Shoshilinch</option></Select>
          </div>
          <div className="ticket-message ticket-message--user"><strong>{selected.foydalanuvchi_ism}</strong><p>{selected.matn}</p><span>{new Date(selected.created_at).toLocaleString('uz-UZ')}</span></div>
          <div className="space-y-3 max-h-72 overflow-y-auto pr-1">{(selected.javoblar || []).map(j => <div key={j.id} className={`ticket-message ${j.muallif_role === 'admin' ? 'ticket-message--admin' : 'ticket-message--user'}`}><strong>{j.muallif_role === 'admin' ? 'Admin' : selected.foydalanuvchi_ism}</strong><p>{j.matn}</p><span>{new Date(j.created_at).toLocaleString('uz-UZ')}</span></div>)}</div>
          {selected.status !== 'yopildi' && <div className="flex gap-2"><Textarea rows={3} value={reply} onChange={e => setReply(e.target.value)} placeholder="O‘quvchiga javob yozing..." /><Button onClick={sendReply} loading={saving} disabled={!reply.trim()} className="self-end"><Send size={16} /> Yuborish</Button></div>}
        </div>}
      </Modal>
    </div>
  );
}
