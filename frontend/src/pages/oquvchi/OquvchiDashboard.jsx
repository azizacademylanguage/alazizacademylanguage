import { useEffect, useState } from 'react';
import { getFanlarim, getNatijalarim } from '../../api/oquvchi';
import { getCoinlarim } from '../../api/coinShop';
import { getOqishRejasi } from '../../api/engagement';
import { useAuth } from '../../context/AuthContext';
import { Card, StatCard, Skeleton } from '../../components/ui';
import SelectedCoursePanel from '../../components/SelectedCoursePanel';
import PersonalLearningPlan from '../../components/PersonalLearningPlan';
import PWAInstallButton from '../../components/PWAInstallButton';
import { Flame, ClipboardCheck, Coins, LineChart as LineChartIcon, TrendingUp, Smartphone } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="px-3 py-2 rounded-xl text-xs" style={{ background: 'var(--color-forest)', color: 'white', boxShadow: 'var(--shadow-md)' }}>
      <p className="font-semibold">{label}</p>
      <p>{payload[0].value}%</p>
    </div>
  );
}

export default function OquvchiDashboard() {
  const { user } = useAuth();
  const [fanlar, setFanlar] = useState([]);
  const [natijalar, setNatijalar] = useState([]);
  const [coin, setCoin] = useState(0);
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getFanlarim(), getNatijalarim(), getCoinlarim(), getOqishRejasi()])
      .then(([f, n, c, p]) => {
        setFanlar(f);
        setNatijalar(n);
        setCoin(c.balans);
        setPlan(p);
      })
      .finally(() => setLoading(false));
  }, []);

  const selectedCourse = fanlar[0] || null;
  const ortacha = natijalar.length
    ? (natijalar.reduce((sum, item) => sum + Number(item.foiz || 0), 0) / natijalar.length).toFixed(1)
    : 0;
  const completedLevels = selectedCourse?.darajalar?.filter((level) => level.otilgan).length || 0;

  const chartData = [...natijalar]
    .sort((a, b) => new Date(a.boshlangan_vaqt) - new Date(b.boshlangan_vaqt))
    .slice(-10)
    .map((item, index) => ({ nomi: `#${index + 1}`, foiz: Number(item.foiz) }));

  return (
    <div className="animate-in">
      <div className="dashboard-welcome mb-7">
        <div>
          <p className="text-xs uppercase tracking-[0.22em] font-bold mb-2" style={{ color: 'var(--color-teal)' }}>O'quvchi paneli</p>
          <h1 className="font-display text-2xl sm:text-3xl font-extrabold" style={{ color: 'var(--color-ink)' }}>
            Salom, {user?.ism || user?.username}!
          </h1>
          <p className="text-sm mt-1" style={{ color: 'var(--color-muted)' }}>Bugungi darsni davom ettiring va keyingi darajani oching.</p>
        </div>
        <div className="welcome-orb" aria-hidden="true">✦</div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-24 w-full" />)}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <StatCard label="Kunlik streak" value={`${plan?.streak?.joriy || 0} kun`} icon={Flame} accent="teal" delay={0} />
          <StatCard label="Tugatilgan daraja" value={completedLevels} icon={TrendingUp} accent="olive" delay={80} />
          <StatCard label="Yechilgan test" value={natijalar.length} icon={ClipboardCheck} accent="amethyst" delay={160} />
          <StatCard label="Coin" value={coin} icon={Coins} accent="jungle" delay={240} />
        </div>
      )}

      {!loading && plan?.fan && <PersonalLearningPlan plan={plan} />}

      {!loading && (
        <Card className="p-4 mb-6 pwa-dashboard-card">
          <div className="flex items-center gap-3 min-w-0">
            <div className="feature-icon feature-icon--olive"><Smartphone size={18} /></div>
            <div className="min-w-0 flex-1"><p className="font-display font-bold text-sm" style={{ color: 'var(--color-ink)' }}>Saytni telefon ilovasi sifatida ishlating</p><p className="text-xs mt-0.5" style={{ color: 'var(--color-muted)' }}>Bosh ekranga o‘rnating va tezroq oching.</p></div>
            <PWAInstallButton />
          </div>
        </Card>
      )}

      {loading ? (
        <Skeleton className="h-[560px] w-full mb-6" />
      ) : selectedCourse ? (
        <div className="mb-6">
          <SelectedCoursePanel fan={selectedCourse} />
        </div>
      ) : (
        <Card className="p-8 text-center mb-6">
          <p className="font-display font-bold" style={{ color: 'var(--color-ink)' }}>Sizga fan tanlanmagan</p>
          <p className="text-sm mt-1" style={{ color: 'var(--color-muted)' }}>Admin sizga English, Rus tili yoki Koreys tilidan birini tanlab berishi kerak.</p>
        </Card>
      )}

      {!loading && chartData.length >= 2 && (
        <Card className="p-5 mb-6 animate-in-fast stagger-2 result-chart-card">
          <div className="flex items-center gap-2 mb-4">
            <LineChartIcon size={17} style={{ color: 'var(--color-teal)' }} />
            <h2 className="font-display font-bold text-sm" style={{ color: 'var(--color-ink)' }}>So'nggi natijalar</h2>
            <span className="ml-auto text-xs font-semibold" style={{ color: 'var(--color-muted)' }}>O'rtacha: {ortacha}%</span>
          </div>
          <ResponsiveContainer width="100%" height={190}>
            <LineChart data={chartData} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-line)" vertical={false} />
              <XAxis dataKey="nomi" tick={{ fontSize: 11, fill: 'var(--color-muted)' }} axisLine={{ stroke: 'var(--color-line)' }} tickLine={false} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: 'var(--color-muted)' }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Line type="monotone" dataKey="foiz" stroke="var(--color-teal)" strokeWidth={3} dot={{ fill: 'var(--color-jungle)', r: 4 }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      )}
    </div>
  );
}
