import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, CheckCheck, Award, ShoppingBag, AlertTriangle, Info } from 'lucide-react';
import { Card, Button, Skeleton, EmptyState } from '../../components/ui';
import { getBildirishnomalar, markAllBildirishnomalarRead, markBildirishnomaRead } from '../../api/engagement';

const icons = { certificate: Award, shop: ShoppingBag, warning: AlertTriangle, success: CheckCheck, info: Info };

export default function BildirishnomalarPage() {
  const [data, setData] = useState(null);
  const navigate = useNavigate();
  const load = () => getBildirishnomalar().then(setData);
  useEffect(() => { load(); }, []);

  const open = async (item) => {
    if (!item.oqilgan) await markBildirishnomaRead(item.id).catch(() => {});
    if (item.havola) navigate(item.havola);
    else load();
  };

  const readAll = async () => {
    await markAllBildirishnomalarRead();
    load();
  };

  if (!data) return <div className="space-y-3"><Skeleton className="h-20" /><Skeleton className="h-20" /><Skeleton className="h-20" /></div>;

  return (
    <div className="animate-in max-w-3xl">
      <div className="flex items-center justify-between gap-3 mb-6">
        <div>
          <p className="text-xs uppercase tracking-[.2em] font-bold mb-1" style={{ color: 'var(--color-teal)' }}>Xabarlar markazi</p>
          <h1 className="font-display text-2xl font-extrabold" style={{ color: 'var(--color-ink)' }}>Bildirishnomalar</h1>
        </div>
        {data.oqilmagan_soni > 0 && <Button size="sm" variant="secondary" onClick={readAll}><CheckCheck size={15} /> Barchasini o‘qish</Button>}
      </div>

      {data.natijalar.length === 0 ? (
        <Card><EmptyState icon={Bell} title="Bildirishnoma yo‘q" description="Yangi daraja, sertifikat va do‘kon holatlari shu yerda ko‘rinadi." /></Card>
      ) : (
        <div className="space-y-3">
          {data.natijalar.map((item) => {
            const Icon = icons[item.tur] || Info;
            return (
              <button type="button" key={item.id} onClick={() => open(item)} className={`notification-page-item ${item.oqilgan ? '' : 'is-unread'}`}>
                <span className={`notification-page-item__icon type-${item.tur}`}><Icon size={19} /></span>
                <span className="min-w-0 flex-1 text-left">
                  <span className="flex items-center justify-between gap-2"><b>{item.sarlavha}</b><time>{new Date(item.created_at).toLocaleDateString('uz-UZ')}</time></span>
                  <small>{item.matn}</small>
                </span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
