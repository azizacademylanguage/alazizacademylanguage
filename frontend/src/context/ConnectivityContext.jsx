import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { getOfflineStats } from '../utils/offlineDb';
import { syncOfflineQueue } from '../utils/offlineSync';

const ConnectivityContext = createContext(null);

export function ConnectivityProvider({ children }) {
  const [online, setOnline] = useState(() => navigator.onLine);
  const [stats, setStats] = useState({ cacheCount: 0, lessonCount: 0, queueCount: 0, lastDownload: null, approxBytes: 0 });
  const [syncing, setSyncing] = useState(false);
  const [lastSync, setLastSync] = useState(null);

  const refreshStats = useCallback(async () => {
    const next = await getOfflineStats().catch(() => stats);
    setStats(next);
    return next;
  }, []);

  const syncNow = useCallback(async () => {
    if (!navigator.onLine || syncing) return { synced: 0, failed: 0, remaining: stats.queueCount };
    setSyncing(true);
    try {
      const result = await syncOfflineQueue();
      setLastSync({ at: Date.now(), ...result });
      await refreshStats();
      return result;
    } finally {
      setSyncing(false);
    }
  }, [refreshStats, stats.queueCount, syncing]);

  useEffect(() => {
    const refresh = () => refreshStats();
    const handleOnline = () => {
      setOnline(true);
      setTimeout(() => syncNow(), 400);
    };
    const handleOffline = () => setOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    window.addEventListener('offline-cache-updated', refresh);
    window.addEventListener('offline-queue-updated', refresh);
    window.addEventListener('offline-meta-updated', refresh);
    window.addEventListener('offline-user-changed', refresh);
    refreshStats();
    if (navigator.onLine) setTimeout(() => syncNow(), 1000);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('offline-cache-updated', refresh);
      window.removeEventListener('offline-queue-updated', refresh);
      window.removeEventListener('offline-meta-updated', refresh);
      window.removeEventListener('offline-user-changed', refresh);
    };
  }, []);

  const value = useMemo(() => ({ online, stats, syncing, lastSync, refreshStats, syncNow }), [online, stats, syncing, lastSync, refreshStats, syncNow]);
  return <ConnectivityContext.Provider value={value}>{children}</ConnectivityContext.Provider>;
}

export const useConnectivity = () => {
  const value = useContext(ConnectivityContext);
  if (!value) throw new Error('useConnectivity must be used inside ConnectivityProvider');
  return value;
};
