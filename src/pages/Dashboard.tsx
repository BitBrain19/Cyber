import React from 'react';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { Shield, AlertTriangle, Activity, Clock, TrendingUp, Users, Database, Network } from 'lucide-react';
import { useData } from '../contexts/DataContext';
import MetricCard from '../components/MetricCard';
import AlertCard from '../components/AlertCard';
import ThreatScoreGauge from '../components/ThreatScoreGauge';
import { useTranslation } from 'react-i18next';

const Dashboard: React.FC = () => {
  const { alerts, threatMetrics, systemHealth } = useData();
  const { t } = useTranslation();
  
  const recentAlerts = alerts.slice(0, 5);
  const overallThreatScore = Math.round(
    (threatMetrics.criticalThreats * 100 + threatMetrics.highThreats * 70 + 
     threatMetrics.mediumThreats * 40 + threatMetrics.lowThreats * 20) / 
    Math.max(threatMetrics.totalThreats, 1)
  );

  const severityData = [
    { name: t('alerts.critical'), value: threatMetrics.criticalThreats, color: '#ef4444' },
    { name: t('alerts.high'), value: threatMetrics.highThreats, color: '#f97316' },
    { name: t('alerts.medium'), value: threatMetrics.mediumThreats, color: '#eab308' },
    { name: t('alerts.low'), value: threatMetrics.lowThreats, color: '#10b981' }
  ];

  const systemMetrics = [
    { name: t('monitoring.cpuUsage'), value: systemHealth.cpuUsage, color: '#00d9ff' },
    { name: t('monitoring.memoryUsage'), value: systemHealth.memoryUsage, color: '#a855f7' },
    { name: t('monitoring.diskUsage'), value: systemHealth.diskUsage, color: '#ec4899' },
    { name: t('monitoring.networkLatency'), value: systemHealth.networkLatency, color: '#10b981' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">{t('dashboard.title')}</h1>
          <p className="text-slate-600 dark:text-slate-400 mt-1">{t('dashboard.subtitle')}</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <div className="text-sm text-slate-500 dark:text-slate-400">{t('dashboard.lastUpdated')}</div>
            <div className="text-sm font-medium text-slate-900 dark:text-white">
              {new Date().toLocaleTimeString()}
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title={t('dashboard.totalThreats')}
          value={threatMetrics.totalThreats}
          icon={Shield}
          trend={{ value: 12, isPositive: false }}
          color="cyber"
        />
        <MetricCard
          title={t('dashboard.criticalAlerts')}
          value={threatMetrics.criticalThreats}
          icon={AlertTriangle}
          trend={{ value: 8, isPositive: false }}
          color="red"
        />
        <MetricCard
          title={t('dashboard.systemHealth')}
          value={`${systemHealth.overallScore}%`}
          icon={Activity}
          trend={{ value: 3, isPositive: true }}
          color="green"
        />
        <MetricCard
          title={t('dashboard.avgResponseTime')}
          value={`${threatMetrics.averageResponseTime}m`}
          icon={Clock}
          trend={{ value: 15, isPositive: true }}
          color="purple"
          subtitle={t('dashboard.meanTimeToAcknowledge')}
        />
      </div>

      {/* Main Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Threat Score Gauge */}
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-700">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">{t('dashboard.overallThreatLevel')}</h3>
          <div className="flex justify-center">
            <ThreatScoreGauge score={overallThreatScore} size="lg" />
          </div>
          <div className="mt-4 text-center">
            <p className="text-sm text-slate-600 dark:text-slate-400">
              {t('dashboard.basedOnActiveThreats', { count: threatMetrics.totalThreats })}
            </p>
          </div>
        </div>

        {/* Threat Trend Chart */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-700">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">{t('dashboard.threatTrends')}</h3>
          <ResponsiveContainer width="100%" height={200} aria-label={t('dashboard.threatTrends')} role="region">
            <AreaChart data={threatMetrics.threatTrend}>
              <defs>
                <linearGradient id="threatsGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="resolvedGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
              <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1e293b', 
                  border: '1px solid #334155', 
                  borderRadius: '8px',
                  color: '#f1f5f9'
                }} 
              />
              <Area 
                type="monotone" 
                dataKey="threats" 
                stroke="#ef4444" 
                fillOpacity={1} 
                fill="url(#threatsGradient)"
                name={t('threats.threats')}
              />
              <Area 
                type="monotone" 
                dataKey="resolved" 
                stroke="#10b981" 
                fillOpacity={1} 
                fill="url(#resolvedGradient)"
                name={t('alerts.resolved')}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Threat Distribution */}
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-700">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">{t('dashboard.threatDistribution')}</h3>
          <ResponsiveContainer width="100%" height={250} aria-label={t('dashboard.threatDistribution')} role="region">
            <PieChart>
              <Pie
                data={severityData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={5}
                dataKey="value"
                nameKey="name"
                aria-label={t('dashboard.threatDistribution')}
              >
                {severityData.map((entry, index) => (
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
          <div className="mt-4 grid grid-cols-2 gap-2">
            {severityData.map((item, index) => (
              <div key={index} className="flex items-center space-x-2">
                <div 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: item.color }}
                  aria-label={item.name}
                ></div>
                <span className="text-sm text-slate-600 dark:text-slate-400">
                  {item.name}: {item.value}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* System Performance */}
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-700">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">{t('dashboard.systemPerformance')}</h3>
          <ResponsiveContainer width="100%" height={250} aria-label={t('dashboard.systemPerformance')} role="region">
            <BarChart data={systemMetrics} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
              <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1e293b', 
                  border: '1px solid #334155', 
                  borderRadius: '8px',
                  color: '#f1f5f9'
                }} 
              />
              <Bar dataKey="value" name={t('dashboard.systemPerformance')}>
                {systemMetrics.map((entry, index) => (
                  <Cell key={`cell-bar-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Alerts */}
      <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-700">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">{t('dashboard.recentAlerts')}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {recentAlerts.map((alert, idx) => (
            <AlertCard key={alert.id || idx} alert={alert} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;