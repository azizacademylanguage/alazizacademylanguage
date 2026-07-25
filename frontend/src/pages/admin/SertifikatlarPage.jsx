import { useEffect, useMemo, useState } from 'react';
import { getAdminSertifikatlar } from '../../api/admin';
import { updateSertifikatStatus } from '../../api/features';
import CertificateCard from '../../components/CertificateCard';
import { Badge, Button, Card, EmptyState, Skeleton } from '../../components/ui';
import { Award, Ban, CheckCircle2, Search } from 'lucide-react';
import { useToast } from '../../context/ToastContext';

export default function SertifikatlarPage() {
  const { showToast } = useToast();
  const [items, setItems] = useState([]); const [loading, setLoading] = useState(true); const [query, setQuery] = useState('');
  const load = () => getAdminSertifikatlar().then(setItems).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);
  const filtered = useMemo(() => { const value = query.trim().toLowerCase(); if (!value) return items; return items.filter(item => `${item.oquvchi_ism} ${item.oquvchi_username} ${item.fan_nomi} ${item.daraja_nomi} ${item.kod}`.toLowerCase().includes(value)); }, [items, query]);
  const changeStatus = async certificate => {
    let reason = '';
    const next = !certificate.faol;
    if (!next) { reason = prompt('Sertifikatni bekor qilish sababini yozing:') || ''; if (!reason.trim()) return; }
    try { await updateSertifikatStatus(certificate.id, { faol: next, bekor_sabab: reason }); showToast(next ? 'Sertifikat qayta faollashtirildi.' : 'Sertifikat bekor qilindi.'); setLoading(true); load(); } catch (e) { showToast(e.response?.data?.detail || 'Holat o‘zgarmadi.', 'danger'); }
  };
  return <div className="animate-in"><div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4 mb-6"><div><p className="text-xs uppercase tracking-[0.22em] font-bold mb-2" style={{ color: 'var(--color-teal)' }}>Admin nazorati</p><h1 className="font-display text-2xl sm:text-3xl font-extrabold">Berilgan sertifikatlar</h1><p className="text-sm mt-1" style={{ color: 'var(--color-muted)' }}>QR orqali tekshiriladi; zaruratda sertifikatni bekor qilish mumkin.</p></div><div className="certificate-count"><Award size={18} /><strong>{items.length}</strong><span>ta sertifikat</span></div></div>{items.length > 0 && <div className="relative mb-6 max-w-lg"><Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: 'var(--color-muted)' }} /><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Ism, login, fan, daraja yoki kod..." className="search-input" /></div>}{loading ? <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">{[1, 2].map(i => <Skeleton key={i} className="h-[560px] w-full" />)}</div> : filtered.length === 0 ? <Card><EmptyState icon={Award} title={items.length ? 'Natija topilmadi' : 'Hozircha sertifikat berilmagan'} description={items.length ? 'Qidiruv so‘zini o‘zgartiring.' : 'O‘quvchi final testdan o‘tganda shu yerda paydo bo‘ladi.'} /></Card> : <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">{filtered.map(certificate => <div key={certificate.id} className="space-y-2"><div className="flex items-center justify-between px-1"><Badge tone={certificate.faol === false ? 'danger' : 'success'}>{certificate.faol === false ? 'Bekor qilingan' : 'Haqiqiy'}</Badge><Button size="sm" variant={certificate.faol === false ? 'secondary' : 'danger'} onClick={() => changeStatus(certificate)}>{certificate.faol === false ? <><CheckCircle2 size={15} /> Faollashtirish</> : <><Ban size={15} /> Bekor qilish</>}</Button></div>{certificate.faol === false && certificate.bekor_sabab && <p className="text-xs px-1" style={{ color: 'var(--color-red)' }}>Sabab: {certificate.bekor_sabab}</p>}<CertificateCard certificate={certificate} adminView /></div>)}</div>}</div>;
}
