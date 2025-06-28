import React from 'react';
import { Menu, Bell, Search, Sun, Moon, RefreshCw as Refresh, User } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { useData } from '../contexts/DataContext';
import ConnectionStatus from './ConnectionStatus';
import { useTranslation } from 'react-i18next';

interface HeaderProps {
  onMenuClick: () => void;
  sidebarOpen: boolean;
}

const Header: React.FC<HeaderProps> = ({ onMenuClick, sidebarOpen }) => {
  const { isDark, toggleTheme } = useTheme();
  const { refreshData, isLoading, alerts } = useData();
  const { t, i18n } = useTranslation();
  
  const activeAlerts = alerts.filter(alert => alert.status === 'active');
  const criticalAlerts = activeAlerts.filter(alert => alert.severity === 'critical');

  const handleThemeToggle = () => {
    toggleTheme();
  };

  const handleLanguageChange = (lng: string) => {
    i18n.changeLanguage(lng);
    localStorage.setItem('i18nextLng', lng);
  };

  return (
    <header className="h-16 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between px-6" role="banner">
      <div className="flex items-center space-x-4">
        <button
          onClick={onMenuClick}
          aria-label={sidebarOpen ? t('accessibility.closeMenu') : t('accessibility.openMenu')}
          className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
        >
          <Menu className="w-5 h-5 text-slate-600 dark:text-slate-400" />
        </button>
        
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search threats, assets, or alerts..."
            className="pl-10 pr-4 py-2 w-80 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyber-500 focus:border-transparent text-sm"
          />
        </div>
      </div>

      <div className="flex items-center space-x-3">
        {/* Connection Status */}
        <ConnectionStatus />

        {/* Refresh Button */}
        <button
          onClick={refreshData}
          disabled={isLoading}
          className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors disabled:opacity-50"
          title="Refresh Data"
        >
          <Refresh className={`w-5 h-5 text-slate-600 dark:text-slate-400 ${isLoading ? 'animate-spin' : ''}`} />
        </button>

        {/* Language Switcher */}
        <nav aria-label="Language selector">
          <button
            onClick={() => handleLanguageChange('en')}
            className={`px-2 py-1 rounded text-sm font-medium focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${i18n.language === 'en' ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300' : 'text-slate-700 dark:text-slate-200'}`}
            aria-pressed={i18n.language === 'en'}
            aria-label="Switch to English"
          >
            EN
          </button>
          <button
            onClick={() => handleLanguageChange('ne')}
            className={`ml-1 px-2 py-1 rounded text-sm font-medium focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${i18n.language === 'ne' ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300' : 'text-slate-700 dark:text-slate-200'}`}
            aria-pressed={i18n.language === 'ne'}
            aria-label="Switch to Nepali"
          >
            ने
          </button>
        </nav>

        {/* Theme Toggle */}
        <button
          onClick={handleThemeToggle}
          aria-label={isDark ? t('settings.light') : t('settings.dark')}
          className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
        >
          {isDark ? (
            <Sun className="w-5 h-5 text-yellow-400" />
          ) : (
            <Moon className="w-5 h-5 text-slate-700" />
          )}
        </button>

        {/* Notifications */}
        <div className="relative">
          <button className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
            <Bell className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            {criticalAlerts.length > 0 && (
              <span className="absolute -top-1 -right-1 w-5 h-5 bg-neon-red text-white text-xs rounded-full flex items-center justify-center animate-pulse-glow">
                {criticalAlerts.length}
              </span>
            )}
          </button>
        </div>

        {/* User Profile */}
        <div className="flex items-center space-x-3 pl-3 border-l border-slate-200 dark:border-slate-700">
          <div className="text-right">
            <div className="text-sm font-medium text-slate-900 dark:text-white">Security Admin</div>
            <div className="text-xs text-slate-500 dark:text-slate-400">admin@company.com</div>
          </div>
          <div className="w-8 h-8 bg-gradient-to-br from-cyber-400 to-cyber-600 rounded-full flex items-center justify-center">
            <User className="w-4 h-4 text-white" />
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;