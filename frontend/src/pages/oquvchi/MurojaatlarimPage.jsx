import { useEffect, useState } from 'react';
import { Headphones, MessageCircle, Plus, Send, XCircle } from 'lucide-react';
import { Badge, Button, Card, EmptyState, Input, Modal, Select, Skeleton, Textarea } from '../../components/ui';
import { createMurojaat, getMeningMurojaatlarim, replyMeningMurojaatim } from '../../api/platform';
import { useToast } from '../../context/ToastContext';

const STATUS_TONE = { yangi: 'warning', korilmoqda: 'forest', javob_berildi: 'success', yopildi: 'neutral' };
const KATEGORIYALAR = [
  ['texnik', 'Texnik muammo'], ['dars', "Dars bo‘yicha savol"], ['test', 'Test yoki natija'],
  ['sertifikat', 'Sertifikat'], ['hisob', 'Hisob va xavfsizlik'], ['taklif', 'Taklif'], ['boshqa', 'Boshqa'],
];

export default function MurojaatlarimPage() {
  const { showToast } = useToast();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newOpen, setNewOpen] = useState(false);
  const [selected, setSelected] = useState(null);
  const [reply, setReply] = useState('');
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ kategoriya: 'texnik', sarlavha: '', matn: '' });

  const load = () => getMeningMurojaatlarim().then(setItems).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const create = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const item = await createMurojaat(form);
      setItems(prev => [item, ...prev]);
      setForm({ kategoriya: 'texnik', sarlavha: '', matn: '' });
      setNewOpen(false);
      showToast('Murojaat yuborildi.');
    } catch (err) {
      showToast(err.response?.data?.detail || 'Murojaat yuborilmadi.', 'danger');
    } finally { setSaving(false); }
  };

  const sendReply = async () => {
    if (!reply.trim() || !selected) return;
    setSaving(true);
    try {
      const updated = await replyMeningMurojaatim(selected.id, reply);
      setSelected(updated);
      setItems(prev => prev.map(x => x.id === updated.id ? updated : x));
      setReply('');
      showToast('Javob yuborildi.');
    } catch (err) {
      showToast(err.response?.data?.detail || 'Javob yuborilmadi.', 'danger');
    } finally { setSaving(false); }
  };

  return (
    <div className="animate-in space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-3">
        <div>
          <h1 className="font-display text-2xl font-extrabold" style={{ color: 'var(--color-ink)' }}>Murojaatlarim</h1>
          <p className="text-sm mt-1" style={{ color: '#8A8371' }}>Texnik muammo, test, sertifikat yoki boshqa savollar bo‘yicha adminga yozing.</p>
        </div>
        <Button onClick={() => setNewOpen(true)}><Plus size={17} /> Yangi murojaat</Button>
      </div>

      {loading ? <div className="space-y-3"><Skeleton className="h-24" /><Skeleton className="h-24" /></div> : items.length === 0 ? (
        <Card><EmptyState icon={Headphones} title="Murojaat yo‘q" description="Savol yoki muammo bo‘lsa yangi murojaat yuboring." action={<Button onClick={() => setNewOpen(true)}><Plus size={16} /> Murojaat yuborish</Button>} /></Card>
      ) : (
        <div className="grid gap-3">
          {items.map(item => (
            <button key={item.id} onClick={() => setSelected(item)} className="text-left w-full">
              <Card hover className="p-4 sm:p-5">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-2">
                      <Badge tone={STATUS_TONE[item.status] || 'neutral'}>{item.status_display}</Badge>
                      <span className="text-xs font-mono" style={{ color: '#8A8371' }}>{item.kod}</span>
                      {item.oxirgi_javob_adminniki && item.status !== 'yopildi' && <Badge tone="success">Yangi javob</Badge>}
                    </div>
                    <h3 className="font-display font-bold truncate" style={{ color: 'var(--color-ink)' }}>{item.sarlavha}</h3>
                    <p className="text-sm mt-1 line-clamp-2" style={{ color: '#8A8371' }}>{item.matn}</p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <div className="flex items-center gap-1 text-xs" style={{ color: '#8A8371' }}><MessageCircle size={14} /> {item.javoblar_soni}</div>
                    <p className="text-[11px] mt-2" style={{ color: '#9C9584' }}>{new Date(item.updated_at).toLocaleDateString('uz-UZ')}</p>
                  </div>
                </div>
              </Card>
            </button>
          ))}
        </div>
      )}

      <Modal open={newOpen} onClose={() => setNewOpen(false)} title="Yangi murojaat" subtitle="Muammoni aniq yozing — admin javobi shu bo‘limda ko‘rinadi." wide>
        <form onSubmit={create} className="space-y-4">
          <Select label="Kategoriya" value={form.kategoriya} onChange={e => setForm({ ...form, kategoriya: e.target.value })}>
            {KATEGORIYALAR.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </Select>
          <Input label="Sarlavha" required maxLength={200} value={form.sarlavha} onChange={e => setForm({ ...form, sarlavha: e.target.value })} placeholder="Masalan: Test natijasi ko‘rinmayapti" />
          <Textarea label="Batafsil ma’lumot" required rows={6} value={form.matn} onChange={e => setForm({ ...form, matn: e.target.value })} placeholder="Qachon va qaysi sahifada muammo bo‘lganini yozing..." />
          <div className="flex justify-end gap-2"><Button variant="secondary" onClick={() => setNewOpen(false)}>Bekor qilish</Button><Button type="submit" loading={saving}>Yuborish</Button></div>
        </form>
      </Modal>

      <Modal open={!!selected} onClose={() => setSelected(null)} title={selected?.sarlavha || 'Murojaat'} subtitle={selected ? `${selected.kod} · ${selected.kategoriya_display}` : ''} wide>
        {selected && <div className="space-y-4">
          <div className="flex gap-2 flex-wrap"><Badge tone={STATUS_TONE[selected.status] || 'neutral'}>{selected.status_display}</Badge><Badge tone="neutral">{selected.ustuvorlik_display}</Badge></div>
          <div className="ticket-message ticket-message--user"><p>{selected.matn}</p><span>{new Date(selected.created_at).toLocaleString('uz-UZ')}</span></div>
          <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
            {(selected.javoblar || []).map(j => <div key={j.id} className={`ticket-message ${j.muallif_role === 'admin' ? 'ticket-message--admin' : 'ticket-message--user'}`}><strong>{j.muallif_role === 'admin' ? 'Admin' : 'Siz'}</strong><p>{j.matn}</p><span>{new Date(j.created_at).toLocaleString('uz-UZ')}</span></div>)}
          </div>
          {selected.status === 'yopildi' ? <div className="flex items-center gap-2 p-3 rounded-xl text-sm" style={{ background: '#F4F4F2', color: '#6B6455' }}><XCircle size={16} /> Bu murojaat yopilgan.</div> : <div className="flex gap-2"><Textarea rows={2} value={reply} onChange={e => setReply(e.target.value)} placeholder="Qo‘shimcha javob yozing..." /><Button onClick={sendReply} loading={saving} disabled={!reply.trim()} className="self-end"><Send size={16} /></Button></div>}
        </div>}
      </Modal>
    </div>
  );
}
