import { useState, useRef } from 'react';
import { topshirSpeaking } from '../api/writingSpeaking';
import { Card, Button } from './ui';
import { Mic, Square, CheckCircle2, Volume2 } from 'lucide-react';

export default function SpeakingTask({ topshiriq }) {
  const [recording, setRecording] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [audioBlob, setAudioBlob] = useState(null);
  const [natija, setNatija] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [xatolik, setXatolik] = useState('');
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const startRecording = async () => {
    setXatolik('');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => chunksRef.current.push(e.data);
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setAudioBlob(blob);
        setAudioUrl(URL.createObjectURL(blob));
        stream.getTracks().forEach((t) => t.stop());
      };

      mediaRecorder.start();
      setRecording(true);
    } catch (err) {
      setXatolik("Mikrofonga ruxsat berilmadi. Brauzer sozlamalarini tekshiring.");
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setRecording(false);
  };

  const handleSubmit = async () => {
    if (!audioBlob) return;
    setSubmitting(true);
    try {
      const result = await topshirSpeaking(topshiriq.id, audioBlob);
      setNatija(result);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Card className="p-5 animate-in-fast">
      <div className="flex items-center gap-2 mb-3">
        <Mic size={16} style={{ color: 'var(--color-forest)' }} />
        <h3 className="font-display font-bold text-sm" style={{ color: 'var(--color-ink)' }}>Speaking mashqi</h3>
      </div>
      <p className="text-sm mb-4 p-3 rounded-xl flex items-center gap-2" style={{ background: 'var(--color-paper-warm)', color: 'var(--color-ink)' }}>
        <Volume2 size={15} className="flex-shrink-0" style={{ color: 'var(--color-forest-light)' }} />
        {topshiriq.matn}
      </p>

      {natija ? (
        <div className="animate-pop flex items-center gap-3 p-3 rounded-xl" style={{ background: '#E4EFE6' }}>
          <CheckCircle2 size={20} style={{ color: 'var(--color-forest)' }} />
          <div>
            <p className="text-sm font-semibold" style={{ color: 'var(--color-ink)' }}>Yuborildi</p>
            <p className="text-xs" style={{ color: '#8A8371' }}>{natija.ai_izoh}</p>
          </div>
        </div>
      ) : (
        <>
          {xatolik && (
            <div className="mb-3 text-xs px-3 py-2 rounded-xl" style={{ background: '#FBEAE8', color: 'var(--color-red)' }}>{xatolik}</div>
          )}

          <div className="flex items-center gap-3">
            {!recording && !audioUrl && (
              <Button variant="secondary" onClick={startRecording}>
                <Mic size={15} /> Yozishni boshlash
              </Button>
            )}
            {recording && (
              <Button variant="danger" onClick={stopRecording} className="animate-pulse">
                <Square size={15} /> To'xtatish
              </Button>
            )}
            {audioUrl && !recording && (
              <>
                <audio src={audioUrl} controls className="h-9" />
                <Button size="sm" variant="ghost" onClick={() => { setAudioUrl(null); setAudioBlob(null); }}>
                  Qayta yozish
                </Button>
              </>
            )}
          </div>

          {audioUrl && (
            <div className="mt-3">
              <Button onClick={handleSubmit} disabled={submitting}>
                {submitting ? 'Yuborilmoqda...' : 'Topshirish'}
              </Button>
            </div>
          )}
        </>
      )}
    </Card>
  );
}
