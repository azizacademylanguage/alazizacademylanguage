import { Outlet } from 'react-router-dom';
import DashboardLayout from '../../components/DashboardLayout';
import CoinBadge from '../../components/CoinBadge';
import { LayoutDashboard, BookOpen, ClipboardCheck, Award, ShoppingBag, Sparkles, MessagesSquare, ShieldCheck, Bell, BrainCircuit, Activity, Trophy, CreditCard, Zap } from 'lucide-react';

const navItems = [
  { to: '/oquvchi', label: 'Bosh sahifa', mobileLabel: 'Bosh', icon: LayoutDashboard, end: true },
  { to: '/oquvchi/fanlarim', label: 'Darajalarim', mobileLabel: 'Daraja', icon: BookOpen },
  { to: '/oquvchi/natijalarim', label: 'Natijalarim', mobileLabel: 'Natija', icon: ClipboardCheck },
  { to: '/oquvchi/sertifikatlarim', label: 'Sertifikatlarim', mobileLabel: 'Sertifikat', icon: Award },
  { to: '/oquvchi/tezkor-oyin', label: 'Tezkor tarjima', mobileLabel: "O‘yin", icon: Zap },
  { to: '/oquvchi/shop', label: "Do'kon", mobileLabel: "Do'kon", icon: ShoppingBag },
  { to: '/oquvchi/ai-yordamchi', label: 'AI yordamchi', mobileLabel: 'AI', icon: Sparkles },
  { to: '/oquvchi/placement-test', label: 'Darajani aniqlash', mobileLabel: 'Placement', icon: BrainCircuit },
  { to: '/oquvchi/bildirishnomalar', label: 'Bildirishnomalar', mobileLabel: 'Xabar', icon: Bell },
  { to: '/oquvchi/yutuqlarim', label: 'Yutuqlarim', mobileLabel: 'Yutuq', icon: Trophy },
  { to: '/oquvchi/faoliyatim', label: 'Faoliyatim', mobileLabel: 'Tarix', icon: Activity },
  { to: '/oquvchi/tolovim', label: 'To‘lovim', mobileLabel: 'To‘lov', icon: CreditCard },
  { to: '/oquvchi/murojaatlar', label: 'Murojaatlar', mobileLabel: 'Yordam', icon: MessagesSquare },
  { to: '/oquvchi/xavfsizlik', label: 'Xavfsizlik', mobileLabel: 'Xavfsiz', icon: ShieldCheck },
];

export default function OquvchiLayout() {
  return (
    <DashboardLayout navItems={navItems} extraSidebarContent={<CoinBadge />}>
      <Outlet />
    </DashboardLayout>
  );
}
