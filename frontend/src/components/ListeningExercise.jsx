import { useEffect, useMemo, useState } from 'react';
import { Card, Button, ProgressBar, Skeleton } from './ui';
import { Headphones, Volume2, ChevronLeft, ChevronRight, CheckCircle2, RotateCcw } from 'lucide-react';
import { getListening, submitListening } from '../api/engagement';

export default function ListeningExercise({ darsId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    setLoading(true);
    getListening(darsId)
      .then((response) => { if (active) setData(response); })
      .catch((err) => {
        if (active && err.response?.status !== 404) setError(err.response?.data?.detail || 'Listening yuklanmadi.');
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; window.speechSynthesis?.cancel(); };
  }, [darsId]);

  const questions = data?.savollar || [];
  const question = questions[index];
  const answeredCount = useMemo(() => Object.keys(answers).length, [answers]);

  const speak = () => {
    if (!question || !('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(question.audio_matn);
    utterance.lang = question.til_kodi || 'en-US';
    utterance.rate = 0.78;
    utterance.pitch = 1;
    window.speechSynthesis.speak(utterance);
  };

  const choose = (value) => {
    setAnswers((prev) => ({ ...prev, [question.id]: value }));
    if (index < questions.length - 1) setTimeout(() => setIndex((v) => v + 1), 220);
  };

  const submit = async () => {
    setSubmitting(true);
    setError('');
    try {
      const payload = questions.map((q) => ({ savol: q.id, javob: answers[q.id] || '' }));
      setResult(await submitListening(darsId, payload));
    } catch (err) {
      setError(err.response?.data?.detail || 'Natijani yuborishda xatolik yuz berdi.');
    } finally {
      setSubmitting(false);
    }
  };

  const restart = () => {
    setAnswers({});
    setIndex(0);
    setResult(null);
  };

  if (loading) return <Skeleton className="h-72 w-full mb-5" />;
  if (!questions.length) return null;

  return (
    <Card className="p-5 mb-5 listening-card animate-in-fast">
      <div className="flex items-start justify-between gap-3 mb-4">
        <div className="flex items-center gap-3">
          <div className="feature-icon feature-icon--teal"><Headphones size={19} /></div>
          <div>
            <h3 className="font-display font-extrabold text-base" style={{ color: 'var(--color-ink)' }}>Listening mashqi</h3>
            <p className="text-xs mt-0.5" style={{ color: 'var(--color-muted)' }}>Ovozni tinglang va to‘g‘ri tarjimani tanlang.</p>
          </div>
        </div>
        <span className="feature-counter">{result ? `${result.foiz}%` : `${answeredCount}/${questions.length}`}</span>
      </div>

      {result ? (
        <div className="listening-result animate-pop">
          <div className={`score-ring ${result.otdi ? 'is-success' : 'is-warning'}`}>
            <strong>{Math.round(Number(result.foiz))}%</strong>
            <span>{result.togri_soni}/{result.jami_soni}</span>
          </div>
          <div className="flex-1">
            <h4 className="font-display font-bold" style={{ color: 'var(--color-ink)' }}>
              {result.otdi ? 'Listening muvaffaqiyatli tugadi!' : 'Yana bir marta urinib ko‘ring'}
            </h4>
            <p className="text-sm mt-1" style={{ color: 'var(--color-muted)' }}>{result.xabar}</p>
            <Button size="sm" variant="secondary" onClick={restart} className="mt-3"><RotateCcw size={14} /> Qayta ishlash</Button>
          </div>
        </div>
      ) : (
        <>
          <ProgressBar value={(answeredCount / questions.length) * 100} />
          <div className="listening-question mt-5">
            <div className="flex items-center justify-between gap-3 mb-4">
              <span className="text-xs font-bold uppercase tracking-wider" style={{ color: 'var(--color-teal)' }}>Savol {index + 1}</span>
              <button type="button" onClick={speak} className="listen-button press">
                <Volume2 size={18} /> Ovozni eshitish
              </button>
            </div>
            <p className="font-display font-bold text-base mb-4" style={{ color: 'var(--color-ink)' }}>{question.savol}</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {question.variantlar.map((option) => {
                const selected = answers[question.id] === option;
                return (
                  <button
                    type="button"
                    key={option}
                    onClick={() => choose(option)}
                    className={`listening-option press ${selected ? 'is-selected' : ''}`}
                  >
                    <span>{option}</span>
                    {selected && <CheckCircle2 size={17} />}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="flex items-center gap-2 mt-5">
            <Button size="sm" variant="ghost" disabled={index === 0} onClick={() => setIndex((v) => v - 1)}>
              <ChevronLeft size={15} /> Oldingi
            </Button>
            {index < questions.length - 1 ? (
              <Button size="sm" variant="secondary" className="ml-auto" onClick={() => setIndex((v) => v + 1)}>
                Keyingi <ChevronRight size={15} />
              </Button>
            ) : (
              <Button size="sm" className="ml-auto" onClick={submit} loading={submitting} disabled={answeredCount < questions.length}>
                <CheckCircle2 size={15} /> Yakunlash
              </Button>
            )}
          </div>
        </>
      )}
      {error && <p className="text-xs mt-3" style={{ color: 'var(--color-red)' }}>{error}</p>}
    </Card>
  );
}
