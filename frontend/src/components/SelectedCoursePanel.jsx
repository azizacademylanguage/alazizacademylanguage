import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  BookOpen,
  CheckCircle2,
  ChevronRight,
  Circle,
  Layers3,
  LockKeyhole,
  PlayCircle,
  Sparkles,
  Trophy,
  Unlock,
} from 'lucide-react';
import { getMavzular } from '../api/oquvchi';
import { Badge, Button, Card, Modal, ProgressBar, Skeleton } from './ui';
import { cleanLevelName, languageMeta } from '../utils/course';

function chooseCurrentLevel(levels) {
  const openLevels = levels.filter((level) => level.ochiq);
  return openLevels.find((level) => !level.otilgan) || openLevels.at(-1) || null;
}

export default function SelectedCoursePanel({ fan }) {
  const [lockedInfo, setLockedInfo] = useState(null);
  const [activeLevelId, setActiveLevelId] = useState(null);
  const [topics, setTopics] = useState([]);
  const [topicsLoading, setTopicsLoading] = useState(false);
  const [topicsError, setTopicsError] = useState('');
  const [refreshToken, setRefreshToken] = useState(0);

  const meta = languageMeta(fan?.fan_nomi || '');
  const levels = fan?.darajalar || [];
  const opened = levels.filter((level) => level.ochiq).length;
  const completed = levels.filter((level) => level.otilgan).length;

  const activeLevel = useMemo(
    () => levels.find((level) => Number(level.id) === Number(activeLevelId)) || null,
    [levels, activeLevelId],
  );

  useEffect(() => {
    const current = chooseCurrentLevel(levels);
    setActiveLevelId((previous) => {
      const previousStillOpen = levels.some(
        (level) => Number(level.id) === Number(previous) && level.ochiq,
      );
      return previousStillOpen ? previous : current?.id || null;
    });
  }, [fan?.id, levels]);

  useEffect(() => {
    if (!activeLevelId || !activeLevel?.ochiq) {
      setTopics([]);
      setTopicsError('');
      return;
    }

    let cancelled = false;
    setTopicsLoading(true);
    setTopicsError('');

    getMavzular(activeLevelId)
      .then((data) => {
        if (!cancelled) setTopics(data);
      })
      .catch((error) => {
        if (!cancelled) {
          setTopics([]);
          setTopicsError(error.response?.data?.detail || "Mavzularni yuklab bo'lmadi.");
        }
      })
      .finally(() => {
        if (!cancelled) setTopicsLoading(false);
      });

    return () => { cancelled = true; };
  }, [activeLevelId, activeLevel?.ochiq, refreshToken]);

  const allTopicsDone = topics.length > 0 && topics.every((topic) => topic.otilgan);

  if (!fan) return null;

  const handleLevelClick = (level) => {
    if (!level.ochiq) {
      setLockedInfo({
        name: cleanLevelName(level.nomi),
        message: level.qulf_sababi,
      });
      return;
    }
    setActiveLevelId(level.id);
  };

  return (
    <>
      <Card className="course-panel course-panel--inline overflow-hidden">
        <div className="course-panel__hero course-panel__hero--compact">
          <div className={`language-mark language-mark--${meta.accent}`}>
            <span className="language-mark__flag">{meta.flag}</span>
            <span className="language-mark__code">{meta.code}</span>
          </div>

          <div className="min-w-0 flex-1 relative z-[1]">
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <Badge tone="forest"><BookOpen size={12} className="mr-1" /> Mening fanim</Badge>
              <Badge tone="success"><Unlock size={12} className="mr-1" /> {opened} ta ochiq</Badge>
            </div>
            <h2 className="font-display text-2xl sm:text-3xl font-extrabold" style={{ color: 'var(--color-ink)' }}>
              {fan.fan_nomi}
            </h2>
            <p className="text-sm mt-1" style={{ color: 'var(--color-muted)' }}>
              Darajani tanlang. Ochiq darajaning mavzulari shu sahifada darhol ko‘rinadi.
            </p>
          </div>

          <div className="course-summary hidden md:flex">
            <Sparkles size={18} />
            <div><strong>{completed}</strong><span>tugatilgan daraja</span></div>
          </div>
        </div>

        <div className="course-content-wrap">
          <section className="level-section">
            <div className="section-heading-row">
              <div>
                <p className="section-eyebrow">Bosqichlar</p>
                <h3 className="section-title">Darajalar</h3>
              </div>
              <span className="section-helper">Faqat ochiq darajaga kirish mumkin</span>
            </div>

            <div className="level-tabs" role="tablist" aria-label="Darajalar">
              {levels.map((level, index) => {
                const name = cleanLevelName(level.nomi);
                const isOpen = Boolean(level.ochiq);
                const isDone = Boolean(level.otilgan);
                const isActive = Number(level.id) === Number(activeLevelId);

                return (
                  <button
                    key={level.id}
                    type="button"
                    role="tab"
                    aria-selected={isActive}
                    className={`level-tab ${isOpen ? 'level-tab--open' : 'level-tab--locked'} ${isDone ? 'level-tab--done' : ''} ${isActive ? 'level-tab--active' : ''}`}
                    style={{ animationDelay: `${index * 55}ms` }}
                    onClick={() => handleLevelClick(level)}
                    title={isOpen ? `${name} darajasini ochish` : `${name} qulflangan`}
                  >
                    <span className="level-tab__icon">
                      {isDone ? <CheckCircle2 size={18} /> : isOpen ? <Unlock size={17} /> : <LockKeyhole size={16} />}
                    </span>
                    <span className="level-tab__name">{name}</span>
                  </button>
                );
              })}
            </div>
          </section>

          <section className="inline-topics-section">
            <div className="section-heading-row section-heading-row--topics">
              <div>
                <p className="section-eyebrow">Hozirgi daraja</p>
                <h3 className="section-title">
                  {activeLevel ? `${cleanLevelName(activeLevel.nomi)} mavzulari` : 'Mavzular'}
                </h3>
              </div>
              {activeLevel && (
                <Badge tone={activeLevel.otilgan ? 'success' : 'forest'}>
                  {activeLevel.otilgan ? 'Daraja tugatilgan' : 'Daraja ochiq'}
                </Badge>
              )}
            </div>

            {topicsLoading ? (
              <div className="topic-grid">
                {[1, 2, 3].map((item) => <Skeleton key={item} className="h-36 w-full" />)}
              </div>
            ) : topicsError ? (
              <div className="topics-message topics-message--error">
                <Layers3 size={22} />
                <p>{topicsError}</p>
                <Button size="sm" variant="secondary" onClick={() => setRefreshToken((value) => value + 1)}>Qayta urinish</Button>
              </div>
            ) : !activeLevel ? (
              <div className="topics-message">
                <LockKeyhole size={24} />
                <p>Hozircha ochiq daraja yo‘q. Admin bilan bog‘laning.</p>
              </div>
            ) : topics.length === 0 ? (
              <div className="topics-message">
                <Layers3 size={24} />
                <p>Bu darajaga hali mavzular joylanmagan.</p>
              </div>
            ) : (
              <>
                <div className="topic-grid">
                  {topics.map((topic, topicIndex) => {
                    const isOpen = topic.ochiq !== false;
                    const score = Number(topic.eng_yaxshi_foiz || 0);
                    const progress = topic.otilgan ? 100 : Math.min(score, 100);

                    return (
                      <article
                        key={topic.id}
                        className={`topic-card ${isOpen ? 'topic-card--open' : 'topic-card--locked'} ${topic.otilgan ? 'topic-card--done' : ''}`}
                        style={{ animationDelay: `${topicIndex * 70}ms` }}
                      >
                        <div className="topic-card__header">
                          <span className="topic-card__icon">
                            {topic.otilgan ? <CheckCircle2 size={20} /> : isOpen ? <PlayCircle size={20} /> : <LockKeyhole size={18} />}
                          </span>
                          <div className="min-w-0 flex-1">
                            <h4 className="topic-card__title">{topic.nomi}</h4>
                            <p className="topic-card__description">
                              {topic.otilgan
                                ? 'Mavzu testidan muvaffaqiyatli o‘tilgan.'
                                : isOpen
                                  ? 'Tushuntirishni o‘qing va 10 ta testni bajaring.'
                                  : topic.qulf_sababi}
                            </p>
                          </div>
                          <Badge tone={topic.otilgan ? 'success' : isOpen ? 'forest' : 'neutral'}>
                            {topic.otilgan ? 'Bajarildi' : isOpen ? 'Ochiq' : 'Qulflangan'}
                          </Badge>
                        </div>

                        {isOpen && (
                          <>
                            <div className="topic-progress-row">
                              <span>Eng yaxshi natija</span>
                              <strong>{score}%</strong>
                            </div>
                            <ProgressBar value={progress} tone={topic.otilgan ? 'forest' : 'amber'} />

                            <div className="topic-lessons">
                              {(topic.darslar || []).map((lesson) => (
                                <Link
                                  key={lesson.id}
                                  to={`/oquvchi/dars/${lesson.id}`}
                                  className="topic-lesson-link"
                                >
                                  <span className="topic-lesson-link__left">
                                    {lesson.testdan_otilgan
                                      ? <CheckCircle2 size={16} />
                                      : <Circle size={16} />}
                                    <span>
                                      <strong>{lesson.sarlavha}</strong>
                                      <small>
                                        {lesson.testdan_otilgan
                                          ? `Test bajarildi · ${lesson.eng_yaxshi_foiz}%`
                                          : 'Dars va testni boshlash'}
                                      </small>
                                    </span>
                                  </span>
                                  <ChevronRight size={17} />
                                </Link>
                              ))}

                              {(!topic.darslar || topic.darslar.length === 0) && (
                                <div className="topic-empty-lesson">Bu mavzuga hali dars qo‘shilmagan.</div>
                              )}
                            </div>
                          </>
                        )}
                      </article>
                    );
                  })}
                </div>

                {allTopicsDone && (
                  <div className="final-test-banner animate-pop">
                    <span className="final-test-banner__icon"><Trophy size={25} /></span>
                    <div className="flex-1">
                      <h4>Barcha mavzular 80%+ bilan tugatildi</h4>
                      <p>Endi yakuniy 10 ta testni topshiring. 80%+ natija keyingi darajani avtomatik ochadi.</p>
                    </div>
                    <Link to={`/oquvchi/final-test/${activeLevel.id}`}>
                      <Button variant="amber">Yakuniy test</Button>
                    </Link>
                  </div>
                )}
              </>
            )}
          </section>
        </div>
      </Card>

      <Modal
        open={Boolean(lockedInfo)}
        onClose={() => setLockedInfo(null)}
        title={`${lockedInfo?.name || 'Daraja'} qulflangan`}
        subtitle="Bu darajaga hozircha kirib bo‘lmaydi."
      >
        <div className="locked-message">
          <LockKeyhole size={24} />
          <p>{lockedInfo?.message || "Darajani ochish uchun admin bilan bog‘laning."}</p>
        </div>
        <div className="flex justify-end mt-5">
          <Button onClick={() => setLockedInfo(null)}>Tushunarli</Button>
        </div>
      </Modal>
    </>
  );
}
