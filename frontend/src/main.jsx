import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.jsx';
import { LanguageProvider } from './context/LanguageContext.jsx';
import { ConnectivityProvider } from './context/ConnectivityContext.jsx';

window.addEventListener('beforeinstallprompt', (event) => {
  event.preventDefault();
  window.__pwaInstallPrompt = event;
  window.dispatchEvent(new CustomEvent('pwa-install-ready', { detail: event }));
});

if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js', { updateViaCache: 'none' })
      .then((registration) => registration.update())
      .catch(() => {});
  });
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <LanguageProvider>
      <ConnectivityProvider>
        <App />
      </ConnectivityProvider>
    </LanguageProvider>
  </StrictMode>,
);
