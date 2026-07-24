import { useEffect, useState } from 'react';
import { getFanlarim } from '../../api/oquvchi';
import { Card, EmptyState, Skeleton } from '../../components/ui';
import SelectedCoursePanel from '../../components/SelectedCoursePanel';
import { BookOpen } from 'lucide-react';

export default function FanlarimPage() {
  const [fanlar, setFanlar] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getFanlarim().then(setFanlar).finally(() => setLoading(false));
  }, []);

  const selectedCourse = fanlar[0] || null;

  return (
    <div className="animate-in">
      <div className="mb-7">
        <p className="text-xs uppercase tracking-[0.22em] font-bold mb-2" style={{ color: 'var(--color-teal)' }}>Mening kursim</p>
        <h1 className="font-display text-2xl sm:text-3xl font-extrabold" style={{ color: 'var(--color-ink)' }}>Darajalar</h1>
        <p className="text-sm mt-1 max-w-2xl" style={{ color: 'var(--color-muted)' }}>
          Faqat admin tanlagan fan ko'rsatiladi. Ochiq darajani tugatib, yakuniy testdan 80% yoki undan yuqori natija olsangiz keyingi daraja avtomatik ochiladi.
        </p>
      </div>

      {loading ? (
        <Skeleton className="h-[460px] w-full" />
      ) : !selectedCourse ? (
        <Card>
          <EmptyState icon={BookOpen} title="Hozircha fan tanlanmagan" description="Admin sizga fan va boshlang'ich darajani tanlab berishini kuting." />
        </Card>
      ) : (
        <SelectedCoursePanel fan={selectedCourse} />
      )}
    </div>
  );
}
