import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, CheckCheck, Award, ShoppingBag, AlertTriangle, Info } from 'lucide-react';
import { getBildirishnomalar, markAllBildirishnomalarRead, markBildirishnomaRead } from '../api/engagement';

const typeIcons = {
  certificate: Award,
  shop: ShoppingBag,
  warning: AlertTriangle,
  success: CheckCheck,
  info: Info,
};

export default function NotificationBell({ mobile = false }) {
  const [open, setOpen] = useState(false);
  const [data, setData] = useState({ oqilmagan_soni: 0, natijalar: [] });
  const boxRef = useRef(null);
  const navigate = useNavigate();

  const load = () => getBildirishnomalar().then(setData).catch(() => {});

  useEffect(() => {
    load();
    const timer = setInterval(load, 45000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const close = (event) => {
      if (boxRef.current && !boxRef.current.contains(event.target)) setOpen(false);
    };
    document.addEventListener('mousedown', close);
    return () => document.removeEventListener('mousedown', close);
  }, []);

  const openItem = async (item) => {
    if (!item.oqilgan) await markBildirishnomaRead(item.id).catch(() => {});
    setOpen(false);
    load();
    if (item.havola) navigate(item.havola);
  };

  const readAll = async () => {
    await markAllBildirishnomalarRead().catch(() => {});
    load();
  };

  return (
    <div className={`notification-bell ${mobile ? 'notification-bell--mobile' : ''}`} ref={boxRef}>
      <button type="button" className="notification-bell__button press" onClick={() => setOpen((v) => !v)} aria-label="Bildirishnomalar">
        <Bell size={mobile ? 18 : 20} />
        {data.oqilmagan_soni > 0 && <span className="notification-bell__count">{Math.min(data.oqilmagan_soni, 99)}</span>}
      </button>
      {open && (
        <div className="notification-popover animate-in-fast">
          <div className="notification-popover__header">
            <div><strong>Bildirishnomalar</strong><span>{data.oqilmagan_soni} ta o‘qilmagan</span></div>
            {data.oqilmagan_soni > 0 && <button type="button" onClick={readAll}>Barchasini o‘qish</button>}
          </div>
          <div className="notification-popover__list">
            {data.natijalar.length === 0 ? (
              <p className="notification-empty">Yangi bildirishnoma yo‘q.</p>
            ) : data.natijalar.slice(0, 8).map((item) => {
              const Icon = typeIcons[item.tur] || Info;
              return (
                <button type="button" key={item.id} className={`notification-item ${item.oqilgan ? '' : 'is-unread'}`} onClick={() => openItem(item)}>
                  <span className={`notification-item__icon type-${item.tur}`}><Icon size={16} /></span>
                  <span className="min-w-0 flex-1"><b>{item.sarlavha}</b><small>{item.matn}</small></span>
                </button>
              );
            })}
          </div>
          <button type="button" className="notification-popover__footer" onClick={() => { setOpen(false); navigate('/oquvchi/bildirishnomalar'); }}>Barcha xabarlarni ko‘rish</button>
        </div>
      )}
    </div>
  );
}
