import { useEffect, useState } from 'react';
import { getShopMahsulotlari, getShopBuyurtmalarim, shopXarid, getCoinlarim } from '../../api/coinShop';
import { Card, Button, EmptyState, Skeleton, Badge } from '../../components/ui';
import { ShoppingBag, Coins, Check, PackageCheck } from 'lucide-react';

export default function ShopPage() {
  const [mahsulotlar, setMahsulotlar] = useState([]);
  const [balans, setBalans] = useState(0);
  const [loading, setLoading] = useState(true);
  const [xaridQilinmoqda, setXaridQilinmoqda] = useState(null);
  const [xatolik, setXatolik] = useState('');
  const [sotibOlingan, setSotibOlingan] = useState(new Set());
  const [buyurtmalar, setBuyurtmalar] = useState([]);

  const load = () => {
    Promise.all([getShopMahsulotlari(), getCoinlarim(), getShopBuyurtmalarim()]).then(([m, c, b]) => {
      setMahsulotlar(m);
      setBalans(c.balans);
      setBuyurtmalar(b);
    }).finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleXarid = async (mahsulot) => {
    setXatolik('');
    setXaridQilinmoqda(mahsulot.id);
    try {
      const buyurtma = await shopXarid(mahsulot.id);
      setBuyurtmalar((prev) => [buyurtma, ...prev]);
      setSotibOlingan((prev) => new Set([...prev, mahsulot.id]));
      setBalans(buyurtma.qolgan_balans);
      window.dispatchEvent(new CustomEvent('coin-updated', { detail: buyurtma.qolgan_balans }));
    } catch (err) {
      setXatolik(err.response?.data?.detail || 'Xarid amalga oshmadi.');
    } finally {
      setXaridQilinmoqda(null);
    }
  };

  return (
    <div className="animate-in">
      <div className="flex items-center justify-between mb-1">
        <h1 className="font-display text-2xl font-bold" style={{ color: 'var(--color-ink)' }}>Do'kon</h1>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full" style={{ background: 'var(--color-amber-light)' }}>
          <Coins size={15} style={{ color: 'var(--color-amber-dark)' }} />
          <span className="text-sm font-bold tabular-nums" style={{ color: 'var(--color-amber-dark)' }}>{balans}</span>
        </div>
      </div>
      <p className="text-sm mb-8" style={{ color: '#8A8371' }}>Coin yig'ib, mahsulotlarni sotib oling.</p>

      {xatolik && (
        <div className="mb-4 text-sm px-3 py-2.5 rounded-xl animate-pop" style={{ background: '#FBEAE8', color: 'var(--color-red)' }}>
          {xatolik}
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-48 w-full" />)}</div>
      ) : mahsulotlar.length === 0 ? (
        <Card><EmptyState icon={ShoppingBag} title="Do'konda hozircha mahsulot yo'q" description="Tez orada yangi mahsulotlar qo'shiladi." /></Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {mahsulotlar.map((m, idx) => {
            const yetarli = balans >= m.narx_coin;
            const xaridQilingan = sotibOlingan.has(m.id);
            return (
              <Card key={m.id} className="animate-in-fast" style={{ animationDelay: `${idx * 50}ms` }}>
                <div className="p-5">
                  {m.rasm ? (
                    <img src={m.rasm} alt={m.nomi} className="w-full h-28 object-cover rounded-xl mb-3" />
                  ) : (
                    <div
                      className="w-full h-28 rounded-xl mb-3 flex items-center justify-center"
                      style={{ background: 'var(--color-paper-warm)' }}
                    >
                      <ShoppingBag size={28} style={{ color: 'var(--color-moss)' }} />
                    </div>
                  )}
                  <p className="font-display font-bold text-sm mb-1" style={{ color: 'var(--color-ink)' }}>{m.nomi}</p>
                  {m.tavsif && <p className="text-xs mb-3" style={{ color: '#8A8371' }}>{m.tavsif}</p>}
                  <div className="flex items-center justify-between">
                    <Badge tone="warning"><Coins size={11} className="inline -mt-0.5 mr-1" />{m.narx_coin}</Badge>
                    {xaridQilingan ? (
                      <span className="flex items-center gap-1 text-xs font-semibold" style={{ color: 'var(--color-forest)' }}>
                        <Check size={13} /> Sotib olindi
                      </span>
                    ) : (
                      <Button
                        size="sm"
                        variant={yetarli ? 'primary' : 'secondary'}
                        disabled={!yetarli || xaridQilinmoqda === m.id}
                        onClick={() => handleXarid(m)}
                      >
                        {xaridQilinmoqda === m.id ? '...' : yetarli ? 'Sotib olish' : 'Yetarli emas'}
                      </Button>
                    )}
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {buyurtmalar.length > 0 && (
        <section className="mt-10">
          <div className="flex items-center gap-2 mb-4">
            <PackageCheck size={20} style={{ color: 'var(--color-teal)' }} />
            <h2 className="font-display text-xl font-extrabold" style={{ color: 'var(--color-ink)' }}>Xaridlarim</h2>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
            {buyurtmalar.map((item) => (
              <Card key={item.id} className="shop-my-order">
                <div className="p-4 flex items-center justify-between gap-4">
                  <div>
                    <strong className="block text-sm" style={{ color: 'var(--color-ink)' }}>{item.mahsulot_nomi}</strong>
                    <span className="text-xs" style={{ color: 'var(--color-muted)' }}>{new Date(item.created_at).toLocaleString('uz-UZ')}</span>
                  </div>
                  <Badge tone={item.status === 'berildi' ? 'success' : item.status === 'tayyor' ? 'forest' : 'warning'}>{item.status_display}</Badge>
                </div>
              </Card>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
