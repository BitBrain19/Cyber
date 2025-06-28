import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { FileText, Download, Calendar, TrendingUp, Shield, AlertTriangle, Clock, Users } from 'lucide-react';
import { useData } from '../contexts/DataContext';
import MetricCard from '../components/MetricCard';

const Reports: React.FC = () => {
  const { threatMetrics, systemHealth, alerts } = useData();
  const [selectedPeriod, setSelectedPeriod] = useState('7d');
  const [selectedReport, setSelectedReport] = useState('security-overview');

  const threatsByCategory = [
    { name: 'Malware', value: 23, color: '#ef4444' },
    { name: 'Phishing', value: 18, color: '#f97316' },
    { name: 'Intrusion', value: 15, color: '#eab308' },
    { name: 'Data Breach', value: 12, color: '#10b981' },
    { name: 'Insider Threat', value: 8, color: '#6366f1' },
  ];

  const complianceMetrics = [
    { name: 'ISO 27001', score: 94, status: 'Compliant' },
    { name: 'SOC 2', score: 89, status: 'Compliant' },
    { name: 'GDPR', score: 96, status: 'Compliant' },
    { name: 'PCI DSS', score: 87, status: 'Needs Review' },
  ];

  const monthlyTrends = [
    { month: 'Jan', threats: 45, resolved: 42, incidents: 3 },
    { month: 'Feb', threats: 52, resolved: 48, incidents: 4 },
    { month: 'Mar', threats: 38, resolved: 36, incidents: 2 },
    { month: 'Apr', threats: 61, resolved: 55, incidents: 6 },
    { month: 'May', threats: 43, resolved: 41, incidents: 2 },
    { month: 'Jun', threats: 58, resolved: 54, incidents: 4 },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Security Reports</h1>
          <p className="text-slate-600 dark:text-slate-400 mt-1">Comprehensive analytics and compliance reporting</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyber-500"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
          <button className="flex items-center space-x-2 px-4 py-2 bg-cyber-500 text-white rounded-lg hover:bg-cyber-600 transition-colors">
            <Download className="w-4 h-4" />
            <span>Export Report</span>
          </button>
        </div>
      </div>

      {/* Report Type Selector */}
      <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-700">
        <div className="flex space-x-4">
          <button
            onClick={() => setSelectedReport('security-overview')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              selectedReport === 'security-overview'
                ? 'bg-cyber-500 text-white'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700'
            }`}
          >
            Security Overview
          </button>
          <button
            onClick={() => setSelectedReport('compliance')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              selectedReport === 'compliance'
                ? 'bg-cyber-500 text-white'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700'
            }`}
          >
            Compliance
          </button>
          <button
            onClick={() => setSelectedReport('incident-analysis')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              selectedReport === 'incident-analysis'
                ? 'bg-cyber-500 text-white'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700'
            }`}
          >
            Incident Analysis
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Threats Detected"
          value={threatMetrics.totalThreats}
          icon={Shield}
          trend={{ value: 12, isPositive: false }}
          color="cyber"
        />
        <MetricCard
          title="Incidents Resolved"
          value={alerts.filter(a => a.status === 'resolved').length}
          icon={AlertTriangle}
          trend={{ value: 8, isPositive: true }}
          color="green"
        />
        <MetricCard
          title="Mean Response Time"
          value={`${threatMetrics.averageResponseTime}m`}
          icon={Clock}
          trend={{ value: 15, isPositive: true }}
          color="purple"
        />
        <MetricCard
          title="System Uptime"
          value={`${systemHealth.overallScore}%`}
          icon={TrendingUp}
          trend={{ value: 2, isPositive: true }}
          color="green"
        />
      </div>

      {selectedReport === 'security-overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Monthly Trends */}
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-700">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Monthly Security Trends</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={monthlyTrends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
                <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={12} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1e293b', 
                    border: '1px solid #334155', 
                    borderRadius: '8px',
                    color: '#f1f5f9'
                  }} 
                />
                <Line type="monotone" dataKey="threats" stroke="#ef4444" strokeWidth={2} name="Threats" />
                <Line type="monotone" dataKey="resolved" stroke="#10b981" strokeWidth={2} name="Resolved" />
                <Line type="monotone" dataKey="incidents" stroke="#f97316" strokeWidth={2} name="Incidents" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Threat Categories */}
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-700">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Threat Categories</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={threatsByCategory}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={120}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {threatsByCategory.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1e293b', 
                    border: '1px solid #334155', 
                    borderRadius: '8px',
                    color: '#f1f5f9'
                  }} 
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 grid grid-cols-1 gap-2">
              {threatsByCategory.map((item, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: item.color }}
                    ></div>
                    <span className="text-sm text-slate-600 dark:text-slate-400">{item.name}</span>
                  </div>
                  <span className="text-sm font-medium text-slate-900 dark:text-white">{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {selectedReport === 'compliance' && (
        <div className="space-y-6">
          {/* Compliance Overview */}
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-700">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-6">Compliance Status</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {complianceMetrics.map((metric, index) => (
                <div key={index} className="p-4 border border-slate-200 dark:border-slate-700 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-slate-900 dark:text-white">{metric.name}</h4>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      metric.status === 'Compliant' 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                    }`}>
                      {metric.status}
                    </span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="flex-1 bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                      <div 
                        className="h-2 rounded-full bg-gradient-to-r from-cyber-400 to-cyber-600"
                        style={{ width: `${metric.score}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium text-slate-900 dark:text-white">
                      {metric.score}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Compliance Details */}
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-700">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Detailed Compliance Report</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-slate-700">
                    <th className="text-left py-3 text-slate-600 dark:text-slate-400 font-medium">Control</th>
                    <th className="text-left py-3 text-slate-600 dark:text-slate-400 font-medium">Status</th>
                    <th className="text-left py-3 text-slate-600 dark:text-slate-400 font-medium">Last Audit</th>
                    <th className="text-left py-3 text-slate-600 dark:text-slate-400 font-medium">Next Review</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-slate-100 dark:border-slate-700">
                    <td className="py-3 text-slate-900 dark:text-white">Access Control</td>
                    <td className="py-3">
                      <span className="px-2 py-1 text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded-full">
                        Compliant
                      </span>
                    </td>
                    <td className="py-3 text-slate-600 dark:text-slate-400">2024-01-15</td>
                    <td className="py-3 text-slate-600 dark:text-slate-400">2024-04-15</td>
                  </tr>
                  <tr className="border-b border-slate-100 dark:border-slate-700">
                    <td className="py-3 text-slate-900 dark:text-white">Data Encryption</td>
                    <td className="py-3">
                      <span className="px-2 py-1 text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded-full">
                        Compliant
                      </span>
                    </td>
                    <td className="py-3 text-slate-600 dark:text-slate-400">2024-01-10</td>
                    <td className="py-3 text-slate-600 dark:text-slate-400">2024-04-10</td>
                  </tr>
                  <tr className="border-b border-slate-100 dark:border-slate-700">
                    <td className="py-3 text-slate-900 dark:text-white">Incident Response</td>
                    <td className="py-3">
                      <span className="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 rounded-full">
                        Review Required
                      </span>
                    </td>
                    <td className="py-3 text-slate-600 dark:text-slate-400">2023-12-20</td>
                    <td className="py-3 text-slate-600 dark:text-slate-400">2024-03-20</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {selectedReport === 'incident-analysis' && (
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-700">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-6">Incident Analysis</h3>
          <div className="space-y-4">
            <div className="p-4 border border-slate-200 dark:border-slate-700 rounded-lg">
              <h4 className="font-medium text-slate-900 dark:text-white mb-2">Recent High-Priority Incidents</h4>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-slate-900 dark:text-white">Malware Detection - WEB-SERVER-01</div>
                    <div className="text-sm text-slate-600 dark:text-slate-400">Resolved in 45 minutes</div>
                  </div>
                  <span className="px-2 py-1 text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded-full">
                    Resolved
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-slate-900 dark:text-white">Unusual Login Activity</div>
                    <div className="text-sm text-slate-600 dark:text-slate-400">Under investigation</div>
                  </div>
                  <span className="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 rounded-full">
                    Investigating
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Reports;