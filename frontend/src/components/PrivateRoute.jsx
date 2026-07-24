import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function PrivateRoute({ children, allowedRole }) {
  const { user } = useAuth();

  if (!user) return <Navigate to="/login" replace />;
  if (allowedRole && user.role !== allowedRole) {
    const redirects = { admin: '/admin', nazoratchi: '/nazoratchi', oquvchi: '/oquvchi' };
    return <Navigate to={redirects[user.role] || '/login'} replace />;
  }
  return children;
}
