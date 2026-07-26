import { Smartphone } from 'lucide-react';
import { Card } from './ui';
import PWAInstallButton from './PWAInstallButton';

export default function PWAInstallCard({ roleLabel = 'platforma' }) {
  return (
    <Card className="p-4 mb-6 pwa-dashboard-card">
      <div className="pwa-dashboard-card__content">
        <div className="feature-icon feature-icon--olive"><Smartphone size={18} /></div>
        <div className="min-w-0 flex-1">
          <p className="font-display font-bold text-sm" style={{ color: 'var(--color-ink)' }}>Dasturni telefon ekraniga o‘rnating</p>
          <p className="text-xs mt-0.5" style={{ color: 'var(--color-muted)' }}>{roleLabel} panelini iPhone yoki Android’da alohida ilova kabi oching.</p>
        </div>
        <PWAInstallButton />
      </div>
    </Card>
  );
}
