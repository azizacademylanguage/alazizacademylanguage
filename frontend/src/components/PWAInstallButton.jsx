import { useEffect, useState } from 'react';
import { Download, CheckCircle2 } from 'lucide-react';

const isStandalone = () => window.matchMedia?.('(display-mode: standalone)').matches || window.navigator.standalone === true;

export default function PWAInstallButton({ compact = false }) {
  const [prompt, setPrompt] = useState(window.__pwaInstallPrompt || null);
  const [installed, setInstalled] = useState(isStandalone());

  useEffect(() => {
    const ready = (event) => setPrompt(event.detail || window.__pwaInstallPrompt || null);
    const done = () => { setInstalled(true); setPrompt(null); };
    window.addEventListener('pwa-install-ready', ready);
    window.addEventListener('appinstalled', done);
    return () => {
      window.removeEventListener('pwa-install-ready', ready);
      window.removeEventListener('appinstalled', done);
    };
  }, []);

  const install = async () => {
    const deferred = prompt || window.__pwaInstallPrompt;
    if (deferred) {
      deferred.prompt();
      await deferred.userChoice.catch(() => null);
      window.__pwaInstallPrompt = null;
      setPrompt(null);
      return;
    }
    const ios = /iphone|ipad|ipod/i.test(navigator.userAgent);
    alert(ios
      ? "Safari pastidagi Share tugmasini bosing va ‘Add to Home Screen’ni tanlang."
      : "Brauzer menyusidan ‘Install app’ yoki ‘Add to Home screen’ni tanlang.");
  };

  if (installed) {
    return compact ? null : <span className="pwa-installed"><CheckCircle2 size={15} /> Ilova o‘rnatilgan</span>;
  }

  return (
    <button type="button" onClick={install} className={compact ? 'pwa-install-compact press' : 'pwa-install-button press'} title="Ilovani telefonga o‘rnatish">
      <Download size={compact ? 17 : 18} /> {!compact && <span>Ilovani o‘rnatish</span>}
    </button>
  );
}
