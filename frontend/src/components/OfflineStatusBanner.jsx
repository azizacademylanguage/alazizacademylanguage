import { CloudOff, RefreshCw, Wifi } from 'lucide-react';
import { useConnectivity } from '../context/ConnectivityContext';
import { useLanguage } from '../context/LanguageContext';

export default function OfflineStatusBanner() {
  const { online, stats, syncing, lastSync, syncNow } = useConnectivity();
  const { t } = useLanguage();
  const show = !online || stats.queueCount > 0 || syncing || (lastSync?.synced > 0 && Date.now() - lastSync.at < 7000);
  if (!show) return null;

  const message = !online
    ? t('offline.bannerOffline')
    : syncing
      ? t('offline.bannerSyncing')
      : stats.queueCount > 0
        ? t('offline.bannerPending', { count: stats.queueCount })
        : t('offline.bannerSynced');

  return (
    <div className={`offline-status-banner ${online ? 'is-online' : 'is-offline'}`} role="status">
      <span className="offline-status-banner__icon">
        {online ? <Wifi size={16} /> : <CloudOff size={16} />}
      </span>
      <span className="offline-status-banner__text">{message}</span>
      {online && stats.queueCount > 0 && (
        <button type="button" onClick={syncNow} disabled={syncing} className="offline-status-banner__button">
          <RefreshCw size={14} className={syncing ? 'animate-spin' : ''} /> {t('common.sync')}
        </button>
      )}
    </div>
  );
}
