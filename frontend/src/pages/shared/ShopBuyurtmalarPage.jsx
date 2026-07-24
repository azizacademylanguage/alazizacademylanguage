import { useEffect, useMemo, useState } from 'react';
import { Coins, PackageCheck, RefreshCw, Search, ShoppingBag, Store } from 'lucide-react';
import { getShopBuyurtmalar, updateShopBuyurtmaStatus } from '../../api/coinShop';
import { useAuth } from '../../context/AuthContext';
import { Badge, Button, Card, EmptyState, Skeleton } from '../../components/ui';

const statusTone = { yangi: 'warning', tayyor: 'forest', berildi: 'success' };

export default function ShopBuyurtmalarPage() {
  const { user } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [savingId, setSavingId] = useState(null);

  const load = async () => {
    setLoading(true);
    try {
      setItems(await getShopBuyurtmalar(statusFilter));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [statusFilter]);

  const filtered = useMemo(() => {
    const value = query.trim().toLowerCase();
    if (!value) return items;
    return items.filter((item) => `${item.oquvchi_ism} ${item.oquvchi_username} ${item.filial_nomi || ''} ${item.mahsulot_nomi}`.toLowerCase().includes(value));
  }, [items, query]);

  const changeStatus = async (item, status) => {
    setSavingId(item.id);
    try {
      const updated = await updateShopBuyurtmaStatus(item.id, status);
      setItems((prev) => prev.map((row) => row.id === item.id ? updated : row));
    } finally {
      setSavingId(null);
    }
  };

  return (
    <div className="animate-in">
      <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4 mb-6">
        <div>
          <p className="text-xs uppercase tracking-[0.22em] font-bold mb-2" style={{ color: 'var(--color-teal)' }}>
            {user?.role === 'admin' ? 'Barcha filiallar' : 'Mening filialim'}
          </p>
          <h1 className="font-display text-2xl sm:text-3xl font-extrabold" style={{ color: 'var(--color-ink)' }}>Coin do‘koni xaridlari</h1>
          <p className="text-sm mt-1" style={{ color: 'var(--color-muted)' }}>O‘quvchilar sotib olgan mahsulotlar va ularni topshirish holati.</p>
        </div>
        <div className="certificate-count"><Store size={18} /><strong>{items.length}</strong><span>ta xarid</span></div>
      </div>

      <div className="shop-orders-toolbar">
        <div className="relative flex-1 min-w-[220px]">
          <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: 'var(--color-muted)' }} />
          <input className="search-input" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="O‘quvchi, filial yoki mahsulot..." />
        </div>
        <select className="shop-status-filter" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="">Barcha holatlar</option>
          <option value="yangi">Yangi</option>
          <option value="tayyor">Tayyorlanmoqda</option>
          <option value="berildi">Berildi</option>
        </select>
        <Button variant="secondary" onClick={load}><RefreshCw size={15} /> Yangilash</Button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">{[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-48 w-full" />)}</div>
      ) : filtered.length === 0 ? (
        <Card><EmptyState icon={ShoppingBag} title="Xaridlar topilmadi" description="O‘quvchi do‘kondan mahsulot sotib olsa shu yerda ko‘rinadi." /></Card>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
          {filtered.map((item, index) => (
            <Card key={item.id} className="shop-order-card animate-in-fast" style={{ animationDelay: `${index * 35}ms` }}>
              <div className="p-5">
                <div className="flex items-start justify-between gap-3 mb-4">
                  <div className="shop-order-icon"><PackageCheck size={21} /></div>
                  <Badge tone={statusTone[item.status] || 'neutral'}>{item.status_display}</Badge>
                </div>
                <h3 className="font-display text-lg font-extrabold mb-1" style={{ color: 'var(--color-ink)' }}>{item.mahsulot_nomi}</h3>
                <p className="text-sm mb-4" style={{ color: 'var(--color-muted)' }}>{item.mahsulot_tavsif || 'Coin do‘koni mahsuloti'}</p>
                <div className="shop-order-meta">
                  <div><span>O‘quvchi</span><strong>{item.oquvchi_ism}</strong><small>@{item.oquvchi_username}</small></div>
                  <div><span>Filial</span><strong>{item.filial_nomi || 'Biriktirilmagan'}</strong></div>
                  <div><span>Narx</span><strong className="inline-flex items-center gap-1"><Coins size={14} /> {item.narx_coin}</strong></div>
                  <div><span>Sana</span><strong>{new Date(item.created_at).toLocaleString('uz-UZ')}</strong></div>
                </div>
                <div className="mt-4 pt-4 border-t" style={{ borderColor: 'var(--color-line)' }}>
                  <label className="text-xs font-bold block mb-2" style={{ color: 'var(--color-muted)' }}>BUYURTMA HOLATI</label>
                  <select
                    className="shop-status-select"
                    value={item.status}
                    disabled={savingId === item.id}
                    onChange={(e) => changeStatus(item, e.target.value)}
                  >
                    <option value="yangi">Yangi</option>
                    <option value="tayyor">Tayyorlanmoqda</option>
                    <option value="berildi">Berildi</option>
                  </select>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
