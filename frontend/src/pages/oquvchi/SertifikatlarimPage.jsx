import { useEffect, useState } from 'react';
import { getSertifikatlarim } from '../../api/gateTest';
import { Card, EmptyState, Skeleton } from '../../components/ui';
import CertificateCard from '../../components/CertificateCard';
import { Award } from 'lucide-react';

export default function SertifikatlarimPage() {
  const [sertifikatlar, setSertifikatlar] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getSertifikatlarim().then(setSertifikatlar).finally(() => setLoading(false));
  }, []);

  return (
    <div className="animate-in">
      <div className="mb-7">
        <p className="text-xs uppercase tracking-[0.22em] font-bold mb-2" style={{ color: 'var(--color-teal)' }}>Yutuqlarim</p>
        <h1 className="font-display text-2xl sm:text-3xl font-extrabold" style={{ color: 'var(--color-ink)' }}>Sertifikatlarim</h1>
        <p className="text-sm mt-1" style={{ color: 'var(--color-muted)' }}>QR kod orqali tekshiriladigan va PDF shaklida yuklab olinadigan sertifikatlar.</p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">{[1, 2].map((i) => <Skeleton key={i} className="h-[500px] w-full" />)}</div>
      ) : sertifikatlar.length === 0 ? (
        <Card><EmptyState icon={Award} title="Hozircha sertifikat yo'q" description="Darajaning barcha mavzularini va yakuniy testini 80%+ bilan tugating." /></Card>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
          {sertifikatlar.map((certificate) => <CertificateCard key={certificate.id} certificate={certificate} />)}
        </div>
      )}
    </div>
  );
}
