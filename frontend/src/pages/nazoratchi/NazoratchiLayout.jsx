import { Outlet } from 'react-router-dom';
import DashboardLayout from '../../components/DashboardLayout';
import { LayoutDashboard, GraduationCap, PackageCheck } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

export default function NazoratchiLayout() {
  const { t } = useLanguage();
  const navItems = [
    { to: '/nazoratchi', label: t('nav.dashboard'), mobileLabel: t('mobile.home'), icon: LayoutDashboard, end: true },
    { to: '/nazoratchi/oquvchilar', label: t('nav.myStudents'), mobileLabel: t('mobile.student'), icon: GraduationCap },
    { to: '/nazoratchi/shop-buyurtmalar', label: t('nav.orders'), mobileLabel: t('mobile.orders'), icon: PackageCheck },
  ];
  return <DashboardLayout navItems={navItems}><Outlet /></DashboardLayout>;
}
