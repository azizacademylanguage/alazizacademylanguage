import { createContext, useContext, useState } from 'react';
import { login as apiLogin, logout as apiLogout, getStoredUser } from '../api/auth';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(getStoredUser());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const login = async (username, password) => {
    setLoading(true);
    setError('');
    try {
      const u = await apiLogin(username, password);
      setUser(u);
      return u;
    } catch (e) {
      let msg = e.response?.data?.detail;
      if (!e.response) {
        msg = "Server bilan ulanib bo'lmadi. Railway backend manzili va Netlify VITE_API_BASE_URL sozlamasini tekshiring.";
      } else if (e.response.status >= 500) {
        msg = "Serverda xatolik yuz berdi. Railway loglarini tekshiring.";
      } else if (!msg) {
        msg = "Login yoki parol noto'g'ri.";
      }
      setError(msg);
      throw e;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    apiLogout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading, error, setError }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
