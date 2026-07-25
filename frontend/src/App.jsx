import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import PrivateRoute from './components/PrivateRoute';

import LoginPage from './pages/auth/LoginPage';

import AdminLayout from './pages/admin/AdminLayout';
import AdminDashboard from './pages/admin/AdminDashboard';
import FiliallarPage from './pages/admin/FiliallarPage';
import NazoratchilarPage from './pages/admin/NazoratchilarPage';
import AdminOquvchilarPage from './pages/admin/OquvchilarPage';
import AdminOquvchiProgressPage from './pages/admin/OquvchiProgressPage';
import FanlarPage from './pages/admin/FanlarPage';
import FanDetailPage from './pages/admin/FanDetailPage';
import DarsDetailPage from './pages/admin/DarsDetailPage';
import DarajaTestlarPage from './pages/admin/DarajaTestlarPage';
import AdminShopPage from './pages/admin/AdminShopPage';
import HisobotlarPage from './pages/admin/HisobotlarPage';
import AmalLoglariPage from './pages/admin/AmalLoglariPage';
import AdminSertifikatlarPage from './pages/admin/SertifikatlarPage';
import KuchliAnalitikaPage from './pages/admin/KuchliAnalitikaPage';
import AdminMurojaatlarPage from './pages/admin/MurojaatlarPage';
import SozlamalarPage from './pages/admin/SozlamalarPage';

import NazoratchiLayout from './pages/nazoratchi/NazoratchiLayout';
import NazoratchiDashboard from './pages/nazoratchi/NazoratchiDashboard';
import OquvchilarPage from './pages/nazoratchi/OquvchilarPage';
import OquvchiStatistikaPage from './pages/nazoratchi/OquvchiStatistikaPage';

import OquvchiLayout from './pages/oquvchi/OquvchiLayout';
import OquvchiDashboard from './pages/oquvchi/OquvchiDashboard';
import FanlarimPage from './pages/oquvchi/FanlarimPage';
import MavzularPage from './pages/oquvchi/MavzularPage';
import DarsPage from './pages/oquvchi/DarsPage';
import MashqPage from './pages/oquvchi/MashqPage';
import NatijalarimPage from './pages/oquvchi/NatijalarimPage';
import GateTestPage from './pages/oquvchi/GateTestPage';
import FinalTestPage from './pages/oquvchi/FinalTestPage';
import SertifikatlarimPage from './pages/oquvchi/SertifikatlarimPage';
import ShopPage from './pages/oquvchi/ShopPage';
import SozOyiniPage from './pages/oquvchi/SozOyiniPage';
import CertificateVerifyPage from './pages/public/CertificateVerifyPage';
import ShopBuyurtmalarPage from './pages/shared/ShopBuyurtmalarPage';
import XavfsizlikPage from './pages/shared/XavfsizlikPage';
import AIYordamchiPage from './pages/oquvchi/AIYordamchiPage';
import MurojaatlarimPage from './pages/oquvchi/MurojaatlarimPage';

function RootRedirect() {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  const redirects = { admin: '/admin', nazoratchi: '/nazoratchi', oquvchi: '/oquvchi' };
  return <Navigate to={redirects[user.role] || '/login'} replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
        <Routes>
          <Route path="/" element={<RootRedirect />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/sertifikat/:kod" element={<CertificateVerifyPage />} />

          {/* ADMIN */}
          <Route path="/admin" element={<PrivateRoute allowedRole="admin"><AdminLayout /></PrivateRoute>}>
            <Route index element={<AdminDashboard />} />
            <Route path="filiallar" element={<FiliallarPage />} />
            <Route path="nazoratchilar" element={<NazoratchilarPage />} />
            <Route path="oquvchilar" element={<AdminOquvchilarPage />} />
            <Route path="oquvchilar/:oquvchiId/progress" element={<AdminOquvchiProgressPage />} />
            <Route path="fanlar" element={<FanlarPage />} />
            <Route path="fanlar/:fanId" element={<FanDetailPage />} />
            <Route path="darslar/:darsId" element={<DarsDetailPage />} />
            <Route path="darajalar/:darajaId/testlar" element={<DarajaTestlarPage />} />
            <Route path="shop" element={<AdminShopPage />} />
            <Route path="shop-buyurtmalar" element={<ShopBuyurtmalarPage />} />
            <Route path="hisobotlar" element={<HisobotlarPage />} />
            <Route path="amal-loglari" element={<AmalLoglariPage />} />
            <Route path="sertifikatlar" element={<AdminSertifikatlarPage />} />
            <Route path="kuchli-analitika" element={<KuchliAnalitikaPage />} />
            <Route path="murojaatlar" element={<AdminMurojaatlarPage />} />
            <Route path="sozlamalar" element={<SozlamalarPage />} />
            <Route path="xavfsizlik" element={<XavfsizlikPage />} />
          </Route>

          {/* NAZORATCHI */}
          <Route path="/nazoratchi" element={<PrivateRoute allowedRole="nazoratchi"><NazoratchiLayout /></PrivateRoute>}>
            <Route index element={<NazoratchiDashboard />} />
            <Route path="oquvchilar" element={<OquvchilarPage />} />
            <Route path="oquvchilar/:oquvchiId" element={<OquvchiStatistikaPage />} />
            <Route path="shop-buyurtmalar" element={<ShopBuyurtmalarPage />} />
          </Route>

          {/* OQUVCHI */}
          <Route path="/oquvchi" element={<PrivateRoute allowedRole="oquvchi"><OquvchiLayout /></PrivateRoute>}>
            <Route index element={<OquvchiDashboard />} />
            <Route path="fanlarim" element={<FanlarimPage />} />
            <Route path="mavzular/:darajaId" element={<MavzularPage />} />
            <Route path="dars/:darsId" element={<DarsPage />} />
            <Route path="mashq/:mashqId" element={<MashqPage />} />
            <Route path="natijalarim" element={<NatijalarimPage />} />
            <Route path="gate-test/:darajaId" element={<GateTestPage />} />
            <Route path="final-test/:darajaId" element={<FinalTestPage />} />
            <Route path="sertifikatlarim" element={<SertifikatlarimPage />} />
            <Route path="soz-oyini" element={<SozOyiniPage />} />
            <Route path="shop" element={<ShopPage />} />
            <Route path="ai-yordamchi" element={<AIYordamchiPage />} />
            <Route path="murojaatlar" element={<MurojaatlarimPage />} />
            <Route path="xavfsizlik" element={<XavfsizlikPage />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
