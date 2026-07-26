import { useRef, useState } from 'react';
import { topshirSpeaking } from '../api/writingSpeaking';
import { Card, Button } from './ui';
import { Mic, Square, CheckCircle2, Volume2, RotateCcw, AudioLines } from 'lucide-react';

export default function SpeakingTask({ topshiriq }) {
  const [listening, setListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interim, setInterim] = useState('');
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const recognitionRef = useRef(null);

  const playSample = () => {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(topshiriq.matn);
    utterance.lang = topshiriq.til_kodi || 'en-US';
    utterance.rate = 0.78;
    window.speechSynthesis.speak(utterance);
  };

  const start = () => {
    setError('');
    setTranscript('');
    setInterim('');
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) {
      setError('Bu brauzer ovozni matnga aylantirishni qo‘llamaydi. Chrome yoki Edge brauzeridan foydalaning.');
      return;
    }
    const recognition = new Recognition();
    recognition.lang = topshiriq.til_kodi || 'en-US';
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;
    recognition.onresult = (event) => {
      let finalText = '';
      let interimText = '';
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const text = event.results[i][0].transcript;
        if (event.results[i].isFinal) finalText += text;
        else interimText += text;
      }
      if (finalText) setTranscript((prev) => `${prev} ${finalText}`.trim());
      setInterim(interimText);
    };
    recognition.onerror = (event) => {
      const messages = {
        'not-allowed': 'Mikrofonga ruxsat berilmadi.',
        'no-speech': 'Ovoz aniqlanmadi. Qayta urinib ko‘ring.',
        network: 'Ovozni tekshirish xizmatiga ulanib bo‘lmadi.',
      };
      setError(messages[event.error] || 'Ovozni tanishda xatolik yuz berdi.');
      setListening(false);
    };
    recognition.onend = () => setListening(false);
    recognitionRef.current = recognition;
    recognition.start();
    setListening(true);
  };

  const stop = () => {
    recognitionRef.current?.stop();
    setListening(false);
  };

  const submit = async () => {
    const text = `${transcript} ${interim}`.trim();
    if (!text) return;
    setSubmitting(true);
    setError('');
    try {
      setResult(await topshirSpeaking(topshiriq.id, text));
    } catch (err) {
      setError(err.response?.data?.detail || 'Speaking natijasini yuborib bo‘lmadi.');
    } finally {
      setSubmitting(false);
    }
  };

  const reset = () => {
    setTranscript('');
    setInterim('');
    setResult(null);
    setError('');
  };

  return (
    <Card className="p-5 animate-in-fast speaking-card">
      <div className="flex items-center justify-between gap-3 mb-4">
        <div className="flex items-center gap-3">
          <div className="feature-icon feature-icon--amethyst"><AudioLines size={19} /></div>
          <div><h3 className="font-display font-extrabold text-base" style={{ color: 'var(--color-ink)' }}>Speaking va talaffuz</h3><p className="text-xs" style={{ color: 'var(--color-muted)' }}>Namunani tinglang, so‘ng gapni mikrofon orqali ayting.</p></div>
        </div>
        <button type="button" onClick={playSample} className="listen-button press"><Volume2 size={17} /> Tinglash</button>
      </div>

      <div className="speaking-target"><Volume2 size={16} /><span>{topshiriq.matn}</span></div>

      {result ? (
        <div className="speaking-result animate-pop">
          <div className={`score-ring ${Number(result.ai_foiz) >= 70 ? 'is-success' : 'is-warning'}`}><strong>{Math.round(Number(result.ai_foiz || 0))}%</strong><span>aniqlik</span></div>
          <div className="flex-1">
            <h4 className="font-display font-bold" style={{ color: 'var(--color-ink)' }}>{Number(result.ai_foiz) >= 70 ? 'Yaxshi talaffuz!' : 'Mashqni davom ettiring'}</h4>
            <p className="text-sm mt-1" style={{ color: 'var(--color-muted)' }}>{result.ai_izoh}</p>
            <p className="recognized-text mt-2"><b>Aniqlangan:</b> {result.transkripsiya || '—'}</p>
            <Button size="sm" variant="secondary" onClick={reset} className="mt-3"><RotateCcw size={14} /> Qayta aytish</Button>
          </div>
        </div>
      ) : (
        <>
          {(transcript || interim) && <div className="recognized-text mt-3"><b>Aniqlanayotgan matn:</b> {transcript} <i>{interim}</i></div>}
          {error && <div className="mt-3 text-xs px-3 py-2 rounded-xl" style={{ background: '#FBEAE8', color: 'var(--color-red)' }}>{error}</div>}
          <div className="flex flex-wrap items-center gap-2 mt-4">
            {!listening ? (
              <Button variant="secondary" onClick={start}><Mic size={16} /> Gapirishni boshlash</Button>
            ) : (
              <Button variant="danger" onClick={stop} className="speaking-recording"><Square size={15} /> To‘xtatish</Button>
            )}
            {(transcript || interim) && !listening && <Button onClick={submit} loading={submitting}><CheckCircle2 size={15} /> Talaffuzni tekshirish</Button>}
          </div>
          <p className="text-[11px] mt-3" style={{ color: 'var(--color-muted)' }}>Mikrofon HTTPS saytda ishlaydi. Eng yaxshi natija uchun Chrome yoki Edge’dan foydalaning.</p>
        </>
      )}
    </Card>
  );
}
