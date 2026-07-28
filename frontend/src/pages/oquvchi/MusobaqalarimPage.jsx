import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock3, Sparkles, Trophy } from 'lucide-react';
import { getMusobaqalar } from '../../api/ranking';
import { Badge, Button, Card, EmptyState, Skeleton } from '../../components/ui';
import { useLanguage } from '../../context/LanguageContext';

export default function MusobaqalarimPage(){
 const [items,setItems]=useState([]);const [loading,setLoading]=useState(true);const navigate=useNavigate();const {t}=useLanguage();
 useEffect(()=>{getMusobaqalar().then(data=>setItems(data.results||data)).finally(()=>setLoading(false))},[]);
 if(loading)return <Skeleton className="h-80 w-full"/>;
 const active=items.filter(item=>item.status==='faol');const finished=items.filter(item=>item.status==='yakun');
 return <div className="animate-in"><div className="competition-page-hero"><div className="competition-page-hero__icon"><Trophy size={28}/></div><div><span>{t('competition.live')}</span><h1>{t('nav.competitions')}</h1><p>Jonli testda qatnashing, tezlik va natija bo‘yicha reytingga kiring.</p></div></div>
 <h2 className="font-display font-bold mb-3">{t('competition.live')}</h2>{active.length?<div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-7">{active.map(item=><Card key={item.id} className="competition-student-card p-5" hover><div className="flex items-start gap-3"><span className="competition-student-card__icon"><Trophy size={20}/></span><div className="min-w-0 flex-1"><h3 className="font-display font-bold truncate">{item.nomi}</h3><p className="text-xs mt-1" style={{color:'var(--color-muted)'}}>{item.fan_nomi||'Barcha fanlar'}</p></div><Badge tone="warning">LIVE</Badge></div><p className="text-sm mt-3">{item.tavsif}</p><div className="competition-student-card__meta"><span><Sparkles size={15}/>{t('competition.questions',{count:item.savollar_soni})}</span><span><Clock3 size={15}/>{t('competition.minutes',{count:item.davomiyligi_daq})}</span></div><Button className="w-full mt-4" onClick={()=>navigate(`/oquvchi/musobaqalar/${item.id}`)}><Trophy size={17}/>{item.mening_urinishim?.status==='boshlandi'?'Davom ettirish':t('competition.enter')}</Button></Card>)}</div>:<EmptyState icon={Trophy} title={t('competition.activeEmpty')} description="Admin musobaqani boshlaganda shu yerda ko‘rinadi."/>}
 {finished.length>0&&<><h2 className="font-display font-bold mb-3 mt-8">Yakunlangan musobaqalar</h2><div className="grid grid-cols-1 lg:grid-cols-2 gap-4">{finished.map(item=><Card key={item.id} className="p-5"><div className="flex items-center gap-2"><Trophy size={18}/><h3 className="font-bold flex-1">{item.nomi}</h3><Badge tone="success">Yakun</Badge></div>{item.mening_urinishim&&<p className="mt-3 text-sm">Natijangiz: <b>{item.mening_urinishim.foiz}%</b></p>}</Card>)}</div></>}</div>;
}
