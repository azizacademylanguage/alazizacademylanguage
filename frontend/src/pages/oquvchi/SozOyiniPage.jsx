import { useEffect, useMemo, useState } from 'react';
import { Brain, Coins, RotateCcw, Sparkles, Trophy, Volume2 } from 'lucide-react';
import { Button, Card, Skeleton } from '../../components/ui';
import { checkSozOyiniPair, finishSozOyini, startSozOyini } from '../../api/coinShop';

export default function SozOyiniPage() {
  const [game, setGame] = useState(null);
  const [loading, setLoading] = useState(true);
  const [opened, setOpened] = useState([]);
  const [matched, setMatched] = useState(new Set());
  const [pairs, setPairs] = useState([]);
  const [moves, setMoves] = useState(0);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const loadGame = async () => {
    setLoading(true);
    setError('');
    setOpened([]);
    setMatched(new Set());
    setPairs([]);
    setMoves(0);
    setBusy(false);
    setResult(null);
    try {
      const data = await startSozOyini();
      setGame(data);
    } catch (err) {
      setGame(null);
      setError(err.response?.data?.detail || "O'yinni yuklab bo'lmadi.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadGame(); }, []);

  const progress = useMemo(() => Math.round((matched.size / 20) * 100), [matched]);

  const speak = (text, event) => {
    event.stopPropagation();
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(new SpeechSynthesisUtterance(text));
  };

  const finish = async (nextPairs) => {
    setBusy(true);
    try {
      const data = await finishSozOyini(game.token, nextPairs);
      setResult(data);
      window.dispatchEvent(new CustomEvent('coin-updated', { detail: data.balans }));
    } catch (err) {
      setError(err.response?.data?.detail || "O'yin natijasini saqlab bo'lmadi.");
    } finally {
      setBusy(false);
    }
  };

  const handleCard = async (card) => {
    if (busy || result || matched.has(card.id) || opened.includes(card.id)) return;
    if (opened.length === 0) {
      setOpened([card.id]);
      return;
    }

    const first = opened[0];
    setOpened([first, card.id]);
    setMoves((value) => value + 1);
    setBusy(true);
    try {
      const checked = await checkSozOyiniPair(game.token, first, card.id);
      if (checked.togri) {
        const nextMatched = new Set(matched);
        nextMatched.add(first);
        nextMatched.add(card.id);
        const nextPairs = [...pairs, { birinchi: first, ikkinchi: card.id }];
        setMatched(nextMatched);
        setPairs(nextPairs);
        setTimeout(() => setOpened([]), 260);
        if (nextPairs.length === 10) {
          setTimeout(() => finish(nextPairs), 500);
          return;
        }
      } else {
        setTimeout(() => setOpened([]), 720);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Kartalarni tekshirib bo‘lmadi.');
      setOpened([]);
    } finally {
      setTimeout(() => setBusy(false), 740);
    }
  };

  return (
    <div className="animate-in word-game-page">
      <section className="word-game-hero">
        <div>
          <div className="word-game-kicker"><Brain size={15} /> SO‘Z XOTIRA O‘YINI</div>
          <h1>{game?.fan || 'Til'} so‘zlarini juftlang</h1>
          <p>Chet tilidagi kartani bosing, keyin uning o‘zbekcha tarjimasini toping. Har bir to‘g‘ri juft — 1 coin.</p>
        </div>
        <div className="word-game-prize">
          <Coins size={22} />
          <strong>10 coin</strong>
          <span>maksimal mukofot</span>
        </div>
      </section>

      <div className="word-game-stats">
        <div><span>Topildi</span><strong>{matched.size / 2} / 10</strong></div>
        <div><span>Urinish</span><strong>{moves}</strong></div>
        <div><span>Jarayon</span><strong>{progress}%</strong></div>
        <Button variant="secondary" size="sm" onClick={loadGame}><RotateCcw size={15} /> Qayta boshlash</Button>
      </div>

      {error && <div className="word-game-error">{error}</div>}

      {loading ? (
        <div className="word-game-grid">{Array.from({ length: 20 }).map((_, i) => <Skeleton key={i} className="h-28 w-full" />)}</div>
      ) : !game ? (
        <Card><div className="p-10 text-center"><Brain className="mx-auto mb-3" /><p className="font-bold">{error || "O'yin mavjud emas"}</p></div></Card>
      ) : (
        <div className="word-game-grid" aria-label="So‘z kartalari">
          {game.cardlar.map((card, index) => {
            const isOpen = opened.includes(card.id) || matched.has(card.id);
            const isMatched = matched.has(card.id);
            return (
              <button
                key={card.id}
                type="button"
                className={`memory-card ${isOpen ? 'is-open' : ''} ${isMatched ? 'is-matched' : ''}`}
                onClick={() => handleCard(card)}
                disabled={busy && !isOpen}
                style={{ animationDelay: `${index * 24}ms` }}
                aria-label={isOpen ? card.matn : 'Yopiq karta'}
              >
                <span className="memory-card__inner">
                  <span className="memory-card__front"><Sparkles size={22} /><small>Kartani ochish</small></span>
                  <span className="memory-card__back">
                    <strong>{card.matn}</strong>
                    <span onClick={(event) => speak(card.matn, event)} role="button" tabIndex={-1}><Volume2 size={15} /></span>
                  </span>
                </span>
              </button>
            );
          })}
        </div>
      )}

      {result && (
        <div className="word-game-result animate-pop">
          <div className="word-game-result__icon"><Trophy size={34} /></div>
          <div>
            <p className="word-game-result__eyebrow">O‘YIN YAKUNLANDI</p>
            <h2>{result.xabar}</h2>
            <p>Yangi balans: <strong>{result.balans} coin</strong></p>
          </div>
          <Button variant="amber" onClick={loadGame}><RotateCcw size={16} /> Yana o‘ynash</Button>
        </div>
      )}
    </div>
  );
}
