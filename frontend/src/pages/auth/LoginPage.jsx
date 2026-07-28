import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';
import { Spinner } from '../../components/ui';
import LanguageSwitcher from '../../components/LanguageSwitcher';
import { GraduationCap, ArrowRight, BookOpen, Users, Building2, Eye, EyeOff } from 'lucide-react';

export default function LoginPage() {
  const { login, loading, error } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const user = await login(username, password);
      if (user.role === 'admin') navigate('/admin');
      else if (user.role === 'nazoratchi') navigate('/nazoratchi');
      else navigate('/oquvchi');
    } catch {
      // AuthContext shows the error.
    }
  };

  const heroLines = t('login.heroTitle').split('\n');

  return (
    <div className="min-h-screen flex" style={{ background: 'var(--color-paper)' }}>
      <div
        className="hidden lg:flex lg:w-5/12 flex-col justify-between p-12 relative overflow-hidden"
        style={{ background: 'linear-gradient(160deg, var(--color-forest) 0%, var(--color-forest-dark) 100%)' }}
      >
        <div className="absolute inset-0 opacity-[0.06]" style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)', backgroundSize: '28px 28px' }} />
        <div className="absolute -top-24 -right-24 w-96 h-96 rounded-full opacity-[0.08] animate-float" style={{ background: 'var(--color-amber)' }} />
        <div className="absolute bottom-0 left-0 w-72 h-72 rounded-full opacity-[0.06] animate-float" style={{ background: 'var(--color-moss)', animationDelay: '1s' }} />

        <div className="relative z-10 flex items-center justify-between gap-3 animate-in-fast">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg, var(--color-amber) 0%, var(--color-amber-dark) 100%)', boxShadow: '0 4px 16px rgba(199,130,42,0.35)' }}>
              <GraduationCap size={22} color="white" strokeWidth={2.2} />
            </div>
            <span className="font-display text-white text-lg font-bold tracking-tight">{t('appName')}</span>
          </div>
          <LanguageSwitcher dark />
        </div>

        <div className="relative z-10">
          <h1 className="font-display text-4xl font-bold text-white leading-tight mb-4 animate-in-fast stagger-1">
            {heroLines.map((line, index) => <span key={line}>{line}{index < heroLines.length - 1 && <br />}</span>)}
          </h1>
          <p className="text-white/70 text-base leading-relaxed max-w-sm animate-in-fast stagger-2">{t('login.heroDescription')}</p>
        </div>

        <div className="relative z-10 flex items-center gap-6 animate-in-fast stagger-3">
          {[
            { icon: Building2, label: t('login.branches') },
            { icon: Users, label: t('login.supervisors') },
            { icon: BookOpen, label: t('login.subjects') },
          ].map((item) => (
            <div key={item.label} className="flex items-center gap-2 text-white/50 text-sm"><item.icon size={15} />{item.label}</div>
          ))}
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-6 sm:p-8 relative">
        <div className="absolute top-5 right-5 lg:hidden"><LanguageSwitcher /></div>
        <div className="w-full max-w-sm animate-in">
          <div className="lg:hidden flex items-center gap-2 mb-8 justify-center animate-pop">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg, var(--color-forest) 0%, var(--color-forest-dark) 100%)' }}>
              <GraduationCap size={18} color="white" />
            </div>
            <span className="font-display text-lg font-bold" style={{ color: 'var(--color-forest)' }}>{t('appName')}</span>
          </div>

          <h2 className="font-display text-2xl font-bold mb-1" style={{ color: 'var(--color-ink)' }}>{t('login.welcome')}</h2>
          <p className="text-sm mb-8" style={{ color: '#8A8371' }}>{t('login.description')}</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="animate-in-fast stagger-1">
              <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--color-ink)' }}>{t('login.username')}</label>
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="username"
                autoComplete="username"
                className="w-full px-4 py-2.5 rounded-xl border text-sm transition-all"
                style={{ borderColor: 'var(--color-line)', background: 'white' }}
                onFocus={(e) => { e.target.style.borderColor = 'var(--color-forest-light)'; e.target.style.boxShadow = '0 0 0 3px rgba(47,110,95,0.12)'; }}
                onBlur={(e) => { e.target.style.borderColor = 'var(--color-line)'; e.target.style.boxShadow = 'none'; }}
              />
            </div>
            <div className="animate-in-fast stagger-2">
              <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--color-ink)' }}>{t('login.password')}</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  autoComplete="current-password"
                  className="w-full px-4 py-2.5 pr-11 rounded-xl border text-sm transition-all"
                  style={{ borderColor: 'var(--color-line)', background: 'white' }}
                  onFocus={(e) => { e.target.style.borderColor = 'var(--color-forest-light)'; e.target.style.boxShadow = '0 0 0 3px rgba(47,110,95,0.12)'; }}
                  onBlur={(e) => { e.target.style.borderColor = 'var(--color-line)'; e.target.style.boxShadow = 'none'; }}
                />
                <button type="button" onClick={() => setShowPassword((v) => !v)} className="absolute right-3.5 top-1/2 -translate-y-1/2 press" style={{ color: '#9C9584' }} tabIndex={-1}>
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {error && <div className="text-sm px-3 py-2.5 rounded-xl animate-pop" style={{ background: '#FBEAE8', color: 'var(--color-red)' }}>{error}</div>}

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl font-semibold text-sm text-white transition-all disabled:opacity-60 press hover:brightness-105 hover:-translate-y-0.5 animate-in-fast stagger-3"
              style={{ background: 'linear-gradient(135deg, var(--color-forest) 0%, var(--color-forest-dark) 100%)', boxShadow: '0 4px 14px rgba(27,75,67,0.3)' }}
            >
              {loading && <Spinner size={15} color="white" />}
              {loading ? t('login.submitting') : t('login.submit')}
              {!loading && <ArrowRight size={16} />}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
