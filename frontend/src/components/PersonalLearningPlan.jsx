import { Link } from 'react-router-dom';
import { Card, Button, ProgressBar } from './ui';
import { CalendarCheck, BookOpenCheck, Languages, Lightbulb, ArrowRight, Flame } from 'lucide-react';

export default function PersonalLearningPlan({ plan }) {
  if (!plan?.fan) return null;
  const lesson = plan.bugungi_dars;
  const targetLink = lesson?.yakuniy_test
    ? `/oquvchi/final-test/${lesson.daraja_id}`
    : lesson?.dars_id
      ? `/oquvchi/dars/${lesson.dars_id}`
      : '/oquvchi';

  return (
    <Card className="personal-plan mb-6 overflow-hidden">
      <div className="personal-plan__header">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] font-extrabold mb-1">Shaxsiy o‘qish rejasi</p>
          <h2 className="font-display text-xl font-extrabold">Bugungi yo‘nalishingiz tayyor</h2>
        </div>
        <div className="personal-plan__streak"><Flame size={18} /> {plan.streak?.joriy || 0} kun</div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 p-5">
        <div className="plan-block plan-block--primary lg:col-span-2">
          <div className="feature-icon feature-icon--amethyst"><BookOpenCheck size={19} /></div>
          <div className="min-w-0 flex-1">
            <p className="text-[11px] uppercase tracking-wider font-bold" style={{ color: 'var(--color-amethyst)' }}>Bugungi dars</p>
            <h3 className="font-display font-extrabold mt-1" style={{ color: 'var(--color-ink)' }}>{lesson?.mavzu_nomi || 'Darslar yakunlangan'}</h3>
            <p className="text-sm mt-1" style={{ color: 'var(--color-muted)' }}>{lesson?.daraja_nomi} · {lesson?.dars_nomi}</p>
          </div>
          {lesson && (
            <Link to={targetLink}>
              <Button size="sm">Boshlash <ArrowRight size={14} /></Button>
            </Link>
          )}
        </div>

        <div className="plan-block">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2"><CalendarCheck size={17} style={{ color: 'var(--color-jungle)' }} /><strong className="text-sm">Haftalik maqsad</strong></div>
            <span className="text-xs font-bold" style={{ color: 'var(--color-jungle)' }}>{plan.haftalik_maqsad?.bajarildi}/{plan.haftalik_maqsad?.maqsad}</span>
          </div>
          <ProgressBar value={plan.haftalik_maqsad?.foiz || 0} />
          <p className="text-xs mt-2" style={{ color: 'var(--color-muted)' }}>Haftada kamida 5 ta o‘quv faolligi.</p>
        </div>

        <div className="plan-block lg:col-span-2">
          <div className="flex items-center gap-2 mb-3"><Languages size={17} style={{ color: 'var(--color-teal)' }} /><strong className="text-sm">Bugun qaytariladigan so‘zlar</strong></div>
          <div className="review-word-list">
            {(plan.qaytarish_sozlari || []).map((word) => (
              <span key={`${word.chet_soz}-${word.uzbek_soz}`} className="review-word">
                <b>{word.chet_soz}</b><i>→</i>{word.uzbek_soz}
              </span>
            ))}
          </div>
        </div>

        <div className="plan-block">
          <div className="flex items-center gap-2 mb-2"><Lightbulb size={17} style={{ color: 'var(--color-olive)' }} /><strong className="text-sm">Tavsiya</strong></div>
          <p className="text-xs leading-relaxed" style={{ color: 'var(--color-muted)' }}>{plan.tavsiyalar?.[0]}</p>
        </div>
      </div>
    </Card>
  );
}
