import { useEffect, useMemo, useState } from 'react';
import { getAdminSertifikatlar } from '../../api/admin';
import CertificateCard from '../../components/CertificateCard';
import { Card, EmptyState, Skeleton } from '../../components/ui';
import { Award, Search } from 'lucide-react';

export default function SertifikatlarPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');

  useEffect(() => {
    getAdminSertifikatlar().then(setItems).finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    const value = query.trim().toLowerCase();
    if (!value) return items;
    return items.filter((item) => `${item.oquvchi_ism} ${item.oquvchi_username} ${item.fan_nomi} ${item.daraja_nomi} ${item.kod}`.toLowerCase().includes(value));
  }, [items, query]);

  return (
    <div className="animate-in">
      <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4 mb-6">
        <div>
          <p className="text-xs uppercase tracking-[0.22em] font-bold mb-2" style={{ color: 'var(--color-teal)' }}>Admin xabarnomasi</p>
          <h1 className="font-display text-2xl sm:text-3xl font-extrabold" style={{ color: 'var(--color-ink)' }}>Berilgan sertifikatlar</h1>
          <p className="text-sm mt-1" style={{ color: 'var(--color-muted)' }}>80%+ bilan darajadan o'tgan o'quvchilar shu yerda ko'rinadi.</p>
        </div>
        <div className="certificate-count"><Award size={18} /><strong>{items.length}</strong><span>ta sertifikat</span></div>
      </div>

      {items.length > 0 && (
        <div className="relative mb-6 max-w-lg">
          <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: 'var(--color-muted)' }} />
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Ism, login, fan, daraja yoki kod..." className="search-input" />
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">{[1, 2].map((i) => <Skeleton key={i} className="h-[520px] w-full" />)}</div>
      ) : filtered.length === 0 ? (
        <Card><EmptyState icon={Award} title={items.length ? 'Natija topilmadi' : 'Hozircha sertifikat berilmagan'} description={items.length ? 'Qidiruv so‘zini o‘zgartiring.' : "O'quvchi darajani 80%+ bilan tugatganda bu yerda paydo bo'ladi."} /></Card>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
          {filtered.map((certificate) => <CertificateCard key={certificate.id} certificate={certificate} adminView />)}
        </div>
      )}
    </div>
  );
}
