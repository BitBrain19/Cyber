import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Shield, 
  AlertTriangle, 
  Activity, 
  FileText, 
  Settings, 
  Zap,
  Network,
  Eye
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
}

const menuItems = [
  { path: '/', icon: Activity, label: 'Dashboard', description: 'Overview & Metrics' },
  { path: '/alerts', icon: AlertTriangle, label: 'Alerts', description: 'Threat Notifications' },
  { path: '/attack-paths', icon: Network, label: 'Attack Paths', description: 'Network Analysis' },
  { path: '/reports', icon: FileText, label: 'Reports', description: 'Analytics & Compliance' },
  { path: '/settings', icon: Settings, label: 'Settings', description: 'Configuration' },
];

const Sidebar: React.FC<SidebarProps> = ({ isOpen }) => {
  const location = useLocation();

  return (
    <aside className={`fixed left-0 top-0 h-full bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 transition-all duration-300 z-30 ${
      isOpen ? 'w-64' : 'w-16'
    }`}>
      <div className="flex flex-col h-full">
        {/* Logo */}
        <div className="flex items-center h-16 px-4 border-b border-slate-200 dark:border-slate-700">
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-cyber-400 to-cyber-600 text-white">
              <Shield className="w-5 h-5" />
            </div>
            {isOpen && (
              <div className="animate-fade-in">
                <h1 className="text-xl font-bold text-slate-900 dark:text-white">
                  <span className="text-cyber-500">Cyber</span>Guard AI
                </h1>
                <p className="text-xs text-slate-500 dark:text-slate-400">Threat Detection</p>
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center px-3 py-3 rounded-lg transition-all duration-200 group ${
                  isActive
                    ? 'bg-cyber-50 dark:bg-cyber-900/20 text-cyber-600 dark:text-cyber-400 shadow-sm'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <Icon className={`w-5 h-5 transition-colors ${isActive ? 'text-cyber-500' : ''}`} />
                {isOpen && (
                  <div className="ml-3 animate-fade-in">
                    <div className="text-sm font-medium">{item.label}</div>
                    <div className="text-xs opacity-75">{item.description}</div>
                  </div>
                )}
                {!isOpen && isActive && (
                  <div className="absolute left-16 bg-slate-900 text-white px-2 py-1 rounded text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity">
                    {item.label}
                  </div>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Status Indicator */}
        <div className="p-4 border-t border-slate-200 dark:border-slate-700">
          <div className={`flex items-center ${isOpen ? 'justify-between' : 'justify-center'}`}>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-neon-green rounded-full animate-pulse"></div>
              {isOpen && (
                <div className="animate-fade-in">
                  <div className="text-xs font-medium text-slate-900 dark:text-white">System Active</div>
                  <div className="text-xs text-slate-500 dark:text-slate-400">All systems operational</div>
                </div>
              )}
            </div>
            {isOpen && (
              <Zap className="w-4 h-4 text-neon-green animate-pulse" />
            )}
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;