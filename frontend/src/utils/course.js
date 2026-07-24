export const cleanLevelName = (value = '') => String(value)
  .replace(/^\s*\d+[.)-]?\s*/, '')
  .replace(/\s*[—–-]\s*\d+\s*%?\s*[—–-]\s*\d+\s*%?\s*$/, '')
  .replace(/\s+\d+\s*%\s*$/, '')
  .trim();

export const languageMeta = (name = '') => {
  const lower = name.toLowerCase();
  if (lower.includes('rus') || lower.includes('russia')) {
    return { code: 'RU', flag: '🇷🇺', label: 'Rus tili', accent: 'amethyst' };
  }
  if (lower.includes('kore')) {
    return { code: 'KR', flag: '🇰🇷', label: 'Koreys tili', accent: 'olive' };
  }
  return { code: 'GB', flag: '🇬🇧', label: 'English', accent: 'teal' };
};
