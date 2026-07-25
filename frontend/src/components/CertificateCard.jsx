import { Award, CalendarDays, CheckCircle2, Download, ExternalLink, ShieldCheck } from 'lucide-react';
import { apiAssetUrl } from '../api/client';
import { Button, Card } from './ui';
import { cleanLevelName, languageMeta } from '../utils/course';

export default function CertificateCard({ certificate, adminView = false, publicView = false }) {
  const meta = languageMeta(certificate.fan_nomi);
  const pdfUrl = apiAssetUrl(certificate.pdf_url);
  const qrUrl = apiAssetUrl(certificate.qr_url);
  const active = certificate.faol !== false;

  return (
    <Card className="certificate-card overflow-hidden">
      <div className="certificate-card__top">
        <div className="certificate-ribbon">AL-AZIZ ACADEMY</div>
        <div className="certificate-seal"><Award size={30} /></div>
        <p className="certificate-kicker">SERTIFIKAT</p>
        <p className="certificate-note">Ushbu sertifikat quyidagi o'quvchiga taqdim etiladi</p>
        <h2 className="certificate-name">{certificate.oquvchi_ism}</h2>
        <div className="certificate-line" />
        <p className="certificate-course">
          <span>{meta.flag}</span> {certificate.fan_nomi} · {cleanLevelName(certificate.daraja_nomi)}
        </p>
        <p className="certificate-result">Yakuniy natija: <strong>{Number(certificate.foiz).toFixed(0)}%</strong></p>
      </div>

      <div className="certificate-card__bottom">
        <div className="certificate-details">
          <div><CalendarDays size={15} /><span>{new Date(certificate.berilgan_sana).toLocaleDateString('uz-UZ')}</span></div>
          <div><ShieldCheck size={15} /><span>{certificate.kod}</span></div>
          {adminView && <div><CheckCircle2 size={15} /><span>Login: {certificate.oquvchi_username}</span></div>}
        </div>
        {active ? <div className="certificate-qr-wrap">
          <img src={qrUrl} alt={`Sertifikat QR ${certificate.kod}`} className="certificate-qr" />
          <span>Tekshirish uchun skanerlang</span>
        </div> : <div className="certificate-qr-wrap" style={{ color: 'var(--color-red)' }}><ShieldCheck size={32} /><span>Bekor qilingan</span></div>}
      </div>

      <div className="certificate-actions">
        {active ? <>
          <a href={pdfUrl} target="_blank" rel="noreferrer" download><Button size="sm"><Download size={15} /> PDF yuklab olish</Button></a>
          {!publicView && certificate.tekshirish_url && <a href={certificate.tekshirish_url} target="_blank" rel="noreferrer"><Button size="sm" variant="secondary"><ExternalLink size={15} /> Tekshirish</Button></a>}
        </> : <div className="text-sm font-semibold" style={{ color: 'var(--color-red)' }}>Sertifikat bekor qilingan{certificate.bekor_sabab ? `: ${certificate.bekor_sabab}` : ''}</div>}
      </div>
    </Card>
  );
}
