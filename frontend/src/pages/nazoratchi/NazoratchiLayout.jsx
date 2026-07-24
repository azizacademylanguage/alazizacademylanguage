import { Outlet } from 'react-router-dom';
import DashboardLayout from '../../components/DashboardLayout';
import { LayoutDashboard, GraduationCap, PackageCheck } from 'lucide-react';

const navItems = [
  { to: '/nazoratchi', label: 'Boshqaruv paneli', mobileLabel: 'Bosh', icon: LayoutDashboard, end: true },
  { to: '/nazoratchi/oquvchilar', label: "O'quvchilarim", mobileLabel: "O'quvchi", icon: GraduationCap },
  { to: '/nazoratchi/shop-buyurtmalar', label: 'Do‘kon xaridlari', mobileLabel: 'Xaridlar', icon: PackageCheck },
];

export default function NazoratchiLayout() {
  return (
    <DashboardLayout navItems={navItems}>
      <Outlet />
    </DashboardLayout>
  );
}
