import { Outlet } from 'react-router-dom';
import DashboardLayout from '../../components/DashboardLayout';
import CoinBadge from '../../components/CoinBadge';
import { LayoutDashboard, BookOpen, ClipboardCheck, Award, ShoppingBag, Brain, Bell, Trophy } from 'lucide-react';

const navItems = [
  { to: '/oquvchi', label: 'Bosh sahifa', mobileLabel: 'Bosh', icon: LayoutDashboard, end: true },
  { to: '/oquvchi/fanlarim', label: 'Darajalarim', mobileLabel: 'Daraja', icon: BookOpen },
  { to: '/oquvchi/natijalarim', label: 'Natijalarim', mobileLabel: 'Natija', icon: ClipboardCheck },
  { to: '/oquvchi/sertifikatlarim', label: 'Sertifikatlarim', mobileLabel: 'Sertifikat', icon: Award },
  { to: '/oquvchi/bildirishnomalar', label: 'Bildirishnomalar', mobileLabel: 'Xabar', icon: Bell },
  { to: '/oquvchi/soz-oyini', label: "So'z o'yini", mobileLabel: "O'yin", icon: Brain },
  { to: '/oquvchi/reyting', label: 'Reyting', mobileLabel: 'Reyting', icon: Trophy },
  { to: '/oquvchi/shop', label: "Do'kon", mobileLabel: "Do'kon", icon: ShoppingBag },
];

export default function OquvchiLayout() {
  return (
    <DashboardLayout navItems={navItems} extraSidebarContent={<CoinBadge />}>
      <Outlet />
    </DashboardLayout>
  );
}
