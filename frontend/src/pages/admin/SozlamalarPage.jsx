import { useEffect, useState } from 'react';
import { Bot, Coins, Save, Settings2, ShieldCheck, Wrench } from 'lucide-react';
import { Button, Card, Input, Skeleton, Textarea } from '../../components/ui';
import { getPlatformSozlamalari, updatePlatformSozlamalari } from '../../api/platform';
import { useToast } from '../../context/ToastContext';

function Toggle({ label, description, checked, onChange }) {
  return <label className="flex items-center justify-between gap-4 p-4 rounded-xl border cursor-pointer" style={{ borderColor: 'var(--color-line)', background: checked ? 'rgba(17,126,104,.05)' : '#FAFCFB' }}>
    <div><p className="font-semibold text-sm">{label}</p><p className="text-xs mt-1" style={{ color: '#8A8371' }}>{description}</p></div>
    <input type="checkbox" className="settings-toggle" checked={checked} onChange={e => onChange(e.target.checked)} />
  </label>;
}

export default function SozlamalarPage() {
  const { showToast } = useToast();
  const [form, setForm] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getPlatformSozlamalari().then(setForm).catch(e => showToast(e.response?.data?.detail || 'Sozlamalar yuklanmadi.', 'danger')).finally(() => setLoading(false));
  }, []);

  const set = (key, value) => setForm(prev => ({ ...prev, [key]: value }));
  const save = async () => {
    setSaving(true);
    try {
      const updated = await updatePlatformSozlamalari(form);
      setForm(updated);
      showToast('Platforma sozlamalari saqlandi.');
    } catch (e) {
      const details = e.response?.data;
      showToast(details?.detail || (details ? Object.values(details).flat().join(' ') : 'Sozlamalar saqlanmadi.'), 'danger');
    } finally { setSaving(false); }
  };

  if (loading || !form) return <div className="space-y-4"><Skeleton className="h-24" /><Skeleton className="h-72" /><Skeleton className="h-64" /></div>;

  return <div className="animate-in space-y-5">
    <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-3">
      <div><h1 className="font-display text-2xl font-extrabold" style={{ color: 'var(--color-ink)' }}>Platforma sozlamalari</h1><p className="text-sm mt-1" style={{ color: '#8A8371' }}>AI, murojaatlar, test, coin va umumiy xavfsizlik qoidalarini boshqaring.</p></div>
      <Button onClick={save} loading={saving}><Save size={17} /> Saqlash</Button>
    </div>

    <Card className="p-5">
      <div className="section-heading"><Settings2 size={19} /><div><h2>Umumiy ko‘rinish</h2><p>Platforma nomi va brend ma’lumotlari.</p></div></div>
      <div className="grid md:grid-cols-2 gap-4 mt-5">
        <Input label="Platforma nomi" value={form.platform_nomi || ''} onChange={e => set('platform_nomi', e.target.value)} />
        <Input label="Qisqa nom" value={form.platform_qisqa_nomi || ''} onChange={e => set('platform_qisqa_nomi', e.target.value)} />
        <div className="md:col-span-2"><Input label="Logo URL" hint="Bo‘sh qoldirilsa hozirgi standart logo ishlaydi." value={form.logo_url || ''} onChange={e => set('logo_url', e.target.value)} /></div>
      </div>
    </Card>

    <div className="grid lg:grid-cols-2 gap-5">
      <Card className="p-5">
        <div className="section-heading"><Bot size={19} /><div><h2>AI yordamchi</h2><p>O‘quvchilarning shaxsiy AI yordamchisi.</p></div></div>
        <div className="space-y-4 mt-5">
          <Toggle label="AI yordamchini yoqish" description="O‘quvchilar AI chatdan foydalanadi." checked={!!form.ai_yordamchi_faol} onChange={v => set('ai_yordamchi_faol', v)} />
          <Input type="number" min="1" max="500" label="Bir o‘quvchiga kunlik savol limiti" value={form.ai_kunlik_limit} onChange={e => set('ai_kunlik_limit', Number(e.target.value))} />
        </div>
      </Card>

      <Card className="p-5">
        <div className="section-heading"><Wrench size={19} /><div><h2>Xizmat holati</h2><p>Murojaat va texnik rejim boshqaruvi.</p></div></div>
        <div className="space-y-4 mt-5">
          <Toggle label="Murojaatlar ochiq" description="O‘quvchilar yangi murojaat yubora oladi." checked={!!form.murojaatlar_faol} onChange={v => set('murojaatlar_faol', v)} />
          <Toggle label="Texnik rejim" description="Platformada texnik ishlar xabari ko‘rsatiladi." checked={!!form.texnik_rejim} onChange={v => set('texnik_rejim', v)} />
          <Input label="Texnik xabar" value={form.texnik_xabar || ''} onChange={e => set('texnik_xabar', e.target.value)} />
          <Input type="number" min="1" label="Maksimal fayl hajmi (MB)" value={form.max_fayl_mb} onChange={e => set('max_fayl_mb', Number(e.target.value))} />
        </div>
      </Card>
    </div>

    <div className="grid lg:grid-cols-2 gap-5">
      <Card className="p-5">
        <div className="section-heading"><Coins size={19} /><div><h2>Test va coin qoidalari</h2><p>Yangi mashqlar uchun standart qiymatlar.</p></div></div>
        <div className="grid sm:grid-cols-3 gap-4 mt-5">
          <Input type="number" min="1" max="100" label="O‘tish foizi" value={form.standart_test_foizi} onChange={e => set('standart_test_foizi', Number(e.target.value))} />
          <Input type="number" min="0" label="Mashq coini" value={form.mashq_coin} onChange={e => set('mashq_coin', Number(e.target.value))} />
          <Input type="number" min="0" label="Final test coini" value={form.final_test_coin} onChange={e => set('final_test_coin', Number(e.target.value))} />
        </div>
      </Card>

      <Card className="p-5">
        <div className="section-heading"><ShieldCheck size={19} /><div><h2>Xavfsizlik eslatmasi</h2><p>Foydalanuvchilarga ko‘rsatiladigan xavfsizlik matni.</p></div></div>
        <div className="mt-5"><Textarea rows={5} value={form.xavfsizlik_eslatmasi || ''} onChange={e => set('xavfsizlik_eslatmasi', e.target.value)} /></div>
        <p className="text-xs mt-3" style={{ color: '#8A8371' }}>Oxirgi yangilanish: {form.updated_at ? new Date(form.updated_at).toLocaleString('uz-UZ') : '—'} {form.updated_by_ism ? `· ${form.updated_by_ism}` : ''}</p>
      </Card>
    </div>
  </div>;
}
