import { useEffect, useState } from 'react';
import { getCoinlarim } from '../api/coinShop';
import { Coins } from 'lucide-react';

export default function CoinBadge() {
  const [balans, setBalans] = useState(null);

  useEffect(() => {
    getCoinlarim().then((d) => setBalans(d.balans)).catch(() => {});
    const onCoinUpdated = (event) => {
      if (typeof event.detail === 'number') setBalans(event.detail);
      else getCoinlarim().then((d) => setBalans(d.balans)).catch(() => {});
    };
    window.addEventListener('coin-updated', onCoinUpdated);
    return () => window.removeEventListener('coin-updated', onCoinUpdated);
  }, []);

  if (balans === null) return null;

  return (
    <div
      className="mt-4 flex items-center gap-2.5 px-3 py-2.5 rounded-xl animate-pop"
      style={{ background: 'rgba(199,130,42,0.15)' }}
    >
      <div
        className="w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0"
        style={{ background: 'linear-gradient(135deg, var(--color-amber) 0%, var(--color-amber-dark) 100%)' }}
      >
        <Coins size={14} color="white" />
      </div>
      <div>
        <p className="text-white text-sm font-bold tabular-nums leading-tight">{balans}</p>
        <p className="text-white/50 text-[10px] leading-tight">coin</p>
      </div>
    </div>
  );
}
