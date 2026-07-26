import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getNazoratchiStatistika, getOquvchilar } from '../../api/nazoratchi';
import { StatCard, Skeleton, Card } from '../../components/ui';
import { Users, ClipboardCheck, TrendingUp, ChevronRight } from 'lucide-react';
import PWAInstallCard from '../../components/PWAInstallCard';

export default function NazoratchiDashboard() {
  const [stats, setStats] = useState(null);
  const [oquvchilar, setOquvchilar] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getNazoratchiStatistika(), getOquvchilar()]).then(([s, o]) => {
      setStats(s);
      setOquvchilar((o.results || o).slice(0, 5));
    }).finally(() => setLoading(false));
  }, []);

  return (
    <div className="animate-in">
      <h1 className="font-display text-2xl font-bold mb-1" style={{ color: 'var(--color-ink)' }}>Boshqaruv paneli</h1>
      <p className="text-sm mb-8" style={{ color: '#8A8371' }}>Sizning filialingiz bo'yicha umumiy holat.</p>

      <PWAInstallCard roleLabel="Filial rahbari" />

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-24 w-full" />)}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
          <StatCard label="O'quvchilarim" value={stats?.oquvchilar_soni ?? 0} icon={Users} accent="forest" delay={0} />
          <StatCard label="Jami urinishlar" value={stats?.jami_urinishlar ?? 0} icon={ClipboardCheck} accent="amber" delay={80} />
          <StatCard label="O'rtacha natija" value={`${stats?.ortacha_foiz ?? 0}%`} icon={TrendingUp} accent="moss" delay={160} />
        </div>
      )}

      <div className="flex items-center justify-between mb-4">
        <h2 className="font-display font-bold text-base" style={{ color: 'var(--color-ink)' }}>So'nggi qo'shilgan o'quvchilar</h2>
        <Link to="/nazoratchi/oquvchilar" className="text-xs font-semibold flex items-center gap-1" style={{ color: 'var(--color-forest)' }}>
          Barchasi <ChevronRight size={13} />
        </Link>
      </div>

      {loading ? (
        <div className="space-y-2">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-14 w-full" />)}</div>
      ) : oquvchilar.length === 0 ? (
        <Card>
          <p className="text-sm text-center py-8" style={{ color: '#8A8371' }}>
            Hali o'quvchi yo'q. "O'quvchilarim" bo'limidan qo'shishingiz mumkin.
          </p>
        </Card>
      ) : (
        <div className="space-y-2">
          {oquvchilar.map((o, idx) => (
            <Link key={o.id} to={`/nazoratchi/oquvchilar/${o.id}`} className="animate-in-fast" style={{ animationDelay: `${idx * 50}ms` }}>
              <Card hover className="flex items-center justify-between p-4">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-full flex items-center justify-center font-display font-bold text-sm" style={{ background: 'var(--color-paper-warm)', color: 'var(--color-forest)' }}>
                    {o.ism?.[0]?.toUpperCase() || '?'}
                  </div>
                  <div>
                    <p className="text-sm font-medium" style={{ color: 'var(--color-ink)' }}>{o.ism} {o.familya}</p>
                    <p className="text-xs" style={{ color: '#8A8371' }}>{o.username}</p>
                  </div>
                </div>
                <ChevronRight size={16} className="text-gray-300" />
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
