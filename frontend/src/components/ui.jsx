import { createPortal } from 'react-dom';
import { useEffect } from 'react';

export function Card({ children, className = '', hover = false, style = {} }) {
  return (
    <div
      className={`rounded-2xl border bg-white ${hover ? 'hover-lift cursor-pointer' : ''} ${className}`}
      style={{ borderColor: 'var(--color-line)', boxShadow: 'var(--shadow-sm)', ...style }}
    >
      {children}
    </div>
  );
}

export function StatCard({ label, value, sub, icon: Icon, accent = 'forest', delay = 0 }) {
  const gradients = {
    forest: 'linear-gradient(135deg, var(--color-forest) 0%, var(--color-teal) 100%)',
    amber: 'linear-gradient(135deg, var(--color-olive) 0%, var(--color-jungle) 100%)',
    moss: 'linear-gradient(135deg, var(--color-jungle) 0%, var(--color-teal) 100%)',
    teal: 'linear-gradient(135deg, var(--color-teal) 0%, var(--color-jungle) 100%)',
    jungle: 'linear-gradient(135deg, var(--color-jungle) 0%, var(--color-forest) 100%)',
    olive: 'linear-gradient(135deg, var(--color-olive) 0%, var(--color-jungle) 100%)',
    amethyst: 'linear-gradient(135deg, var(--color-amethyst) 0%, var(--color-teal) 100%)',
  };
  return (
    <div
      className="animate-in-fast hover-lift rounded-2xl border bg-white p-5 flex items-start justify-between overflow-hidden relative"
      style={{ borderColor: 'var(--color-line)', boxShadow: 'var(--shadow-sm)', animationDelay: `${delay}ms` }}
    >
      <div className="relative z-10">
        <p className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: '#9C9584' }}>{label}</p>
        <p className="font-display text-3xl font-extrabold tabular-nums" style={{ color: 'var(--color-ink)' }}>{value}</p>
        {sub && <p className="text-xs mt-1.5" style={{ color: '#9C9584' }}>{sub}</p>}
      </div>
      {Icon && (
        <div
          className="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0 relative z-10"
          style={{ background: gradients[accent], boxShadow: '0 4px 12px rgba(27,75,67,0.25)' }}
        >
          <Icon size={19} color="white" strokeWidth={2.2} />
        </div>
      )}
      <div className="absolute -right-6 -bottom-6 w-24 h-24 rounded-full opacity-[0.05]" style={{ background: gradients[accent] }} />
    </div>
  );
}

export function Button({ children, variant = 'primary', className = '', size = 'md', loading = false, ...props }) {
  const base = 'press inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition-all disabled:opacity-50 disabled:pointer-events-none';
  const sizes = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2.5 text-sm',
    lg: 'px-5 py-3 text-base',
  };
  const variants = {
    primary: {
      background: 'linear-gradient(135deg, var(--color-forest) 0%, var(--color-teal) 100%)',
      color: 'white',
      boxShadow: '0 8px 18px rgba(8,99,117,0.22)',
    },
    secondary: { background: 'white', color: 'var(--color-ink)', border: '1px solid var(--color-line)' },
    danger: { background: '#FBEAE8', color: 'var(--color-red)' },
    ghost: { background: 'transparent', color: 'var(--color-forest)' },
    amber: {
      background: 'linear-gradient(135deg, var(--color-olive) 0%, var(--color-jungle) 100%)',
      color: 'white',
      boxShadow: '0 8px 18px rgba(59,100,2,0.22)',
    },
  };
  return (
    <button
      type={props.type || 'button'}
      className={`${base} ${sizes[size]} ${className} hover:brightness-105 hover:-translate-y-0.5`}
      style={variants[variant]}
      disabled={loading || props.disabled}
      {...props}
    >
      {loading && <Spinner size={14} color={variant === 'secondary' || variant === 'ghost' ? 'var(--color-forest)' : 'white'} />}
      {children}
    </button>
  );
}

export function Spinner({ size = 16, color = 'currentColor' }) {
  return (
    <svg className="animate-spin-slow" width={size} height={size} viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="12" r="9" stroke={color} strokeWidth="3" opacity="0.25" />
      <path d="M21 12a9 9 0 0 0-9-9" stroke={color} strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}

export function Badge({ children, tone = 'neutral' }) {
  const tones = {
    neutral: { background: 'var(--color-paper-warm)', color: '#6B6455' },
    success: { background: '#E4EFE6', color: '#2F6E42' },
    warning: { background: 'var(--color-amber-light)', color: '#8A5A1A' },
    danger: { background: '#FBEAE8', color: 'var(--color-red)' },
    forest: { background: 'rgba(27,75,67,0.1)', color: 'var(--color-forest)' },
  };
  return (
    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold whitespace-nowrap" style={tones[tone]}>
      {children}
    </span>
  );
}

/**
 * Modal — document.body ga to'g'ridan-to'g'ri portal orqali chiqariladi.
 * Bu ota-elementlardagi overflow/transform/z-index qatlamlaridan mustaqil
 * ishlaydi, shuning uchun "modal ochilmayapti / tugma bosilmayapti" kabi
 * stacking-context muammolari butunlay bartaraf etiladi.
 */
export function Modal({ open, onClose, title, subtitle, children, wide = false }) {
  useEffect(() => {
    if (!open) return;
    const onKeyDown = (e) => { if (e.key === 'Escape') onClose?.(); };
    document.addEventListener('keydown', onKeyDown);
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKeyDown);
      document.body.style.overflow = prevOverflow;
    };
  }, [open, onClose]);

  if (!open) return null;

  return createPortal(
    <div className="modal-overlay" onMouseDown={onClose}>
      <div
        className="modal-box"
        style={{ maxWidth: wide ? 520 : 440 }}
        onMouseDown={(e) => e.stopPropagation()}
      >
        <div className="p-6 sm:p-7">
          <h3 className="font-display text-lg font-bold" style={{ color: 'var(--color-ink)' }}>{title}</h3>
          {subtitle && <p className="text-sm mt-1 mb-4" style={{ color: '#8A8371' }}>{subtitle}</p>}
          {!subtitle && <div className="mb-4" />}
          {children}
        </div>
      </div>
    </div>,
    document.body
  );
}

