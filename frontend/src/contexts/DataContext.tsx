import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { alertsAPI, monitoringAPI, visualizationAPI, wsService, healthAPI } from '../services/api';
import { generateMockData } from '../utils/mockData';
import type { Alert, ThreatMetrics, SystemHealth, NetworkNode } from '../types';

interface DataContextType {
  alerts: Alert[];
  threatMetrics: ThreatMetrics;
  systemHealth: SystemHealth;
  networkNodes: NetworkNode[];
  refreshData: () => Promise<void>;
  isLoading: boolean;
  isConnected: boolean;
  error: string | null;
  connectionState: 'CONNECTING' | 'CONNECTED' | 'DISCONNECTED' | 'ERROR';
  lastUpdated: Date | null;
  retryConnection: () => void;
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
  const [connectionState, setConnectionState] = useState<'CONNECTING' | 'CONNECTED' | 'DISCONNECTED' | 'ERROR'>('DISCONNECTED');
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  // Check if backend is available
  const checkBackendConnection = useCallback(async (): Promise<boolean> => {
    try {
      await healthAPI.checkLiveness();
      return true;
    } catch (error) {
      console.warn('Backend health check failed:', error);
      return false;
    }
  }, []);

  // Load data from backend
  const loadBackendData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Parallel data loading for better performance
      const [alertsData, metricsData, healthData, topologyData] = await Promise.allSettled([
        alertsAPI.getAlerts({ limit: 100 }),
        monitoringAPI.getMetrics(),
        monitoringAPI.getHealth(),
        visualizationAPI.getAttackPaths()
      ]);

      // Process alerts
      if (alertsData.status === 'fulfilled') {
        setAlerts(alertsData.value);
      } else {
        console.error('Failed to load alerts:', alertsData.reason);
      }

      // Process metrics
      if (metricsData.status === 'fulfilled') {
        const metrics = metricsData.value;
        setThreatMetrics({
          totalThreats: metrics.active_threats || 0,
          criticalThreats: metrics.threat_metrics?.critical_threats || 0,
          highThreats: metrics.threat_metrics?.high_threats || 0,
          mediumThreats: metrics.threat_metrics?.medium_threats || 0,
          lowThreats: metrics.threat_metrics?.low_threats || 0,
          threatTrend: metrics.threat_metrics?.threat_trend || [],
          topThreatTypes: metrics.threat_metrics?.top_categories || [],
          averageResponseTime: metrics.threat_metrics?.average_response_time || 0,
          mttr: metrics.threat_metrics?.average_response_time * 2 || 0,
        });
      } else {
        console.error('Failed to load metrics:', metricsData.reason);
      }

      // Process system health
      if (healthData.status === 'fulfilled') {
        const health = healthData.value;
        setSystemHealth({
          overallScore: health.overall_score || 0,
          components: health.components || [],
          networkLatency: health.network_latency || 0,
          cpuUsage: health.cpu_usage || 0,
          memoryUsage: health.memory_usage || 0,
          diskUsage: health.disk_usage || 0,
        });
      } else {
        console.error('Failed to load health data:', healthData.reason);
      }

      // Process network topology
      if (topologyData.status === 'fulfilled') {
        setNetworkNodes(topologyData.value.nodes || []);
      } else {
        console.error('Failed to load topology data:', topologyData.reason);
      }

