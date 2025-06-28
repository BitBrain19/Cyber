import React, { useState } from 'react';
import { Settings as SettingsIcon, Shield, Bell, Database, Users, Key, Palette, Monitor } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

const Settings: React.FC = () => {
  const { isDark, toggleTheme } = useTheme();
  const [activeSection, setActiveSection] = useState('general');
  const [notifications, setNotifications] = useState({
    criticalAlerts: true,
    weeklyReports: true,
    systemUpdates: false,
    maintenanceWindows: true,
  });

  const sections = [
    { id: 'general', name: 'General', icon: SettingsIcon },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'integrations', name: 'Integrations', icon: Database },
    { id: 'users', name: 'User Management', icon: Users },
    { id: 'api', name: 'API Keys', icon: Key },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Settings</h1>
        <p className="text-slate-600 dark:text-slate-400 mt-1">Configure your security monitoring preferences</p>
      </div>

      <div className="flex space-x-6">
        {/* Sidebar */}
        <div className="w-64 bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700">
          <nav className="p-4 space-y-2">
            {sections.map((section) => {
              const Icon = section.icon;
              return (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                    activeSection === section.id
                      ? 'bg-cyber-50 dark:bg-cyber-900/20 text-cyber-600 dark:text-cyber-400'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{section.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1 bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700">
          <div className="p-6">
            {activeSection === 'general' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-4">General Settings</h2>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <label className="text-sm font-medium text-slate-900 dark:text-white">Theme</label>
                      <p className="text-sm text-slate-600 dark:text-slate-400">Choose your preferred theme</p>
                    </div>
                    <button
                      onClick={toggleTheme}
                      className={`flex items-center space-x-2 px-4 py-2 rounded-lg border transition-colors ${
                        isDark
                          ? 'bg-slate-700 border-slate-600 text-white'
                          : 'bg-white border-slate-300 text-slate-900'
                      }`}
                    >
                      {isDark ? <Monitor className="w-4 h-4" /> : <Palette className="w-4 h-4" />}
                      <span>{isDark ? 'Dark Mode' : 'Light Mode'}</span>
                    </button>
                  </div>

                  <div className="border-t border-slate-200 dark:border-slate-700 pt-4">
                    <div>
                      <label className="text-sm font-medium text-slate-900 dark:text-white">Dashboard Refresh Rate</label>
                      <p className="text-sm text-slate-600 dark:text-slate-400">How often to update dashboard data</p>
                    </div>
                    <select className="mt-2 px-3 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyber-500">
                      <option>30 seconds</option>
                      <option>1 minute</option>
                      <option>5 minutes</option>
                      <option>Manual</option>
                    </select>
                  </div>

                  <div className="border-t border-slate-200 dark:border-slate-700 pt-4">
                    <div>
                      <label className="text-sm font-medium text-slate-900 dark:text-white">Time Zone</label>
                      <p className="text-sm text-slate-600 dark:text-slate-400">Your local time zone for reports</p>
                    </div>
                    <select className="mt-2 px-3 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyber-500">
                      <option>UTC</option>
                      <option>America/New_York</option>
                      <option>America/Los_Angeles</option>
                      <option>Europe/London</option>
                      <option>Asia/Tokyo</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'security' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-4">Security Settings</h2>
                </div>

                <div className="space-y-4">
                  <div className="p-4 border border-slate-200 dark:border-slate-700 rounded-lg">
                    <h3 className="font-medium text-slate-900 dark:text-white mb-2">Threat Detection Sensitivity</h3>
                    <div className="space-y-2">
                      <label className="flex items-center">
                        <input type="radio" name="sensitivity" className="mr-2" defaultChecked />
                        <span className="text-sm text-slate-600 dark:text-slate-400">High (More alerts, fewer false negatives)</span>
                      </label>
                      <label className="flex items-center">
                        <input type="radio" name="sensitivity" className="mr-2" />
                        <span className="text-sm text-slate-600 dark:text-slate-400">Medium (Balanced)</span>
                      </label>
                      <label className="flex items-center">
                        <input type="radio" name="sensitivity" className="mr-2" />
                        <span className="text-sm text-slate-600 dark:text-slate-400">Low (Fewer alerts, more false negatives)</span>
                      </label>
                    </div>
                  </div>

                  <div className="p-4 border border-slate-200 dark:border-slate-700 rounded-lg">
                    <h3 className="font-medium text-slate-900 dark:text-white mb-2">Auto-Response Actions</h3>
                    <div className="space-y-2">
                      <label className="flex items-center">
                        <input type="checkbox" className="mr-2" defaultChecked />
                        <span className="text-sm text-slate-600 dark:text-slate-400">Auto-block suspicious IPs</span>
                      </label>
                      <label className="flex items-center">
                        <input type="checkbox" className="mr-2" />
                        <span className="text-sm text-slate-600 dark:text-slate-400">Auto-quarantine malware</span>
                      </label>
                      <label className="flex items-center">
                        <input type="checkbox" className="mr-2" defaultChecked />
                        <span className="text-sm text-slate-600 dark:text-slate-400">Auto-disable compromised accounts</span>
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'notifications' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-4">Notification Settings</h2>
                </div>

                <div className="space-y-4">
                  {Object.entries(notifications).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between py-3 border-b border-slate-200 dark:border-slate-700 last:border-b-0">
                      <div>
                        <label className="text-sm font-medium text-slate-900 dark:text-white">
                          {key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1')}
                        </label>
                        <p className="text-sm text-slate-600 dark:text-slate-400">
                          {key === 'criticalAlerts' && 'Immediate notifications for critical security threats'}
                          {key === 'weeklyReports' && 'Weekly security summary reports'}
                          {key === 'systemUpdates' && 'Notifications about system updates and maintenance'}
                          {key === 'maintenanceWindows' && 'Scheduled maintenance notifications'}
                        </p>
                      </div>
                      <button
                        onClick={() => setNotifications(prev => ({ ...prev, [key]: !value }))}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          value ? 'bg-cyber-500' : 'bg-slate-300 dark:bg-slate-600'
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            value ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeSection === 'integrations' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-4">Integrations</h2>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {[
                    { name: 'Splunk', status: 'Connected', logo: '🔍' },
                    { name: 'Elasticsearch', status: 'Connected', logo: '🔎' },
                    { name: 'Slack', status: 'Not Connected', logo: '💬' },
                    { name: 'Microsoft Sentinel', status: 'Not Connected', logo: '🛡️' },
                  ].map((integration) => (
                    <div key={integration.name} className="p-4 border border-slate-200 dark:border-slate-700 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <span className="text-2xl">{integration.logo}</span>
                          <div>
                            <h3 className="font-medium text-slate-900 dark:text-white">{integration.name}</h3>
                            <p className="text-sm text-slate-600 dark:text-slate-400">{integration.status}</p>
                          </div>
                        </div>
                        <button
                          className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                            integration.status === 'Connected'
                              ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 hover:bg-red-200'
                              : 'bg-cyber-100 text-cyber-800 dark:bg-cyber-900 dark:text-cyber-200 hover:bg-cyber-200'
                          }`}
                        >
                          {integration.status === 'Connected' ? 'Disconnect' : 'Connect'}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeSection === 'api' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-4">API Keys</h2>
                </div>

                <div className="space-y-4">
                  <div className="p-4 border border-slate-200 dark:border-slate-700 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium text-slate-900 dark:text-white">Production API Key</h3>
                      <span className="px-2 py-1 text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded-full">
                        Active
                      </span>
                    </div>
                    <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">
                      Used for production integrations and automated responses
                    </p>
                    <div className="flex items-center space-x-2">
                      <code className="flex-1 px-3 py-2 bg-slate-100 dark:bg-slate-700 rounded text-sm font-mono">
                        sk_live_••••••••••••••••••••••••••••••••
                      </code>
                      <button className="px-3 py-2 bg-slate-500 text-white rounded hover:bg-slate-600 transition-colors text-sm">
                        Regenerate
                      </button>
                    </div>
                  </div>

                  <button className="w-full p-4 border-2 border-dashed border-slate-300 dark:border-slate-600 rounded-lg text-slate-600 dark:text-slate-400 hover:border-cyber-500 hover:text-cyber-500 transition-colors">
                    + Create New API Key
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;