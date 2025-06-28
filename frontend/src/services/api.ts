import axios from 'axios';
import type { Alert, ThreatMetrics, SystemHealth, NetworkNode } from '../types';

// Configuration based on environment
const API_BASE_URL = import.meta.env.PROD 
  ? 'https://api.cyberguard.com.np/api'
  : 'http://localhost:8000/api';

const WS_BASE_URL = import.meta.env.PROD
  ? 'wss://api.cyberguard.com.np/api'
  : 'ws://localhost:8000/api';

// Create axios instance with enhanced configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: true,
});

// Request interceptor for authentication and security
api.interceptors.request.use(
  (config) => {
    // Add auth token
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add CSRF token for state-changing operations
    if (['post', 'put', 'delete', 'patch'].includes(config.method?.toLowerCase() || '')) {
      const csrfToken = localStorage.getItem('csrf_token');
      if (csrfToken) {
        config.headers['X-CSRF-Token'] = csrfToken;
      }
    }

    // Add request ID for tracing
    config.headers['X-Request-ID'] = generateRequestId();

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and token refresh
api.interceptors.response.use(
  (response) => {
    // Update CSRF token if provided
    const csrfToken = response.headers['x-csrf-token'];
    if (csrfToken) {
      localStorage.setItem('csrf_token', csrfToken);
    }

    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Handle authentication errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Attempt token refresh
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await authAPI.refreshToken();
          localStorage.setItem('auth_token', response.access_token);
          localStorage.setItem('refresh_token', response.refresh_token);
          
          // Retry original request
          originalRequest.headers.Authorization = `Bearer ${response.access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('auth_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }

    // Handle rate limiting
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after'];
      if (retryAfter) {
        // Wait and retry
        await new Promise(resolve => setTimeout(resolve, parseInt(retryAfter) * 1000));
        return api(originalRequest);
      }
    }

    // Log errors for monitoring
    console.error('API Error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      message: error.message,
      requestId: error.config?.headers['X-Request-ID']
    });

    return Promise.reject(error);
  }
);

// Utility functions
function generateRequestId(): string {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function validateResponse<T>(data: any): T {
  // Add response validation logic here
  return data as T;
}

// Enhanced API interfaces
export interface LoginCredentials {
  username: string;
  password: string;
  totp_code?: string; // For 2FA
  remember_me?: boolean;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: number;
    username: string;
    email: string;
    role: string;
    is_2fa_enabled: boolean;
  };
}

// Authentication API with enhanced security
export const authAPI = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await api.post('/auth/login', credentials);
    const data = validateResponse<AuthResponse>(response.data);
    
    // Store tokens securely
    localStorage.setItem('auth_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    
    return data;
  },

  logout: async (): Promise<void> => {
    try {
      await api.post('/auth/logout');
    } finally {
      // Always clear local storage
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('csrf_token');
    }
  },

  refreshToken: async (): Promise<AuthResponse> => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await api.post('/auth/refresh', { 
      refresh_token: refreshToken 
    });
    return validateResponse<AuthResponse>(response.data);
  },

  enable2FA: async (): Promise<{ secret: string; qr_code: string }> => {
    const response = await api.post('/auth/2fa/enable');
    return response.data;
  },

  verify2FA: async (code: string): Promise<{ success: boolean }> => {
    const response = await api.post('/auth/2fa/verify', { code });
    return response.data;
  },

  disable2FA: async (code: string): Promise<{ success: boolean }> => {
    const response = await api.post('/auth/2fa/disable', { code });
    return response.data;
  },
};

// Enhanced monitoring API
export const monitoringAPI = {
  getStatus: async () => {
    const response = await api.get('/monitor/status');
    return response.data;
  },

  getMetrics: async () => {
    const response = await api.get('/monitor/metrics');
    return response.data;
  },

  getEvents: async (params: {
    limit?: number;
    event_type?: string;
    start_time?: string;
    end_time?: string;
    severity?: string;
  } = {}) => {
    const response = await api.get('/monitor/events', { params });
    return response.data;
  },

  createEvent: async (eventData: any) => {
    const response = await api.post('/monitor/events', eventData);
    return response.data;
  },

  getAssets: async (params: {
    asset_type?: string;
    criticality?: string;
    status?: string;
  } = {}) => {
    const response = await api.get('/monitor/assets', { params });
    return response.data;
  },

  getHealth: async () => {
    const response = await api.get('/monitor/health');
    return response.data;
  },

  getThreatIntelligence: async (params: {
    indicator_type?: string;
    threat_type?: string;
    limit?: number;
  } = {}) => {
    const response = await api.get('/monitor/threat-intelligence', { params });
    return response.data;
  },
};

// Enhanced alerts API with better error handling
export const alertsAPI = {
  getAlerts: async (params: {
    limit?: number;
    severity?: string;
    status?: string;
    category?: string;
    start_date?: string;
    end_date?: string;
  } = {}): Promise<Alert[]> => {
    const response = await api.get('/alerts', { params });
    return response.data.map((alert: any) => ({
      ...alert,
      timestamp: new Date(alert.timestamp),
    }));
  },

  createAlert: async (alertData: any): Promise<Alert> => {
    const response = await api.post('/alerts', alertData);
    return {
      ...response.data,
      timestamp: new Date(response.data.timestamp),
    };
  },

  updateAlertStatus: async (alertId: string, status: string, comment?: string) => {
    const response = await api.put(`/alerts/${alertId}/status`, { 
      status, 
      comment 
    });
    return response.data;
  },

  assignAlert: async (alertId: string, userId: number) => {
    const response = await api.put(`/alerts/${alertId}/assign`, { user_id: userId });
    return response.data;
  },

  getAlertsSummary: async (timeRange: string = '24h') => {
    const response = await api.get('/alerts/summary', { 
      params: { time_range: timeRange } 
    });
    return response.data;
  },

  getAlertDetails: async (alertId: string) => {
    const response = await api.get(`/alerts/${alertId}`);
    return response.data;
  },

  executeRemediation: async (alertId: string, action: string, parameters?: any) => {
    const response = await api.post(`/alerts/${alertId}/remediate`, { 
      action, 
      parameters 
    });
    return response.data;
  },

  bulkUpdateAlerts: async (alertIds: string[], updates: any) => {
    const response = await api.put('/alerts/bulk', { 
      alert_ids: alertIds, 
      updates 
    });
    return response.data;
  },
};

// Enhanced visualization API
export const visualizationAPI = {
  getAttackPaths: async (params: {
    risk_level?: string;
    time_range?: string;
    asset_type?: string;
  } = {}): Promise<{ nodes: NetworkNode[]; edges: any[]; metadata: any }> => {
    const response = await api.get('/visualize/attack-paths', { params });
    return {
      ...response.data,
      nodes: response.data.nodes.map((node: any) => ({
        ...node,
        lastActivity: new Date(node.last_activity),
      })),
    };
  },

  getNetworkTopology: async (params: {
    depth?: number;
    include_offline?: boolean;
  } = {}) => {
    const response = await api.get('/visualize/network-topology', { params });
    return response.data;
  },

  getThreatMap: async (params: {
    time_range?: string;
    threat_type?: string;
    severity?: string;
  } = {}) => {
    const response = await api.get('/visualize/threat-map', { params });
    return response.data;
  },

  getUserBehavior: async (params: {
    user_id?: string;
    time_range?: string;
    anomaly_threshold?: number;
  } = {}) => {
    const response = await api.get('/visualize/user-behavior', { params });
    return response.data;
  },

  getDataFlow: async (params: {
    time_range?: string;
    source?: string;
    destination?: string;
  } = {}) => {
    const response = await api.get('/visualize/data-flow', { params });
    return response.data;
  },

  getComplianceStatus: async (standard?: string) => {
    const params = standard ? { standard } : {};
    const response = await api.get('/visualize/compliance', { params });
    return response.data;
  },
};

// Enhanced reports API
export const reportsAPI = {
  generateReport: async (reportData: {
    type: string;
    format: string;
    start_date: string;
    end_date: string;
    filters?: any;
    template_id?: string;
  }) => {
    const response = await api.post('/reports/generate', reportData);
    return response.data;
  },

  downloadReport: async (reportId: string) => {
    const response = await api.get(`/reports/${reportId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  getReportStatus: async (reportId: string) => {
    const response = await api.get(`/reports/${reportId}/status`);
    return response.data;
  },

  getReports: async (params: {
    limit?: number;
    status?: string;
    type?: string;
  } = {}) => {
    const response = await api.get('/reports', { params });
    return response.data;
  },

  getTemplates: async () => {
    const response = await api.get('/reports/templates');
    return response.data;
  },

  scheduleReport: async (scheduleData: {
    template_id: string;
    schedule: string;
    recipients: string[];
    parameters?: any;
  }) => {
    const response = await api.post('/reports/schedule', scheduleData);
    return response.data;
  },
};

// Enhanced metrics API
export const metricsAPI = {
  getModelMetrics: async (timeRange: string = '24h') => {
    const response = await api.get('/metrics/models', { 
      params: { time_range: timeRange } 
    });
    return response.data;
  },

  getSystemMetrics: async (timeRange: string = '1h') => {
    const response = await api.get('/metrics/system', { 
      params: { time_range: timeRange } 
    });
    return response.data;
  },

  getPerformanceMetrics: async (timeRange: string = '24h') => {
    const response = await api.get('/metrics/performance', { 
      params: { time_range: timeRange } 
    });
    return response.data;
  },

  getSecurityMetrics: async (timeRange: string = '24h') => {
    const response = await api.get('/metrics/security', { 
      params: { time_range: timeRange } 
    });
    return response.data;
  },

  getComplianceMetrics: async (standard?: string) => {
    const params = standard ? { standard } : {};
    const response = await api.get('/metrics/compliance', { params });
    return response.data;
  },
};

// Enhanced admin API
export const adminAPI = {
  trainModels: async (modelType?: string) => {
    const params = modelType ? { model_type: modelType } : {};
    const response = await api.post('/admin/train', params);
    return response.data;
  },

  getUsers: async (params: {
    limit?: number;
    role?: string;
    status?: string;
  } = {}) => {
    const response = await api.get('/admin/users', { params });
    return response.data;
  },

  createUser: async (userData: {
    username: string;
    email: string;
    password: string;
    role: string;
    is_active?: boolean;
  }) => {
    const response = await api.post('/admin/users', userData);
    return response.data;
  },

  updateUser: async (userId: string, userData: any) => {
    const response = await api.put(`/admin/users/${userId}`, userData);
    return response.data;
  },

  deleteUser: async (userId: string) => {
    const response = await api.delete(`/admin/users/${userId}`);
    return response.data;
  },

  getSystemConfig: async () => {
    const response = await api.get('/admin/config');
    return response.data;
  },

  updateSystemConfig: async (config: any) => {
    const response = await api.put('/admin/config', config);
    return response.data;
  },

  getAuditLogs: async (params: {
    limit?: number;
    user_id?: number;
    action?: string;
    start_date?: string;
    end_date?: string;
  } = {}) => {
    const response = await api.get('/admin/audit-logs', { params });
    return response.data;
  },

  backupDatabase: async () => {
    const response = await api.post('/admin/backup');
    return response.data;
  },

  restoreDatabase: async (backupId: string) => {
    const response = await api.post(`/admin/restore/${backupId}`);
    return response.data;
  },
};

// Enhanced WebSocket service with reconnection and error handling
export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 1000;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private isConnecting = false;

  connect(
    onMessage: (data: any) => void, 
    onError?: (error: Event) => void,
    onConnect?: () => void,
    onDisconnect?: () => void
  ) {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return;
    }

    this.isConnecting = true;
    const token = localStorage.getItem('auth_token');
    const wsUrl = `${WS_BASE_URL}/monitor${token ? `?token=${token}` : ''}`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.startHeartbeat();
        if (onConnect) onConnect();
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onclose = (event) => {
        console.log('WebSocket disconnected', event.code, event.reason);
        this.isConnecting = false;
        this.stopHeartbeat();
        if (onDisconnect) onDisconnect();
        
        // Attempt reconnection if not a normal closure
        if (event.code !== 1000) {
          this.reconnect(onMessage, onError, onConnect, onDisconnect);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.isConnecting = false;
        if (onError) onError(error);
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.isConnecting = false;
      if (onError) onError(error as Event);
    }
  }

  private startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000); // Send ping every 30 seconds
  }

  private stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private reconnect(
    onMessage: (data: any) => void, 
    onError?: (error: Event) => void,
    onConnect?: () => void,
    onDisconnect?: () => void
  ) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), 30000);
      
      setTimeout(() => {
        console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.connect(onMessage, onError, onConnect, onDisconnect);
      }, delay);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  disconnect() {
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    this.reconnectAttempts = 0;
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  getConnectionState(): string {
    if (!this.ws) return 'DISCONNECTED';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'CONNECTING';
      case WebSocket.OPEN: return 'CONNECTED';
      case WebSocket.CLOSING: return 'CLOSING';
      case WebSocket.CLOSED: return 'DISCONNECTED';
      default: return 'UNKNOWN';
    }
  }
}

export const wsService = new WebSocketService();

// Health check API
export const healthAPI = {
  check: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  checkLiveness: async () => {
    const response = await api.get('/health/live');
    return response.data;
  },

  checkReadiness: async () => {
    const response = await api.get('/health/ready');
    return response.data;
  },
};

// Export the configured axios instance
export default api;