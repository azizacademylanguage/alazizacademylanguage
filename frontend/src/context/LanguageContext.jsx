import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { LANGUAGES, translations } from '../i18n/translations';

const STORAGE_KEY = 'alaziz_interface_language';
const LanguageContext = createContext(null);

function resolveInitialLanguage() {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (translations[stored]) return stored;
  const browser = (navigator.language || 'uz').slice(0, 2).toLowerCase();
  return translations[browser] ? browser : 'uz';
}

function interpolate(value, params = {}) {
  return String(value).replace(/\{(\w+)\}/g, (_, key) => params[key] ?? `{${key}}`);
}

export function LanguageProvider({ children }) {
  const [language, setLanguageState] = useState(resolveInitialLanguage);

  const setLanguage = useCallback((nextLanguage) => {
    if (!translations[nextLanguage]) return;
    localStorage.setItem(STORAGE_KEY, nextLanguage);
    setLanguageState(nextLanguage);
  }, []);

  useEffect(() => {
    document.documentElement.lang = language;
    document.documentElement.dir = 'ltr';
  }, [language]);

  const t = useCallback((key, params) => {
    const value = translations[language]?.[key] ?? translations.uz[key] ?? key;
    return interpolate(value, params);
  }, [language]);

  const value = useMemo(() => ({
    language,
    setLanguage,
    t,
    languages: LANGUAGES,
    locale: LANGUAGES.find((item) => item.code === language)?.locale || 'uz-UZ',
  }), [language, setLanguage, t]);

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) throw new Error('useLanguage must be used inside LanguageProvider');
  return context;
};
