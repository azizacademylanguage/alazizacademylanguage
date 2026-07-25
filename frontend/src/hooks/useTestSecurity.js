import { useEffect, useRef, useState } from 'react';

export default function useTestSecurity(limitMinutes = null) {
  const startedAt = useRef(Date.now());
  const [focusLosses, setFocusLosses] = useState(0);
  const [secondsLeft, setSecondsLeft] = useState(limitMinutes ? Number(limitMinutes) * 60 : null);
  const [timeExpired, setTimeExpired] = useState(false);

  useEffect(() => {
    startedAt.current = Date.now();
    setFocusLosses(0);
    setSecondsLeft(limitMinutes ? Number(limitMinutes) * 60 : null);
    setTimeExpired(false);
  }, [limitMinutes]);

  useEffect(() => {
    const onVisibility = () => {
      if (document.hidden) setFocusLosses(v => v + 1);
    };
    document.addEventListener('visibilitychange', onVisibility);
    return () => document.removeEventListener('visibilitychange', onVisibility);
  }, []);

  useEffect(() => {
    if (secondsLeft === null || timeExpired) return undefined;
    if (secondsLeft <= 0) {
      setTimeExpired(true);
      return undefined;
    }
    const timer = window.setInterval(() => setSecondsLeft(v => Math.max(0, v - 1)), 1000);
    return () => window.clearInterval(timer);
  }, [secondsLeft, timeExpired]);

  const reset = () => {
    startedAt.current = Date.now();
    setFocusLosses(0);
    setSecondsLeft(limitMinutes ? Number(limitMinutes) * 60 : null);
    setTimeExpired(false);
  };

  const getSecurityData = () => ({
    davomiylik_soniya: Math.max(1, Math.round((Date.now() - startedAt.current) / 1000)),
    sahifadan_chiqish_soni: focusLosses,
    vaqt_tugadi: timeExpired,
  });

  const formattedTime = secondsLeft === null
    ? null
    : `${String(Math.floor(secondsLeft / 60)).padStart(2, '0')}:${String(secondsLeft % 60).padStart(2, '0')}`;

  return { focusLosses, secondsLeft, formattedTime, timeExpired, getSecurityData, reset };
}
