import React, { createContext, useContext, useState, useEffect } from 'react';
import { alertsAPI, monitoringAPI, visualizationAPI, wsService } from '../services/api';
import { generateMockData } from '../utils/mockData';
import type { Alert, ThreatMetrics, SystemHealth, NetworkNode } from '../types';

interface DataContextType {
  alerts: Alert[];
  threatMetrics: ThreatMetrics;
  systemHealth: SystemHealth;
  networkNodes: NetworkNode[];
  refreshData: () => void;
  isLoading: boolean;
  isConnected: boolean;
  error: string | null;
}

const DataContext = createContext<DataContextType | undefined>(undefined);

export const useData = () => {
  const context = useContext(DataContext);
  if (context === undefined) {
    throw new Error('useData must be used within a DataProvider');
  }
  return context;
};

export const DataProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [threatMetrics, setThreatMetrics] = useState<ThreatMetrics>({} as ThreatMetrics);
  const [systemHealth, setSystemHealth] = useState<SystemHealth>({} as SystemHealth);
  const [networkNodes, setNetworkNodes] = useState<NetworkNode[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Check if backend is available
  const checkBackendConnection = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/health');
      return response.ok;
    } catch {
      return false;
    }
  };

  // Load data from backend
  const loadBackendData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Load alerts
      const alertsData = await alertsAPI.getAlerts(100);
      setAlerts(alertsData);

      // Load metrics
      const metricsData = await monitoringAPI.getMetrics();
      setThreatMetrics({
        totalThreats: metricsData.active_threats || 0,
        criticalThreats: metricsData.threat_metrics?.critical_threats || 0,
        highThreats: metricsData.threat_metrics?.high_threats || 0,
        mediumThreats: metricsData.threat_metrics?.medium_threats || 0,
        lowThreats: metricsData.threat_metrics?.low_threats || 0,
        threatTrend: metricsData.threat_metrics?.threat_trend || [],
        topThreatTypes: metricsData.threat_metrics?.top_categories || [],
        averageResponseTime: metricsData.threat_metrics?.average_response_time || 0,
        mttr: metricsData.threat_metrics?.average_response_time * 2 || 0,
      });

      // Load system health
      const healthData = await monitoringAPI.getHealth();
      setSystemHealth({
        overallScore: healthData.overall_score || 0,
        components: healthData.components || [],
        networkLatency: healthData.network_latency || 0,
        cpuUsage: healthData.cpu_usage || 0,
        memoryUsage: healthData.memory_usage || 0,
        diskUsage: healthData.disk_usage || 0,
      });

      // Load network topology
      const topologyData = await visualizationAPI.getAttackPaths();
      setNetworkNodes(topologyData.nodes || []);

      setIsConnected(true);
    } catch (err) {
      console.error('Failed to load backend data:', err);
      setError('Failed to connect to backend');
      setIsConnected(false);
      
      // Fallback to mock data
      const mockData = generateMockData();
      setAlerts(mockData.alerts);
      setThreatMetrics(mockData.threatMetrics);
      setSystemHealth(mockData.systemHealth);
      setNetworkNodes(mockData.networkNodes);
    } finally {
      setIsLoading(false);
    }
  };

  // Setup WebSocket for real-time updates
  const setupWebSocket = () => {
    wsService.connect(
      (data) => {
        console.log('Real-time data received:', data);
        
        // Update metrics if received
        if (data.threat_metrics) {
          setThreatMetrics(prev => ({
            ...prev,
            ...data.threat_metrics,
          }));
        }

        // Update system health if received
        if (data.system_health) {
          setSystemHealth(prev => ({
            ...prev,
            ...data.system_health,
          }));
        }

        // Update alerts if received
        if (data.recent_alerts) {
          setAlerts(data.recent_alerts.map((alert: any) => ({
            ...alert,
            timestamp: new Date(alert.timestamp),
          })));
        }
      },
      (error) => {
        console.error('WebSocket error:', error);
        setError('Real-time connection lost');
      }
    );
  };

  const refreshData = async () => {
    const backendAvailable = await checkBackendConnection();
    
    if (backendAvailable) {
      await loadBackendData();
      setupWebSocket();
    } else {
      console.warn('Backend not available, using mock data');
      setIsConnected(false);
      setError('Backend server not running');
      
      // Use mock data as fallback
      const mockData = generateMockData();
      setAlerts(mockData.alerts);
      setThreatMetrics(mockData.threatMetrics);
      setSystemHealth(mockData.systemHealth);
      setNetworkNodes(mockData.networkNodes);
    }
  };

  // Initial data load
  useEffect(() => {
    refreshData();

    // Cleanup WebSocket on unmount
    return () => {
      wsService.disconnect();
    };
  }, []);

  // Periodic refresh for non-WebSocket data
  useEffect(() => {
    if (!isConnected) return;

    const interval = setInterval(() => {
      loadBackendData();
    }, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, [isConnected]);

  return (
    <DataContext.Provider value={{
      alerts,
      threatMetrics,
      systemHealth,
      networkNodes,
      refreshData,
      isLoading,
      isConnected,
      error
    }}>
      {children}
    </DataContext.Provider>
  );
};