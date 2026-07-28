import { Languages } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

export default function LanguageSwitcher({ compact = false, dark = false }) {
  const { language, setLanguage, languages, t } = useLanguage();

  return (
    <label
      className={`language-switcher ${compact ? 'language-switcher--compact' : ''} ${dark ? 'language-switcher--dark' : ''}`}
      title={t('language.label')}
    >
      <Languages size={compact ? 15 : 16} aria-hidden="true" />
      <select
        value={language}
        onChange={(event) => setLanguage(event.target.value)}
        aria-label={t('language.label')}
      >
        {languages.map((item) => (
          <option key={item.code} value={item.code}>{compact ? item.short : item.label}</option>
        ))}
      </select>
    </label>
  );
}
