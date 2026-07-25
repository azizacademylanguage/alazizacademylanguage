import { NavLink, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { GraduationCap, LogOut, Wrench } from 'lucide-react';
import { getPlatformHolati } from '../api/platform';

export default function DashboardLayout({ navItems, children, extraSidebarContent }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [platforma, setPlatforma] = useState(null);

  useEffect(() => {
    getPlatformHolati().then(setPlatforma).catch(() => {});
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const roleLabel = { admin: 'Admin', nazoratchi: 'Nazoratchi', oquvchi: "O'quvchi" }[user?.role] || '';

  const SidebarContent = () => (
    <>
      <div>
        <div className="flex items-center gap-2.5 mb-8 px-1">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 overflow-hidden"
            style={{ background: 'linear-gradient(135deg, var(--color-amber) 0%, var(--color-amber-dark) 100%)' }}
          >
            {platforma?.logo_url ? <img src={platforma.logo_url} alt="Logo" className="w-full h-full object-cover" /> : <GraduationCap size={16} color="white" strokeWidth={2.2} />}
          </div>
          <span className="font-display text-white font-bold text-[15px] tracking-tight truncate">{platforma?.platform_qisqa_nomi || "Bilim Yo'li"}</span>
        </div>

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
          Chiqish
        </button>
      </div>
    </>
  );

  return (
    <div className="min-h-screen flex" style={{ background: 'var(--color-paper)' }}>
      {/* Desktop sidebar */}
      <aside
        className="hidden lg:flex w-64 flex-shrink-0 flex-col justify-between p-5 sticky top-0 h-screen overflow-y-auto"
        style={{ background: 'linear-gradient(180deg, var(--color-forest) 0%, var(--color-teal) 62%, var(--color-amethyst) 125%)', boxShadow: '12px 0 40px rgba(8,41,0,0.08)' }}
      >
        <SidebarContent />
      </aside>

      {/* Mobile topbar — menyu tugmasisiz, navigatsiya pastda */}
      <header className="mobile-topbar lg:hidden">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="mobile-topbar__logo">
            {platforma?.logo_url ? <img src={platforma.logo_url} alt="Logo" className="w-full h-full object-cover" /> : <GraduationCap size={15} color="white" strokeWidth={2.3} />}
          </div>
          <div className="min-w-0">
            <p className="font-display text-white font-extrabold text-sm leading-tight truncate">{platforma?.platform_qisqa_nomi || "Bilim Yo'li"}</p>
            <p className="text-white/55 text-[10px] leading-tight truncate">{roleLabel}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="mobile-user-chip" title={user?.full_name || user?.username}>
            {(user?.ism?.[0] || user?.username?.[0] || '?').toUpperCase()}
          </div>
          <button
            type="button"
            onClick={handleLogout}
            className="mobile-logout-btn press"
            aria-label="Hisobdan chiqish"
            title="Chiqish"
          >
            <LogOut size={18} />
          </button>
        </div>
      </header>

      {/* Mobile bottom navigation */}
      <nav className="mobile-bottom-nav lg:hidden" aria-label="Asosiy navigatsiya">
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
              <span className="mobile-bottom-nav__icon">
                <item.icon size={20} strokeWidth={2.1} />
              </span>
              <span className="mobile-bottom-nav__label">{item.mobileLabel || item.label}</span>
            </NavLink>
          ))}
        </div>
      </nav>

      {/* Content */}
      <main className="flex-1 min-w-0 overflow-x-hidden">
        <div className="dashboard-content max-w-6xl mx-auto p-4 pt-20 sm:p-6 sm:pt-24 lg:p-8 lg:pt-8">
          {platforma?.texnik_rejim && (
            <div className="mb-5 flex items-start gap-3 p-4 rounded-2xl border" style={{ background: '#FFF7E8', borderColor: '#F2D59B', color: '#80633B' }}>
              <Wrench size={18} className="flex-shrink-0 mt-0.5" />
              <div><p className="font-semibold text-sm">Texnik rejim</p><p className="text-xs mt-1">{platforma.texnik_xabar}</p></div>
            </div>
          )}
          {children}
        </div>
      </main>
    </div>
  );
}
