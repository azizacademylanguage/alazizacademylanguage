import { useEffect, useState } from 'react';
import { boshlashMusobaqa, createMusobaqa, getFiliallar, getMusobaqalar, yakunlaMusobaqa } from '../../api/adminExtra';
import { getFanlar } from '../../api/admin';
import { Badge, Button, Card, Input, Modal, Select, Textarea } from '../../components/ui';
import { CalendarDays, Clock3, Medal, Play, Plus, Sparkles, Trophy, Users } from 'lucide-react';

const today = new Date().toISOString().slice(0, 10);
const empty = { nomi:'', tavsif:'', boshlanish_sana:today, tugash_sana:today, fan:'', filial:'', status:'reja', davomiyligi_daq:15, savollar_soni:20, birinchi_coin:100, ikkinchi_coin:60, uchinchi_coin:30 };
const tone = (value) => value === 'yakun' ? 'success' : value === 'faol' ? 'warning' : 'neutral';
const statusLabel = (value) => ({ reja:'Rejada', faol:'Jonli', yakun:'Yakunlangan' }[value] || value);

export default function MusobaqalarPage() {
  const [items,setItems]=useState([]); const [fanlar,setFanlar]=useState([]); const [filiallar,setFiliallar]=useState([]);
  const [open,setOpen]=useState(false); const [form,setForm]=useState(empty); const [saving,setSaving]=useState(false); const [busyId,setBusyId]=useState(null);
  const load=()=>Promise.all([getMusobaqalar(),getFanlar(),getFiliallar()]).then(([a,b,c])=>{setItems(a.results||a);setFanlar(b.results||b);setFiliallar(c.results||c)});
  useEffect(()=>{load()},[]);
  const submit=async e=>{e.preventDefault();setSaving(true);try{await createMusobaqa({...form,fan:form.fan||null,filial:form.filial||null,davomiyligi_daq:Number(form.davomiyligi_daq),savollar_soni:Number(form.savollar_soni),birinchi_coin:Number(form.birinchi_coin),ikkinchi_coin:Number(form.ikkinchi_coin),uchinchi_coin:Number(form.uchinchi_coin)});setOpen(false);setForm(empty);await load()}finally{setSaving(false)}};
  const start=async id=>{if(!confirm('Musobaqa o‘quvchilarda hozir boshlansinmi?'))return;setBusyId(id);try{await boshlashMusobaqa(id);await load()}finally{setBusyId(null)}};
  const finish=async id=>{if(!confirm('Musobaqani yakunlab, 1–3 o‘rinlarga coin berilsinmi?'))return;setBusyId(id);try{await yakunlaMusobaqa(id);await load()}finally{setBusyId(null)}};
  return <div className="animate-in">
    <div className="competition-admin-hero"><div><span className="competition-admin-hero__eyebrow"><Sparkles size={14}/>Jonli bellashuv</span><h1>Reyting va musobaqalar</h1><p>Musobaqani boshlashingiz bilan mos o‘quvchilarda katta jonli bildirishnoma chiqadi.</p></div><Button onClick={()=>setOpen(true)}><Plus size={16}/>Yangi musobaqa</Button></div>
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">{items.map(item=><Card key={item.id} className={`competition-admin-card p-5 competition-admin-card--${item.status}`}>
      <div className="flex justify-between gap-3"><div className="min-w-0"><div className="flex items-center gap-2"><span className="competition-admin-card__icon"><Trophy size={18}/></span><h2 className="font-display font-bold truncate">{item.nomi}</h2></div><p className="text-xs mt-2" style={{color:'var(--color-muted)'}}>{item.fan_nomi||'Barcha fanlar'} · {item.filial_nomi||'Barcha filiallar'}</p></div><Badge tone={tone(item.status)}>{statusLabel(item.status)}</Badge></div>
      <p className="text-sm mt-3 competition-admin-card__description">{item.tavsif||'Musobaqa tavsifi kiritilmagan.'}</p>
      <div className="competition-admin-card__stats"><span><Clock3 size={14}/>{item.davomiyligi_daq} daqiqa</span><span><Sparkles size={14}/>{item.savollar_soni} savol</span><span><Users size={14}/>{item.qatnashuvchilar_soni||0} qatnashuvchi</span><span><CalendarDays size={14}/>{item.boshlanish_sana}</span></div>
      <div className="mt-4 space-y-2">{(item.reyting||[]).slice(0,5).map(row=><div key={row.oquvchi_id} className="competition-ranking-row"><Medal size={15}/><span className="w-7">#{row.orin}</span><span className="flex-1 truncate">{row.ism}</span><b>{row.foiz??row.ball}%</b></div>)}{!item.reyting?.length&&<p className="text-xs text-center py-3" style={{color:'var(--color-muted)'}}>Hali natija yo‘q.</p>}</div>
      <div className="flex flex-wrap gap-2 mt-4">{item.status==='reja'&&<Button loading={busyId===item.id} onClick={()=>start(item.id)}><Play size={16}/>Boshlash</Button>}{item.status==='faol'&&<Button variant="amber" loading={busyId===item.id} onClick={()=>finish(item.id)}>Yakunlash va coin berish</Button>}</div>
    </Card>)}</div>
    <Modal open={open} onClose={()=>setOpen(false)} title="Yangi musobaqa" subtitle="Fan, filial, savollar soni va vaqtni belgilang." wide><form onSubmit={submit} className="space-y-3">
      <Input label="Nomi" required value={form.nomi} onChange={e=>setForm({...form,nomi:e.target.value})}/><Textarea label="Tavsif" rows={3} value={form.tavsif} onChange={e=>setForm({...form,tavsif:e.target.value})}/>
      <div className="grid grid-cols-2 gap-3"><Input type="date" label="Boshlanish" required value={form.boshlanish_sana} onChange={e=>setForm({...form,boshlanish_sana:e.target.value})}/><Input type="date" label="Tugash" required value={form.tugash_sana} onChange={e=>setForm({...form,tugash_sana:e.target.value})}/></div>
      <div className="grid grid-cols-2 gap-3"><Select label="Fan" value={form.fan} onChange={e=>setForm({...form,fan:e.target.value})}><option value="">Barcha fanlar</option>{fanlar.map(f=><option key={f.id} value={f.id}>{f.nomi}</option>)}</Select><Select label="Filial" value={form.filial} onChange={e=>setForm({...form,filial:e.target.value})}><option value="">Barcha filiallar</option>{filiallar.map(f=><option key={f.id} value={f.id}>{f.nomi}</option>)}</Select></div>
      <div className="grid grid-cols-2 gap-3"><Input min="1" max="120" type="number" label="Vaqt (daqiqa)" value={form.davomiyligi_daq} onChange={e=>setForm({...form,davomiyligi_daq:e.target.value})}/><Input min="1" max="100" type="number" label="Savollar soni" value={form.savollar_soni} onChange={e=>setForm({...form,savollar_soni:e.target.value})}/></div>
      <div className="grid grid-cols-3 gap-2"><Input type="number" label="1-o‘rin" value={form.birinchi_coin} onChange={e=>setForm({...form,birinchi_coin:e.target.value})}/><Input type="number" label="2-o‘rin" value={form.ikkinchi_coin} onChange={e=>setForm({...form,ikkinchi_coin:e.target.value})}/><Input type="number" label="3-o‘rin" value={form.uchinchi_coin} onChange={e=>setForm({...form,uchinchi_coin:e.target.value})}/></div><Button type="submit" loading={saving} className="w-full">Saqlash</Button>
    </form></Modal>
  </div>;
}
