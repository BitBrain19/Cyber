export interface Alert {
  id: string;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  timestamp: Date;
  category: string;
  source: string;
  threatScore: number;
  status: 'active' | 'investigating' | 'resolved';
  affectedAssets: string[];
}

export interface ThreatMetrics {
  totalThreats: number;
  criticalThreats: number;
  highThreats: number;
  mediumThreats: number;
  lowThreats: number;
  threatTrend: Array<{ date: string; threats: number; resolved: number }>;
  topThreatTypes: Array<{ name: string; count: number; severity: string }>;
  averageResponseTime: number;
  mttr: number; // Mean Time To Resolution
}

export interface SystemHealth {
  overallScore: number;
  components: Array<{
    name: string;
    status: 'healthy' | 'warning' | 'critical';
    uptime: number;
    lastCheck: Date;
  }>;
  networkLatency: number;
  cpuUsage: number;
  memoryUsage: number;
  diskUsage: number;
}

export interface NetworkNode {
  id: string;
  label: string;
  type: 'server' | 'workstation' | 'router' | 'firewall' | 'database' | 'cloud';
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  connections: string[];
  position: { x: number; y: number };
  threats: number;
  lastActivity: Date;
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  lastLogin: Date;
  riskScore: number;
  activities: Array<{
    timestamp: Date;
    action: string;
    resource: string;
    riskLevel: string;
  }>;
}