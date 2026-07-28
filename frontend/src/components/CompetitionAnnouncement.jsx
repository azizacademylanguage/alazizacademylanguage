import { createPortal } from 'react-dom';
import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock3, Sparkles, Trophy, X } from 'lucide-react';
import { getFaolMusobaqalar } from '../api/competition';
import { useLanguage } from '../context/LanguageContext';
import { Button } from './ui';

const KEY='alaziz_dismissed_competitions';
const getHidden=()=>{try{return JSON.parse(sessionStorage.getItem(KEY)||'[]')}catch{return[]}};
export default function CompetitionAnnouncement(){
 const [items,setItems]=useState([]); const [hidden,setHidden]=useState(getHidden); const navigate=useNavigate(); const {t}=useLanguage();
 useEffect(()=>{let alive=true;const load=async()=>{if(!navigator.onLine)return;try{const data=await getFaolMusobaqalar();if(alive)setItems(Array.isArray(data)?data:data.results||[])}catch{}};load();const timer=setInterval(load,5000);addEventListener('online',load);return()=>{alive=false;clearInterval(timer);removeEventListener('online',load)}},[]);
 const active=useMemo(()=>items.find(item=>item.qatnashishi_mumkin&&!item.mening_urinishim?.status&&!hidden.includes(item.id)),[items,hidden]);
 useEffect(()=>{if(active)navigator.vibrate?.([80,50,120])},[active?.id]);
 if(!active)return null;
 const dismiss=()=>{const next=[...new Set([...hidden,active.id])];sessionStorage.setItem(KEY,JSON.stringify(next));setHidden(next)};
 const enter=()=>{dismiss();navigate(`/oquvchi/musobaqalar/${active.id}`)};
 return createPortal(<div className="competition-announcement" role="dialog" aria-modal="true"><div className="competition-announcement__confetti competition-announcement__confetti--one"/><div className="competition-announcement__confetti competition-announcement__confetti--two"/><div className="competition-announcement__confetti competition-announcement__confetti--three"/><div className="competition-announcement__card"><button type="button" className="competition-announcement__close" onClick={dismiss}><X size={18}/></button><div className="competition-announcement__trophy"><Trophy size={42}/></div><span className="competition-announcement__live"><span/>{t('competition.live')}</span><h2>{t('competition.startedTitle')}</h2><p>{t('competition.startedText',{name:active.nomi})}</p><div className="competition-announcement__meta"><span><Sparkles size={16}/>{t('competition.questions',{count:active.savollar_soni})}</span><span><Clock3 size={16}/>{t('competition.minutes',{count:active.davomiyligi_daq})}</span></div><div className="competition-announcement__actions"><Button variant="secondary" onClick={dismiss}>{t('competition.later')}</Button><Button onClick={enter}><Trophy size={17}/>{t('competition.enter')}</Button></div></div></div>,document.body);
}
