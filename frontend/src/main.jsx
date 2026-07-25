import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import './index.css';
import { ThemeProvider } from './theme/ThemeContext.jsx';
import { LanguageProvider } from './i18n/LanguageContext.jsx';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ThemeProvider>
      <LanguageProvider>
        <App/>
      </LanguageProvider>
    </ThemeProvider>
  </StrictMode>
);
