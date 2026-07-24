import { useEffect, useState, useRef } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { getDars, saveDarsProgress } from '../../api/oquvchi';
import { getWritingTopshiriqlar } from '../../api/writingSpeaking';
import { getSpeakingTopshiriqlar } from '../../api/writingSpeaking';
import { Card, Button, Skeleton } from '../../components/ui';
import WritingTask from '../../components/WritingTask';
import SpeakingTask from '../../components/SpeakingTask';
import { ChevronLeft, CheckCircle2, ListChecks } from 'lucide-react';

export default function DarsPage() {
  const { darsId } = useParams();
  const navigate = useNavigate();
  const [dars, setDars] = useState(null);
  const [writingTopshiriqlar, setWritingTopshiriqlar] = useState([]);
  const [speakingTopshiriqlar, setSpeakingTopshiriqlar] = useState([]);
  const [loading, setLoading] = useState(true);
  const [markingDone, setMarkingDone] = useState(false);
  const videoRef = useRef();
  const saveTimeout = useRef();

  const load = () => {
    getDars(darsId).then((d) => {
      setDars(d);
      setLoading(false);
      if (videoRef.current && d.progress?.video_pozitsiya_soniya) {
        videoRef.current.currentTime = d.progress.video_pozitsiya_soniya;
      }
    });
    getWritingTopshiriqlar(darsId).then(setWritingTopshiriqlar).catch(() => {});
    getSpeakingTopshiriqlar(darsId).then(setSpeakingTopshiriqlar).catch(() => {});
  };

  useEffect(() => { setLoading(true); load(); }, [darsId]);

  const handleTimeUpdate = () => {
    clearTimeout(saveTimeout.current);
    saveTimeout.current = setTimeout(() => {
      if (videoRef.current) {
        saveDarsProgress(darsId, { video_pozitsiya_soniya: Math.floor(videoRef.current.currentTime) });
      }
    }, 3000);
  };

  const handleVideoEnded = async () => {
    await saveDarsProgress(darsId, { video_tugatilgan: true, video_pozitsiya_soniya: 0 });
    load();
  };

  const markAsDone = async () => {
    setMarkingDone(true);
    try {
      await saveDarsProgress(darsId, { video_tugatilgan: true });
      load();
    } finally {
      setMarkingDone(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-3xl space-y-4">
        <Skeleton className="h-8 w-2/3" />
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }
  if (!dars) return <p className="text-sm" style={{ color: '#8A8371' }}>Dars topilmadi.</p>;

  return (
    <div className="animate-in max-w-3xl">
      <button onClick={() => navigate(-1)} className="inline-flex items-center gap-1 text-sm mb-4 hover:underline press" style={{ color: 'var(--color-forest)' }}>
        <ChevronLeft size={15} /> Orqaga
      </button>

      <h1 className="font-display text-2xl font-bold mb-6" style={{ color: 'var(--color-ink)' }}>{dars.sarlavha}</h1>

      {dars.video && (
        <Card className="mb-5 p-0 overflow-hidden animate-in-fast">
          <video
            ref={videoRef}
            src={dars.video}
            controls
            className="w-full block"
            onTimeUpdate={handleTimeUpdate}
            onEnded={handleVideoEnded}
          />
        </Card>
      )}

      {dars.audio && (
        <Card className="mb-5 p-5 animate-in-fast stagger-1">
          <p className="text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: '#8A8371' }}>Audio dars</p>
          <audio src={dars.audio} controls className="w-full" />
        </Card>
      )}

      {dars.tushuntirish_matn && (
        <Card className="mb-5 p-5 animate-in-fast stagger-2">
          <p className="text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: '#8A8371' }}>Tushuntirish</p>
          <p className="text-sm leading-relaxed whitespace-pre-line" style={{ color: 'var(--color-ink)' }}>{dars.tushuntirish_matn}</p>
        </Card>
      )}

      {dars.misollar && (
        <Card className="mb-5 p-5 animate-in-fast stagger-3">
          <p className="text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: '#8A8371' }}>Misollar</p>
          <p className="text-sm leading-relaxed whitespace-pre-line" style={{ color: 'var(--color-ink)' }}>{dars.misollar}</p>
        </Card>
      )}

      {writingTopshiriqlar.map((t) => <div key={`w-${t.id}`} className="mb-5"><WritingTask topshiriq={t} /></div>)}
      {speakingTopshiriqlar.map((t) => <div key={`s-${t.id}`} className="mb-5"><SpeakingTask topshiriq={t} /></div>)}

      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 mt-6">
        {!dars.progress?.video_tugatilgan ? (
          <Button variant="secondary" onClick={markAsDone} disabled={markingDone} className="justify-center">
            <CheckCircle2 size={16} /> {markingDone ? 'Saqlanmoqda...' : "Darsni tugatdim deb belgilash"}
          </Button>
        ) : (
          <span className="flex items-center justify-center gap-2 text-sm font-medium py-2.5" style={{ color: 'var(--color-forest)' }}>
            <CheckCircle2 size={16} /> Dars tugatilgan
          </span>
        )}

        {dars.mashq_bor && (
          <Link to={`/oquvchi/mashq/${dars.mashq_id}`} className="sm:ml-auto">
            <Button variant="amber" className="w-full justify-center"><ListChecks size={16} /> Mashqni boshlash</Button>
          </Link>
        )}
      </div>
    </div>
  );
}
