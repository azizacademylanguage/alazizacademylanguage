import { createContext, useContext, useState, useCallback } from 'react';
import { Toast } from '../components/ui';

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toast, setToast] = useState(null);

  const showToast = useCallback((message, tone = 'success') => {
    setToast({ message, tone, key: Date.now() });
  }, []);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {toast && <Toast key={toast.key} message={toast.message} tone={toast.tone} onClose={() => setToast(null)} />}
    </ToastContext.Provider>
  );
}

export const useToast = () => useContext(ToastContext);
