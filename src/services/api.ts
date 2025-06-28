import axios from 'axios';
import type { Alert, ThreatMetrics, SystemHealth, NetworkNode } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Authentication API
export const authAPI = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
    localStorage.removeItem('auth_token');
  },

  refreshToken: async (): Promise<AuthResponse> => {
    const refreshToken = localStorage.getItem('refresh_token');
    const response = await api.post('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  },
};

// Monitoring API
export const monitoringAPI = {
  getStatus: async () => {
    const response = await api.get('/monitor/status');
    return response.data;
  },

  getMetrics: async () => {
    const response = await api.get('/monitor/metrics');
    return response.data;
  },

  getEvents: async (limit = 100, eventType?: string) => {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    if (eventType) params.append('event_type', eventType);
    
    const response = await api.get(`/monitor/events?${params}`);
    return response.data;
  },

  createEvent: async (eventData: any) => {
    const response = await api.post('/monitor/events', eventData);
    return response.data;
  },

  getAssets: async () => {
    const response = await api.get('/monitor/assets');
    return response.data;
  },

  getHealth: async () => {
    const response = await api.get('/monitor/health');
    return response.data;
  },
};

// Alerts API
export const alertsAPI = {
  getAlerts: async (limit = 100, severity?: string, status?: string): Promise<Alert[]> => {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    if (severity) params.append('severity', severity);
    if (status) params.append('status', status);

    const response = await api.get(`/alerts?${params}`);
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

  updateAlertStatus: async (alertId: string, status: string) => {
    const response = await api.put(`/alerts/${alertId}/status`, { status });
    return response.data;
  },

  getAlertsSummary: async () => {
    const response = await api.get('/alerts/summary');
    return response.data;
  },

  getAlertDetails: async (alertId: string) => {
    const response = await api.get(`/alerts/${alertId}`);
    return response.data;
  },

  executeRemediation: async (alertId: string, action: string) => {
    const response = await api.post(`/alerts/${alertId}/remediate`, { action });
    return response.data;
  },
};

// Visualization API
export const visualizationAPI = {
  getAttackPaths: async (riskLevel?: string): Promise<{ nodes: NetworkNode[]; edges: any[]; metadata: any }> => {
    const params = new URLSearchParams();
    if (riskLevel) params.append('risk_level', riskLevel);

    const response = await api.get(`/visualize/attack-paths?${params}`);
    return {
      ...response.data,
      nodes: response.data.nodes.map((node: any) => ({
        ...node,
        lastActivity: new Date(node.last_activity),
      })),
    };
  },

  getNetworkTopology: async () => {
    const response = await api.get('/visualize/network-topology');
    return response.data;
  },

  getThreatMap: async (timeRange = '24h') => {
    const response = await api.get(`/visualize/threat-map?time_range=${timeRange}`);
    return response.data;
  },

  getUserBehavior: async (userId?: string) => {
    const params = new URLSearchParams();
    if (userId) params.append('user_id', userId);

    const response = await api.get(`/visualize/user-behavior?${params}`);
    return response.data;
  },

  getDataFlow: async () => {
    const response = await api.get('/visualize/data-flow');
    return response.data;
  },
};

// Reports API
export const reportsAPI = {
  generateReport: async (reportData: any) => {
    const response = await api.post('/reports/generate', reportData);
    return response.data;
  },

  downloadReport: async (reportId: string) => {
    const response = await api.get(`/reports/${reportId}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  getTemplates: async () => {
    const response = await api.get('/reports/templates');
    return response.data;
  },
};

// Metrics API
export const metricsAPI = {
  getModelMetrics: async () => {
    const response = await api.get('/metrics/models');
    return response.data;
  },

  getSystemMetrics: async () => {
    const response = await api.get('/metrics/system');
    return response.data;
  },

  getPerformanceMetrics: async () => {
    const response = await api.get('/metrics/performance');
    return response.data;
  },
};

// Admin API
export const adminAPI = {
  trainModels: async () => {
    const response = await api.post('/admin/train');
    return response.data;
  },

  getUsers: async () => {
    const response = await api.get('/admin/users');
    return response.data;
  },

  createUser: async (userData: any) => {
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
};

// WebSocket connection for real-time data
export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  connect(onMessage: (data: any) => void, onError?: (error: Event) => void) {
    const token = localStorage.getItem('auth_token');
    const wsUrl = `ws://localhost:8000/api/monitor${token ? `?token=${token}` : ''}`;

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.reconnect(onMessage, onError);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (onError) onError(error);
    };
  }

  private reconnect(onMessage: (data: any) => void, onError?: (error: Event) => void) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.connect(onMessage, onError);
      }, this.reconnectDelay * this.reconnectAttempts);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }
}

export const wsService = new WebSocketService();

// Health check
export const healthAPI = {
  check: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;