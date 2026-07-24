import { Outlet } from 'react-router-dom';
import DashboardLayout from '../../components/DashboardLayout';
import { LayoutDashboard, Building2, Users, UserRoundPlus, BookOpen, ShoppingBag, FileClock, Download, Award, PackageCheck } from 'lucide-react';

const navItems = [
  { to: '/admin', label: 'Boshqaruv paneli', mobileLabel: 'Bosh', icon: LayoutDashboard, end: true },
  { to: '/admin/filiallar', label: 'Filiallar', mobileLabel: 'Filial', icon: Building2 },
  { to: '/admin/nazoratchilar', label: 'Nazoratchilar', mobileLabel: 'Rahbar', icon: Users },
  { to: '/admin/oquvchilar', label: "O'quvchilar", mobileLabel: "O'quvchi", icon: UserRoundPlus },
  { to: '/admin/sertifikatlar', label: 'Sertifikatlar', mobileLabel: 'Sertifikat', icon: Award },
  { to: '/admin/fanlar', label: "Ta'lim mazmuni", mobileLabel: "Ta'lim", icon: BookOpen },
  { to: '/admin/shop', label: "Do'kon", mobileLabel: "Do'kon", icon: ShoppingBag },
  { to: '/admin/shop-buyurtmalar', label: 'Do‘kon xaridlari', mobileLabel: 'Xaridlar', icon: PackageCheck },
  { to: '/admin/hisobotlar', label: 'Hisobotlar', mobileLabel: 'Hisobot', icon: Download },
  { to: '/admin/amal-loglari', label: 'Amal loglari', mobileLabel: 'Loglar', icon: FileClock },
];

export default function AdminLayout() {
  return (
    <DashboardLayout navItems={navItems}>
      <Outlet />
    </DashboardLayout>
  );
}
