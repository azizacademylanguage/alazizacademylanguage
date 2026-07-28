import { useEffect, useRef, useState } from 'react';
import { Check, ChevronDown, Languages } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

export default function LanguageSwitcher({ compact = false, dark = false }) {
  const { language, setLanguage, languages, t } = useLanguage();
  const [open, setOpen] = useState(false);
  const rootRef = useRef(null);
  const active = languages.find((item) => item.code === language) || languages[0];

  useEffect(() => {
    const closeOutside = (event) => { if (!rootRef.current?.contains(event.target)) setOpen(false); };
    const closeEscape = (event) => { if (event.key === 'Escape') setOpen(false); };
    document.addEventListener('pointerdown', closeOutside);
    document.addEventListener('keydown', closeEscape);
    return () => {
      document.removeEventListener('pointerdown', closeOutside);
      document.removeEventListener('keydown', closeEscape);
    };
  }, []);

  const choose = (code) => { setLanguage(code); setOpen(false); };

  return (
    <div ref={rootRef} className={`language-switcher ${compact ? 'language-switcher--compact' : ''} ${dark ? 'language-switcher--dark' : ''} ${open ? 'is-open' : ''}`} title={t('language.label')}>
      <button type="button" className="language-switcher__trigger" onClick={() => setOpen((value) => !value)} aria-haspopup="listbox" aria-expanded={open} aria-label={t('language.label')}>
        <span className="language-switcher__globe"><Languages size={compact ? 15 : 17} /></span>
        <span className="language-switcher__flag">{active.flag}</span>
        <span className="language-switcher__value">{compact ? active.short : active.label}</span>
        <ChevronDown className="language-switcher__chevron" size={14} />
      </button>
      {open && (
        <div className="language-switcher__menu" role="listbox" aria-label={t('language.label')}>
          <div className="language-switcher__menu-title">{t('language.label')}</div>
          {languages.map((item) => {
            const selected = item.code === language;
            return (
              <button type="button" key={item.code} role="option" aria-selected={selected} className={`language-switcher__option ${selected ? 'is-selected' : ''}`} onClick={() => choose(item.code)}>
                <span className="language-switcher__option-flag">{item.flag}</span>
                <span className="language-switcher__option-copy"><strong>{item.label}</strong><small>{item.short}</small></span>
                <span className="language-switcher__check">{selected && <Check size={15} />}</span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
