import { Outlet } from 'react-router-dom';
import DashboardLayout from '../../components/DashboardLayout';
import { LayoutDashboard, Building2, Users, UserRoundPlus, BookOpen, ShoppingBag, FileClock, Download, Award, PackageCheck, BarChart3, Trophy, UsersRound } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

export default function AdminLayout() {
  const { t } = useLanguage();
  const navItems = [
    { to: '/admin', label: t('nav.dashboard'), mobileLabel: t('mobile.home'), icon: LayoutDashboard, end: true },
    { to: '/admin/kengaytirilgan-statistika', label: t('nav.statistics'), mobileLabel: t('mobile.statistics'), icon: BarChart3 },
    { to: '/admin/musobaqalar', label: t('nav.competitions'), mobileLabel: t('mobile.ranking'), icon: Trophy },
    { to: '/admin/filiallar', label: t('nav.branches'), mobileLabel: t('mobile.branch'), icon: Building2 },
    { to: '/admin/nazoratchilar', label: t('nav.supervisors'), mobileLabel: t('mobile.supervisor'), icon: Users },
    { to: '/admin/oquvchilar', label: t('nav.students'), mobileLabel: t('mobile.student'), icon: UserRoundPlus },
    { to: '/admin/foydalanuvchilar', label: t('nav.users'), mobileLabel: t('mobile.users'), icon: UsersRound },
    { to: '/admin/sertifikatlar', label: t('nav.certificates'), mobileLabel: t('mobile.certificate'), icon: Award },
    { to: '/admin/fanlar', label: t('nav.content'), mobileLabel: t('mobile.content'), icon: BookOpen },
    { to: '/admin/shop', label: t('nav.shop'), mobileLabel: t('mobile.shop'), icon: ShoppingBag },
    { to: '/admin/shop-buyurtmalar', label: t('nav.orders'), mobileLabel: t('mobile.orders'), icon: PackageCheck },
    { to: '/admin/hisobotlar', label: t('nav.reports'), mobileLabel: t('mobile.report'), icon: Download },
    { to: '/admin/amal-loglari', label: t('nav.audit'), mobileLabel: t('mobile.audit'), icon: FileClock },
  ];
  return <DashboardLayout navItems={navItems}><Outlet /></DashboardLayout>;
}