      setIsConnected(true);
      setConnectionState('CONNECTED');
      setLastUpdated(new Date());
      setRetryCount(0);

    } catch (err) {
      console.error('Failed to load backend data:', err);
      setError('Failed to connect to backend services');
      setIsConnected(false);
      setConnectionState('ERROR');
      
      // Fallback to mock data
      const mockData = generateMockData();
      setAlerts(mockData.alerts);
      setThreatMetrics(mockData.threatMetrics);
      setSystemHealth(mockData.systemHealth);
      setNetworkNodes(mockData.networkNodes);
      setLastUpdated(new Date());
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Setup WebSocket for real-time updates
  const setupWebSocket = useCallback(() => {
    setConnectionState('CONNECTING');
    
    wsService.connect(
      // onMessage
      (data) => {
        console.log('Real-time data received:', data);
        
        try {
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

          setLastUpdated(new Date());
          setError(null);
          
        } catch (error) {
          console.error('Error processing real-time data:', error);
        }
      },
      // onError
      (error) => {
        console.error('WebSocket error:', error);
        setError('Real-time connection lost');
        setConnectionState('ERROR');
      },
      // onConnect
      () => {
        console.log('WebSocket connected successfully');
        setConnectionState('CONNECTED');
        setError(null);
      },
      // onDisconnect
      () => {
        console.log('WebSocket disconnected');
        setConnectionState('DISCONNECTED');
      }
    );
  }, []);

  // Retry connection with exponential backoff
  const retryConnection = useCallback(async () => {
    if (retryCount >= 5) {
      setError('Maximum retry attempts reached. Please refresh the page.');
      return;
    }

    setRetryCount(prev => prev + 1);
    const delay = Math.min(1000 * Math.pow(2, retryCount), 30000);
    
    setTimeout(async () => {
      const backendAvailable = await checkBackendConnection();
      
      if (backendAvailable) {
        await loadBackendData();
        setupWebSocket();
      } else {
        setError('Backend server is not responding');
        setConnectionState('ERROR');
      }
    }, delay);
  }, [retryCount, checkBackendConnection, loadBackendData, setupWebSocket]);

  // Main refresh function
  const refreshData = useCallback(async () => {
    const backendAvailable = await checkBackendConnection();
    
    if (backendAvailable) {
      await loadBackendData();
      setupWebSocket();
    } else {
      console.warn('Backend not available, using mock data');
      setIsConnected(false);
      setError('Backend server not running');
      setConnectionState('ERROR');
      
      // Use mock data as fallback
      const mockData = generateMockData();
      setAlerts(mockData.alerts);
      setThreatMetrics(mockData.threatMetrics);
      setSystemHealth(mockData.systemHealth);
      setNetworkNodes(mockData.networkNodes);
      setLastUpdated(new Date());
    }
  }, [checkBackendConnection, loadBackendData, setupWebSocket]);

  // Initial data load
  useEffect(() => {
    refreshData();

    // Cleanup WebSocket on unmount
    return () => {
      wsService.disconnect();
    };
  }, [refreshData]);

  // Periodic health check and data refresh
  useEffect(() => {
    if (!isConnected) return;

    const interval = setInterval(async () => {
      try {
        // Check if backend is still available
        const isHealthy = await checkBackendConnection();
        
        if (isHealthy) {
          // Refresh data periodically (every 30 seconds)
          await loadBackendData();
        } else {
          setIsConnected(false);
          setError('Backend connection lost');
          setConnectionState('ERROR');
        }
      } catch (error) {
        console.error('Periodic health check failed:', error);
      }
    }, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, [isConnected, checkBackendConnection, loadBackendData]);

  // Auto-retry on connection errors
  useEffect(() => {
    if (connectionState === 'ERROR' && retryCount < 5) {
      const timeout = setTimeout(() => {
        retryConnection();
      }, 5000); // Retry after 5 seconds

      return () => clearTimeout(timeout);
    }
  }, [connectionState, retryCount, retryConnection]);

  // Monitor WebSocket connection state
  useEffect(() => {
    const interval = setInterval(() => {
      const wsState = wsService.getConnectionState();
      if (wsState !== connectionState) {
        setConnectionState(wsState as any);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [connectionState]);

  const contextValue: DataContextType = {
    alerts,
    threatMetrics,
    systemHealth,
    networkNodes,
    refreshData,
    isLoading,
    isConnected,
    error,
    connectionState,
    lastUpdated,
    retryConnection,
  };

  return (
    <DataContext.Provider value={contextValue}>
      {children}
    </DataContext.Provider>
  );
};