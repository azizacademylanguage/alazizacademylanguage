import { CloudUpload, WifiOff } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button, Card } from './ui';
import { useLanguage } from '../context/LanguageContext';

export default function OfflineQueuedNotice({ compact = false }) {
  const { t } = useLanguage();
  if (compact) {
    return (
      <div className="offline-queued-inline">
        <WifiOff size={18} />
        <div><strong>{t('offline.queuedResultTitle')}</strong><span>{t('offline.queuedResultText')}</span></div>
      </div>
    );
  }
  return (
    <Card className="offline-queued-result p-7 text-center animate-pop">
      <div className="offline-queued-result__icon"><CloudUpload size={32} /></div>
      <h2 className="font-display text-xl font-extrabold">{t('offline.queuedResultTitle')}</h2>
      <p>{t('offline.queuedResultText')}</p>
      <Link to="/oquvchi/offline"><Button>{t('nav.offline')}</Button></Link>
    </Card>
  );
}
