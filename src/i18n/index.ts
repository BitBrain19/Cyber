import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translations
import enTranslations from './locales/en.json';
import neTranslations from './locales/ne.json';

const resources = {
  en: {
    translation: enTranslations,
  },
  ne: {
    translation: neTranslations,
  },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    debug: process.env.NODE_ENV === 'development',
    
    interpolation: {
      escapeValue: false, // React already escapes values
    },
    
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
    },
    
    // Nepal-specific settings
    load: 'languageOnly',
    supportedLngs: ['en', 'ne'],
    
    // Performance optimizations
    react: {
      useSuspense: false,
    },
  });

export default i18n; 