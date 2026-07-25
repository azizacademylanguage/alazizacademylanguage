import { useEffect, useState } from 'react';
import { Download, Smartphone } from 'lucide-react';
import { Button, Card } from './ui';

export default function PwaInstallCard() {
  const [promptEvent, setPromptEvent] = useState(() => window.__alazizPwaInstallPrompt || null);
  const [installed, setInstalled] = useState(false);

  useEffect(() => {
    const standalone = window.matchMedia?.('(display-mode: standalone)').matches || window.navigator.standalone === true;
    setInstalled(Boolean(standalone));

    const onPrompt = (event) => {
      event.preventDefault?.();
      setPromptEvent(window.__alazizPwaInstallPrompt || event);
    };
    const onInstalled = () => {
      setInstalled(true);
      setPromptEvent(null);
    };

    window.addEventListener('beforeinstallprompt', onPrompt);
    window.addEventListener('alaziz-pwa-install-available', onPrompt);
    window.addEventListener('appinstalled', onInstalled);
    return () => {
      window.removeEventListener('beforeinstallprompt', onPrompt);
      window.removeEventListener('alaziz-pwa-install-available', onPrompt);
      window.removeEventListener('appinstalled', onInstalled);
    };
  }, []);

  if (installed || !promptEvent) return null;

  const install = async () => {
    await promptEvent.prompt();
    const choice = await promptEvent.userChoice;
    if (choice?.outcome === 'accepted') setPromptEvent(null);
  };

  return (
    <Card className="p-4 mb-6 border flex flex-col sm:flex-row sm:items-center gap-4" style={{ background: '#F1F7F4', borderColor: '#CDE2D7' }}>
      <div className="w-11 h-11 rounded-2xl flex items-center justify-center flex-shrink-0" style={{ background: '#DDEEE5' }}>
        <Smartphone size={22} />
      </div>
      <div className="min-w-0 flex-1">
        <p className="font-display font-bold">Platformani telefonga o‘rnating</p>
        <p className="text-sm mt-1" style={{ color: 'var(--color-muted)' }}>Sayt bosh ekranda ilova kabi ochiladi va tezroq ishlaydi.</p>
      </div>
      <Button onClick={install}><Download size={16} /> O‘rnatish</Button>
    </Card>
  );
}
