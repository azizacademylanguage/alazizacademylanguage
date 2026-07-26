import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getAdminSertifikatlar, getAdminStatistika } from '../../api/admin';
import { StatCard, Card, Skeleton, Badge, Button } from '../../components/ui';
import { Award, Building2, Users, GraduationCap, TrendingUp, ArrowRight } from 'lucide-react';
import BranchComparisonChart from '../../components/BranchComparisonChart';
import PWAInstallCard from '../../components/PWAInstallCard';
import { cleanLevelName } from '../../utils/course';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [certificates, setCertificates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getAdminStatistika(), getAdminSertifikatlar()])
      .then(([statsData, certificateData]) => {
        setStats(statsData);
        setCertificates(certificateData);
      })
      .finally(() => setLoading(false));
  }, []);

  const chartData = stats?.filiallar_kesimida?.map((item) => ({
    name: item.filial_nomi,
    students: item.oquvchilar_soni,
    average: item.ortacha_foiz,
  })) || [];

  return (
    <div className="animate-in">
      <div className="mb-7">
        <p className="text-xs uppercase tracking-[0.22em] font-bold mb-2" style={{ color: 'var(--color-teal)' }}>Admin nazorati</p>
        <h1 className="font-display text-2xl sm:text-3xl font-extrabold" style={{ color: 'var(--color-ink)' }}>Boshqaruv paneli</h1>
        <p className="text-sm mt-1" style={{ color: 'var(--color-muted)' }}>O'quvchilar, natijalar va yangi sertifikatlarni kuzating.</p>
      </div>

      <PWAInstallCard roleLabel="Admin" />

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">{[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-24 w-full" />)}</div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <StatCard label="Filiallar" value={stats?.jami_filiallar ?? 0} icon={Building2} accent="teal" delay={0} />
          <StatCard label="Nazoratchilar" value={stats?.jami_nazoratchilar ?? 0} icon={Users} accent="amethyst" delay={80} />
          <StatCard label="O'quvchilar" value={stats?.jami_oquvchilar ?? 0} icon={GraduationCap} accent="jungle" delay={160} />
          <StatCard label="Sertifikatlar" value={certificates.length} icon={Award} accent="olive" delay={240} />
        </div>
      )}

      {!loading && certificates.length > 0 && (
        <Card className="p-5 mb-6 certificate-notification animate-in-fast">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
            <div>
              <div className="flex items-center gap-2"><Award size={18} style={{ color: 'var(--color-olive)' }} /><h2 className="font-display font-bold" style={{ color: 'var(--color-ink)' }}>Yangi darajadan o'tganlar</h2></div>
              <p className="text-xs mt-1" style={{ color: 'var(--color-muted)' }}>80%+ natija olgan o'quvchilarga sertifikat avtomatik yaratildi.</p>
            </div>
            <Link to="/admin/sertifikatlar"><Button size="sm" variant="secondary">Barchasini ko'rish <ArrowRight size={14} /></Button></Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {certificates.slice(0, 3).map((certificate) => (
              <Link key={certificate.id} to="/admin/sertifikatlar" className="recent-certificate-item">
                <div className="recent-certificate-icon"><Award size={17} /></div>
                <div className="min-w-0">
                  <p className="font-semibold text-sm truncate" style={{ color: 'var(--color-ink)' }}>{certificate.oquvchi_ism}</p>
                  <p className="text-xs truncate" style={{ color: 'var(--color-muted)' }}>{certificate.fan_nomi} · {cleanLevelName(certificate.daraja_nomi)}</p>
                </div>
                <Badge tone="success">{Number(certificate.foiz).toFixed(0)}%</Badge>
              </Link>
            ))}
          </div>
        </Card>
      )}

      {!loading && chartData.length > 0 && (
        <Card className="p-0 mb-6 animate-in-fast branch-comparison-card">
          <BranchComparisonChart data={chartData} />
        </Card>
      )}

      <Card className="animate-in-fast">
        <div className="flex items-center gap-2 p-5 pb-0"><TrendingUp size={17} style={{ color: 'var(--color-jungle)' }} /><h2 className="font-display font-bold text-sm" style={{ color: 'var(--color-ink)' }}>Filiallar kesimida statistika</h2></div>
        {loading ? (
          <div className="p-5 space-y-2">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-10 w-full" />)}</div>
        ) : !stats?.filiallar_kesimida?.length ? (
          <p className="text-sm py-8 text-center px-5" style={{ color: 'var(--color-muted)' }}>Hozircha filiallar mavjud emas.</p>
        ) : (
          <div className="overflow-x-auto p-5 pt-3">
            <table className="w-full text-sm">
              <thead><tr className="text-left border-b" style={{ borderColor: 'var(--color-line)' }}><th className="py-2 pr-4">Filial</th><th className="py-2 pr-4">Nazoratchilar</th><th className="py-2 pr-4">O'quvchilar</th><th className="py-2 pr-4">O'rtacha natija</th></tr></thead>
              <tbody>{stats.filiallar_kesimida.map((item) => <tr key={item.filial_id} className="border-b last:border-0" style={{ borderColor: 'var(--color-line)' }}><td className="py-3 pr-4 font-medium">{item.filial_nomi}</td><td className="py-3 pr-4">{item.nazoratchilar_soni}</td><td className="py-3 pr-4">{item.oquvchilar_soni}</td><td className="py-3 pr-4 font-semibold" style={{ color: 'var(--color-jungle)' }}>{item.ortacha_foiz}%</td></tr>)}</tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
