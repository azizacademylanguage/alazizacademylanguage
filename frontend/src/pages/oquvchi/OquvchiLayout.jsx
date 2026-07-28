import { Outlet } from 'react-router-dom';
import DashboardLayout from '../../components/DashboardLayout';
import CoinBadge from '../../components/CoinBadge';
import { LayoutDashboard, BookOpen, ClipboardCheck, Award, ShoppingBag, Brain, Bell, Trophy, CloudDownload, Swords } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';
import CompetitionAnnouncement from '../../components/CompetitionAnnouncement';

export default function OquvchiLayout() {
  const { t } = useLanguage();
  const navItems = [
    { to: '/oquvchi', label: t('nav.home'), mobileLabel: t('mobile.home'), icon: LayoutDashboard, end: true },
    { to: '/oquvchi/fanlarim', label: t('nav.levels'), mobileLabel: t('mobile.level'), icon: BookOpen },
    { to: '/oquvchi/offline', label: t('nav.offline'), mobileLabel: t('mobile.offline'), icon: CloudDownload },
    { to: '/oquvchi/reyting', label: t('nav.ranking'), mobileLabel: t('mobile.ranking'), icon: Trophy },
    { to: '/oquvchi/musobaqalar', label: t('nav.competitions'), mobileLabel: t('mobile.competition'), icon: Swords },
    { to: '/oquvchi/natijalarim', label: t('nav.results'), mobileLabel: t('mobile.result'), icon: ClipboardCheck },
    { to: '/oquvchi/sertifikatlarim', label: t('nav.myCertificates'), mobileLabel: t('mobile.certificate'), icon: Award },
    { to: '/oquvchi/bildirishnomalar', label: t('nav.notifications'), mobileLabel: t('mobile.notification'), icon: Bell },
    { to: '/oquvchi/soz-oyini', label: t('nav.wordGame'), mobileLabel: t('mobile.game'), icon: Brain },
    { to: '/oquvchi/shop', label: t('nav.shop'), mobileLabel: t('mobile.shop'), icon: ShoppingBag },
  ];
  return (
    <>
      <CompetitionAnnouncement />
      <DashboardLayout navItems={navItems} extraSidebarContent={<CoinBadge />}>
      <Outlet />
      </DashboardLayout>
    </>
  );
}
