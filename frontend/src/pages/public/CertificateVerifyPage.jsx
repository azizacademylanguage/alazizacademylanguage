import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { tekshirSertifikat } from '../../api/gateTest';
import CertificateCard from '../../components/CertificateCard';
import { Card, Skeleton } from '../../components/ui';
import { BadgeCheck, CircleX } from 'lucide-react';

export default function CertificateVerifyPage() {
  const { kod } = useParams();
  const [certificate, setCertificate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    tekshirSertifikat(kod)
      .then(setCertificate)
      .catch((err) => setError(err.response?.data?.detail || 'Sertifikat topilmadi.'))
      .finally(() => setLoading(false));
  }, [kod]);

  return (
    <main className="public-certificate-page">
      <div className="public-certificate-shell">
        <div className="text-center mb-6">
          <p className="public-brand">AL-AZIZ ACADEMY</p>
          <h1 className="font-display text-2xl sm:text-3xl font-extrabold" style={{ color: 'var(--color-ink)' }}>Sertifikatni tekshirish</h1>
        </div>
        {loading ? (
          <Skeleton className="h-[520px] w-full" />
        ) : error || !certificate ? (
          <Card className="p-10 text-center">
            <CircleX size={42} className="mx-auto mb-4" style={{ color: 'var(--color-amethyst)' }} />
            <p className="font-display font-bold text-lg" style={{ color: 'var(--color-ink)' }}>Sertifikat haqiqiy emas</p>
            <p className="text-sm mt-1" style={{ color: 'var(--color-muted)' }}>{error}</p>
          </Card>
        ) : certificate.haqiqiy === false ? (
          <Card className="p-10 text-center">
            <CircleX size={42} className="mx-auto mb-4" style={{ color: 'var(--color-red)' }} />
            <p className="font-display font-bold text-lg" style={{ color: 'var(--color-ink)' }}>Sertifikat bekor qilingan</p>
            <p className="text-sm mt-2" style={{ color: 'var(--color-muted)' }}>Kod: {certificate.kod}</p>
            {certificate.bekor_sabab && <p className="text-sm mt-2" style={{ color: 'var(--color-red)' }}>Sabab: {certificate.bekor_sabab}</p>}
          </Card>
        ) : (
          <>
            <div className="verified-banner"><BadgeCheck size={19} /> Ushbu sertifikat bazada mavjud va haqiqiy.</div>
            <CertificateCard certificate={certificate} publicView />
          </>
        )}
      </div>
    </main>
  );
}