export function Input({ label, hint, error, ...props }) {
  return (
    <div>
      {label && <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--color-ink)' }}>{label}</label>}
      <input
        className="w-full px-3.5 py-2.5 rounded-xl border text-sm transition-all outline-none"
        style={{ borderColor: error ? 'var(--color-red)' : 'var(--color-line)' }}
        onFocus={(e) => { if (!error) e.target.style.borderColor = 'var(--color-forest-light)'; e.target.style.boxShadow = '0 0 0 3px rgba(47,110,95,0.12)'; }}
        onBlur={(e) => { e.target.style.borderColor = error ? 'var(--color-red)' : 'var(--color-line)'; e.target.style.boxShadow = 'none'; }}
        {...props}
      />
      {hint && !error && <p className="text-xs mt-1" style={{ color: '#9C9584' }}>{hint}</p>}
      {error && <p className="text-xs mt-1" style={{ color: 'var(--color-red)' }}>{error}</p>}
    </div>
  );
}

export function Select({ label, children, error, ...props }) {
  return (
    <div>
      {label && <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--color-ink)' }}>{label}</label>}
      <select
        className="w-full px-3.5 py-2.5 rounded-xl border text-sm bg-white transition-all outline-none cursor-pointer"
        style={{ borderColor: error ? 'var(--color-red)' : 'var(--color-line)' }}
        {...props}
      >
        {children}
      </select>
      {error && <p className="text-xs mt-1" style={{ color: 'var(--color-red)' }}>{error}</p>}
    </div>
  );
}

export function Textarea({ label, hint, ...props }) {
  return (
    <div>
      {label && <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--color-ink)' }}>{label}</label>}
      <textarea
        className="w-full px-3.5 py-2.5 rounded-xl border text-sm transition-all outline-none"
        style={{ borderColor: 'var(--color-line)' }}
        onFocus={(e) => { e.target.style.borderColor = 'var(--color-forest-light)'; e.target.style.boxShadow = '0 0 0 3px rgba(47,110,95,0.12)'; }}
        onBlur={(e) => { e.target.style.borderColor = 'var(--color-line)'; e.target.style.boxShadow = 'none'; }}
        {...props}
      />
      {hint && <p className="text-xs mt-1" style={{ color: '#9C9584' }}>{hint}</p>}
    </div>
  );
}

export function EmptyState({ title, description, action, icon: Icon }) {
  return (
    <div className="text-center py-16 px-6 animate-fade">
      {Icon && (
        <div className="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-4 animate-float" style={{ background: 'var(--color-paper-warm)' }}>
          <Icon size={24} style={{ color: 'var(--color-moss)' }} />
        </div>
      )}
      <p className="font-display font-bold text-base mb-1" style={{ color: 'var(--color-ink)' }}>{title}</p>
      <p className="text-sm mb-5 max-w-xs mx-auto" style={{ color: '#8A8371' }}>{description}</p>
      {action}
    </div>
  );
}

export function ProgressBar({ value, tone = 'forest', animated = true }) {
  const gradients = {
    forest: 'linear-gradient(90deg, var(--color-forest) 0%, var(--color-forest-light) 100%)',
    amber: 'linear-gradient(90deg, var(--color-amber-dark) 0%, var(--color-amber) 100%)',
  };
  return (
    <div className="w-full h-2 rounded-full overflow-hidden" style={{ background: 'var(--color-paper-warm)' }}>
      <div
        className={animated ? 'h-full rounded-full transition-all duration-700 ease-out' : 'h-full rounded-full'}
        style={{ width: `${Math.min(100, Math.max(0, value))}%`, background: gradients[tone] }}
      />
    </div>
  );
}

export function Skeleton({ className = '' }) {
  return <div className={`skeleton rounded-lg ${className}`} />;
}

export function IconButton({ icon: Icon, onClick, tone = 'default', size = 15, title }) {
  const tones = {
    default: 'text-gray-300 hover:text-gray-500',
    danger: 'text-gray-300 hover:text-red-500',
    forest: 'text-gray-300 hover:text-[var(--color-forest)]',
  };
  return (
    <button type="button" onClick={onClick} title={title} className={`transition-colors press ${tones[tone]}`}>
      <Icon size={size} />
    </button>
  );
}

/** Toast — vaqtinchalik xabar, ekran o'ng-pastida chiqadi (portal orqali) */
export function Toast({ message, tone = 'success', onClose }) {
  useEffect(() => {
    const t = setTimeout(() => onClose?.(), 3500);
    return () => clearTimeout(t);
  }, [onClose]);

  if (!message) return null;

  const tones = {
    success: { background: '#1B4B43', icon: '✓' },
    error: { background: '#B4453A', icon: '!' },
  };
  const t = tones[tone];

  return createPortal(
    <div
      className="fixed bottom-5 right-5 z-[10001] flex items-center gap-3 px-4 py-3 rounded-xl text-white text-sm font-medium animate-pop"
      style={{ background: t.background, boxShadow: 'var(--shadow-lg)', maxWidth: 340 }}
    >
      <span className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold" style={{ background: 'rgba(255,255,255,0.25)' }}>
        {t.icon}
      </span>
      {message}
    </div>,
    document.body
  );
}
