import { useEffect, useState } from 'react';
import { CloudDownload, Database, HardDriveDownload, RefreshCw, ShieldCheck, Trash2, Wifi, WifiOff } from 'lucide-react';
import { getFanlarim, getMavzular, getDars, getMashq } from '../../api/oquvchi';
import { getListening } from '../../api/engagement';
import { getSpeakingTopshiriqlar, getWritingTopshiriqlar } from '../../api/writingSpeaking';
import { getFinalTest, getGateTest } from '../../api/gateTest';
import { Card, Button, ProgressBar } from '../../components/ui';
import { useConnectivity } from '../../context/ConnectivityContext';
import { useLanguage } from '../../context/LanguageContext';
import { clearCurrentUserOfflineData, getOfflineStats, setOfflineMeta } from '../../utils/offlineDb';
import { apiAssetUrl } from '../../api/client';

const MEDIA_CACHE = 'alaziz-offline-media-v1';

function collectMediaUrls(value, output = new Set()) {
  if (!value) return output;
  if (typeof value === 'string') {
    if (/^(https?:\/\/|\/media\/)/i.test(value) && /\.(mp3|wav|ogg|m4a|mp4|webm|jpg|jpeg|png|webp|pdf)(\?|$)/i.test(value)) {
      output.add(apiAssetUrl(value));
    }
    return output;
  }
  if (Array.isArray(value)) value.forEach((entry) => collectMediaUrls(entry, output));
  else if (typeof value === 'object') Object.values(value).forEach((entry) => collectMediaUrls(entry, output));
  return output;
}

async function cacheMedia(urls) {
  if (!('caches' in window)) return 0;
  const cache = await caches.open(MEDIA_CACHE);
  let saved = 0;
  for (const url of urls) {
    try {
      const response = await fetch(url, { credentials: 'omit' });
      if (response.ok || response.type === 'opaque') {
        await cache.put(url, response.clone());
        saved += 1;
      }
    } catch {
      // Media is optional; lesson text remains available.
    }
  }
  return saved;
}

function formatBytes(bytes = 0) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function OfflinePage() {
  const { t, locale } = useLanguage();
  const { online, stats, syncing, syncNow, refreshStats } = useConnectivity();
  const [downloading, setDownloading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('');
  const [localStats, setLocalStats] = useState(stats);

  const reload = async () => {
    const next = await getOfflineStats();
    setLocalStats(next);
    await refreshStats();
  };

  useEffect(() => { reload().catch(() => {}); }, [stats.cacheCount, stats.queueCount, stats.lastDownload]);

  const downloadLessons = async () => {
    if (!online || downloading) return;
    setDownloading(true);
    setMessage('');
    setProgress(2);
    let lessonCount = 0;
    const media = new Set();
    try {
      const fanResponse = await getFanlarim();
      const fanlar = Array.isArray(fanResponse) ? fanResponse : (fanResponse?.results || []);
      const openLevels = fanlar.flatMap((fan) => (fan.darajalar || []).filter((level) => level.ochiq));
      let completedLevels = 0;
      for (const level of openLevels) {
        const topicResponse = await getMavzular(level.id);
        const topics = Array.isArray(topicResponse) ? topicResponse : (topicResponse?.results || []);
        collectMediaUrls(topics, media);
        const lessons = topics.flatMap((topic) => topic.darslar || []);
        for (const lesson of lessons) {
          const detail = await getDars(lesson.id);
          collectMediaUrls(detail, media);
          await Promise.allSettled([
            getListening(lesson.id),
            getWritingTopshiriqlar(lesson.id),
            getSpeakingTopshiriqlar(lesson.id),
            detail.mashq_id ? getMashq(detail.mashq_id) : Promise.resolve(null),
          ]);
          lessonCount += 1;
        }
        await Promise.allSettled([getGateTest(level.id), getFinalTest(level.id)]);
        completedLevels += 1;
        setProgress(Math.min(88, 8 + Math.round((completedLevels / Math.max(openLevels.length, 1)) * 80)));
      }
      await cacheMedia(media);
      const downloadedAt = new Date().toISOString();
      await setOfflineMeta('last-download', { downloadedAt, lessonCount, mediaCount: media.size });
      setProgress(100);
      setMessage(t('offline.downloadSuccess', { count: lessonCount }));
      await reload();
    } catch (error) {
      setMessage(error.response?.data?.detail || t('offline.downloadError'));
      setProgress(0);
    } finally {
      setDownloading(false);
    }
  };

  const clearData = async () => {
    if (!window.confirm(t('offline.clearConfirm'))) return;
    await clearCurrentUserOfflineData();
    setMessage('');
    setProgress(0);
    await reload();
  };

  const lastDownload = localStats.lastDownload?.downloadedAt
    ? new Intl.DateTimeFormat(locale, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(localStats.lastDownload.downloadedAt))
    : t('offline.never');

  return (
    <div className="animate-in offline-page">
      <div className="offline-page__hero">
        <div>
          <span className={`offline-network-pill ${online ? 'is-online' : 'is-offline'}`}>
            {online ? <Wifi size={14} /> : <WifiOff size={14} />}
            {online ? t('common.online') : t('common.offline')}
          </span>
          <h1>{t('offline.title')}</h1>
          <p>{t('offline.subtitle')}</p>
        </div>
        <div className="offline-page__hero-icon"><HardDriveDownload size={34} /></div>
      </div>

      <div className="offline-stat-grid">
        <Card className="offline-stat-card"><CloudDownload size={20} /><div><span>{t('offline.cachedLessons')}</span><strong>{localStats.lessonCount}</strong></div></Card>
        <Card className="offline-stat-card"><RefreshCw size={20} /><div><span>{t('offline.cachedRequests')}</span><strong>{localStats.queueCount}</strong></div></Card>
        <Card className="offline-stat-card"><Database size={20} /><div><span>{t('offline.lastDownload')}</span><strong className="offline-stat-card__date">{lastDownload}</strong><small>{formatBytes(localStats.approxBytes)}</small></div></Card>
      </div>

      <Card className="p-5 offline-download-card">
        <div className="offline-download-card__copy">
          <div className="feature-icon feature-icon--teal"><ShieldCheck size={20} /></div>
          <div><h2>{t('offline.readyTitle')}</h2><p>{t('offline.readyText')}</p><p>{t('offline.queueText')}</p></div>
        </div>
        {downloading && <div className="mt-4"><div className="flex justify-between text-xs mb-2"><span>{t('offline.downloading')}</span><b>{progress}%</b></div><ProgressBar value={progress} /></div>}
        {message && <p className="offline-page__message">{message}</p>}
        <div className="offline-page__actions">
          <Button onClick={downloadLessons} disabled={!online || downloading}>
            <CloudDownload size={16} /> {downloading ? t('offline.downloading') : t('offline.download')}
          </Button>
          <Button variant="secondary" onClick={syncNow} disabled={!online || syncing || localStats.queueCount === 0}>
            <RefreshCw size={16} className={syncing ? 'animate-spin' : ''} /> {t('offline.syncNow')}
          </Button>
          <Button variant="ghost" onClick={clearData} disabled={downloading}>
            <Trash2 size={16} /> {t('offline.clear')}
          </Button>
        </div>
      </Card>
    </div>
  );
}
