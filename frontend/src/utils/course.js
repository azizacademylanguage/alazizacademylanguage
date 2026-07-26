export const cleanLevelName = (value = '') => String(value)
  .replace(/^\s*\d+[.)-]?\s*/, '')
  .replace(/\s*[—–-]\s*\d+\s*%?\s*[—–-]\s*\d+\s*%?\s*$/, '')
  .replace(/\s+\d+\s*%\s*$/, '')
  .trim();

export const languageMeta = (name = '') => {
  const lower = name.toLowerCase();
  if (lower.includes('rus')) return { code: 'RU', flag: '🇷🇺', label: 'Rus tili', accent: 'amethyst' };
  if (lower.includes('kore')) return { code: 'KR', flag: '🇰🇷', label: 'Koreys tili', accent: 'olive' };
  if (lower.includes('matem')) return { code: 'MAT', flag: '∑', label: 'Matematika', accent: 'teal' };
  if (lower.includes('ona tili') || lower.includes("o'zbek")) return { code: 'ONA', flag: '📝', label: 'Ona tili', accent: 'jungle' };
  if (lower.includes('tarix')) return { code: 'TAR', flag: '🏛️', label: 'Tarix', accent: 'amber' };
  if (lower.includes('huquq')) return { code: 'HUQ', flag: '⚖️', label: 'Huquq', accent: 'amethyst' };
  if (lower === 'it' || lower.includes('axborot texnolog')) return { code: 'IT', flag: '💻', label: 'IT', accent: 'teal' };
  if (lower.includes('kompyuter')) return { code: 'PC', flag: '🖥️', label: 'Kompyuter', accent: 'olive' };
  if (lower.includes('arab')) return { code: 'AR', flag: '🇸🇦', label: 'Arab tili', accent: 'amber' };
  if (lower.includes('turk')) return { code: 'TR', flag: '🇹🇷', label: 'Turk tili', accent: 'amethyst' };
  return { code: 'GB', flag: '🇬🇧', label: 'English', accent: 'teal' };
};
