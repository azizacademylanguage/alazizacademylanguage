import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { GraduationCap, LogOut } from 'lucide-react';
import NotificationBell from './NotificationBell';
import PWAInstallButton from './PWAInstallButton';
import LanguageSwitcher from './LanguageSwitcher';
import { useLanguage } from '../context/LanguageContext';

export default function DashboardLayout({ navItems, children, extraSidebarContent }) {
  const { user, logout } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const roleLabel = user?.role ? t(`role.${user.role}`) : '';

  const SidebarContent = () => (
    <>
      <div>
        <div className="flex items-center gap-2.5 mb-6 px-1">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
            style={{ background: 'linear-gradient(135deg, var(--color-amber) 0%, var(--color-amber-dark) 100%)' }}
          >
            <GraduationCap size={16} color="white" strokeWidth={2.2} />
          </div>
          <span className="font-display text-white font-bold text-[15px] tracking-tight">{t('appName')}</span>
        </div>

        <div className="mb-4 px-1"><LanguageSwitcher dark /></div>

        <nav className="space-y-1">
          {navItems.map((item, idx) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 animate-slide ${
                  isActive ? 'text-white' : 'text-white/60 hover:text-white/90 hover:bg-white/5'
                }`
              }
              style={({ isActive }) => ({
                background: isActive ? 'linear-gradient(135deg, rgba(255,255,255,0.20), rgba(255,255,255,0.10))' : 'transparent',
                boxShadow: isActive ? '0 8px 20px rgba(0,0,0,0.14)' : 'none',
                animationDelay: `${idx * 40}ms`,
              })}
            >
              <item.icon size={17} strokeWidth={2} className="transition-transform group-hover:scale-110" />
              {item.label}
            </NavLink>
          ))}
        </nav>

        {extraSidebarContent}
      </div>

      <div className="border-t pt-4" style={{ borderColor: 'rgba(255,255,255,0.12)' }}>
        <div className="px-1 mb-3 flex items-center gap-2.5">
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 font-display font-bold text-xs text-white"
            style={{ background: 'rgba(255,255,255,0.15)' }}
          >
            {(user?.ism?.[0] || user?.username?.[0] || '?').toUpperCase()}
          </div>
          <div className="min-w-0">
            <p className="text-white text-sm font-semibold truncate">{user?.full_name || user?.username}</p>
            <p className="text-white/50 text-xs truncate">{roleLabel}{user?.filial ? ` · ${user.filial.nomi}` : ''}</p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-xl text-sm text-white/70 hover:text-white hover:bg-white/10 transition-all press"
        >
          <LogOut size={16} />
          {t('common.logout')}
        </button>
      </div>
    </>
  );

  return (
    <div className="min-h-screen flex" style={{ background: 'var(--color-paper)' }}>
      <aside
        className="hidden lg:flex w-64 flex-shrink-0 flex-col justify-between p-5 sticky top-0 h-screen"
        style={{ background: 'linear-gradient(180deg, var(--color-forest) 0%, var(--color-teal) 62%, var(--color-amethyst) 125%)', boxShadow: '12px 0 40px rgba(8,41,0,0.08)' }}
      >
        <SidebarContent />
      </aside>

      <header className="mobile-topbar lg:hidden">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="mobile-topbar__logo"><GraduationCap size={15} color="white" strokeWidth={2.3} /></div>
          <div className="min-w-0">
            <p className="font-display text-white font-extrabold text-sm leading-tight truncate">{t('appName')}</p>
            <p className="text-white/55 text-[10px] leading-tight truncate">{roleLabel}</p>
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          <LanguageSwitcher compact dark />
          <PWAInstallButton compact />
          {user?.role === 'oquvchi' && <NotificationBell mobile />}
          <div className="mobile-user-chip" title={user?.full_name || user?.username}>
            {(user?.ism?.[0] || user?.username?.[0] || '?').toUpperCase()}
          </div>
          <button
            type="button"
            onClick={handleLogout}
            className="mobile-logout-btn press"
            aria-label={t('common.logout')}
            title={t('common.logout')}
          >
            <LogOut size={18} />
          </button>
        </div>
      </header>

      <nav className="mobile-bottom-nav lg:hidden" aria-label={t('nav.dashboard')}>
        <div className="mobile-bottom-nav__scroller">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              aria-label={item.label}
              title={item.label}
              className={({ isActive }) => `mobile-bottom-nav__item ${isActive ? 'is-active' : ''}`}
            >
              <span className="mobile-bottom-nav__icon"><item.icon size={20} strokeWidth={2.1} /></span>
              <span className="mobile-bottom-nav__label">{item.mobileLabel || item.label}</span>
            </NavLink>
          ))}
        </div>
      </nav>

      <main className="flex-1 min-w-0 overflow-x-hidden relative">
        <div className="desktop-quick-actions hidden lg:flex">
          <LanguageSwitcher compact />
          <PWAInstallButton compact />
          {user?.role === 'oquvchi' && <NotificationBell />}
        </div>
        <div className="dashboard-content max-w-6xl mx-auto p-4 pt-20 sm:p-6 sm:pt-24 lg:p-8 lg:pt-8">
          {children}
        </div>
      </main>
    </div>
  );
}
