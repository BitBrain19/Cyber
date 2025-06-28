import type { Alert, ThreatMetrics, SystemHealth, NetworkNode } from '../types';

const severityOptions: Array<'critical' | 'high' | 'medium' | 'low'> = ['critical', 'high', 'medium', 'low'];
const statusOptions: Array<'active' | 'investigating' | 'resolved'> = ['active', 'investigating', 'resolved'];
const categories = [
  'Malware Detection', 'Anomalous Behavior', 'Network Intrusion', 
  'Data Exfiltration', 'Credential Compromise', 'Insider Threat',
  'Phishing Attempt', 'Brute Force Attack', 'Privilege Escalation'
];

const sources = [
  'Firewall', 'IDS/IPS', 'SIEM', 'Endpoint Protection', 
  'Network Monitor', 'User Behavior Analytics', 'Cloud Security'
];

const threatTypes = [
  'Advanced Persistent Threat', 'Ransomware', 'Data Breach', 'Insider Threat',
  'Phishing', 'DDoS Attack', 'Malware', 'Zero-day Exploit', 'Social Engineering'
];

const assetNames = [
  'WEB-SERVER-01', 'DB-PROD-02', 'AD-CONTROLLER', 'MAIL-SERVER',
  'FILE-SERVER-01', 'BACKUP-SERVER', 'DMZ-FIREWALL', 'CORE-SWITCH',
  'WORKSTATION-HR-01', 'LAPTOP-DEV-05', 'CLOUD-INSTANCE-A1', 'API-GATEWAY'
];

function generateRandomDate(daysBack: number = 7): Date {
  const now = new Date();
  const randomTime = Math.random() * daysBack * 24 * 60 * 60 * 1000;
  return new Date(now.getTime() - randomTime);
}

function generateAlerts(): Alert[] {
  const alerts: Alert[] = [];
  const alertCount = Math.floor(Math.random() * 15) + 10;

  for (let i = 0; i < alertCount; i++) {
    const severity = severityOptions[Math.floor(Math.random() * severityOptions.length)];
    const category = categories[Math.floor(Math.random() * categories.length)];
    
    alerts.push({
      id: `alert-${i + 1}`,
      title: `${category} Detected`,
      description: generateAlertDescription(category, severity),
      severity,
      timestamp: generateRandomDate(1),
      category,
      source: sources[Math.floor(Math.random() * sources.length)],
      threatScore: severity === 'critical' ? 90 + Math.random() * 10 :
                   severity === 'high' ? 70 + Math.random() * 20 :
                   severity === 'medium' ? 40 + Math.random() * 30 :
                   Math.random() * 40,
      status: statusOptions[Math.floor(Math.random() * statusOptions.length)],
      affectedAssets: [
        assetNames[Math.floor(Math.random() * assetNames.length)],
        ...(Math.random() > 0.7 ? [assetNames[Math.floor(Math.random() * assetNames.length)]] : [])
      ]
    });
  }

  return alerts.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
}

function generateAlertDescription(category: string, severity: string): string {
  const descriptions: Record<string, string[]> = {
    'Malware Detection': [
      'Suspicious executable detected on endpoint with behavior analysis indicating potential malware',
      'Multiple files encrypted simultaneously, potential ransomware activity detected',
      'Unknown process attempting to communicate with known malicious C&C server'
    ],
    'Anomalous Behavior': [
      'User accessing unusual number of files outside normal business hours',
      'Abnormal data transfer patterns detected from database server',
      'Service account showing irregular authentication patterns'
    ],
    'Network Intrusion': [
      'Unauthorized access attempt detected on critical network segment',
      'Suspicious network traffic patterns indicating potential lateral movement',
      'Multiple failed authentication attempts from external IP address'
    ],
    'Data Exfiltration': [
      'Large volume of sensitive data accessed and transferred to external location',
      'Unusual database queries extracting customer information detected',
      'Encrypted channel established to suspicious external domain'
    ],
    'Credential Compromise': [
      'Multiple login attempts with compromised credentials detected',
      'Password spray attack targeting multiple user accounts',
      'Service account credentials being used from unexpected locations'
    ]
  };

  const categoryDescriptions = descriptions[category] || descriptions['Anomalous Behavior'];
  return categoryDescriptions[Math.floor(Math.random() * categoryDescriptions.length)];
}

function generateThreatMetrics(): ThreatMetrics {
  const criticalThreats = Math.floor(Math.random() * 5) + 1;
  const highThreats = Math.floor(Math.random() * 12) + 3;
  const mediumThreats = Math.floor(Math.random() * 25) + 10;
  const lowThreats = Math.floor(Math.random() * 40) + 15;
  
  const threatTrend = [];
  for (let i = 6; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    threatTrend.push({
      date: date.toISOString().split('T')[0],
      threats: Math.floor(Math.random() * 50) + 20,
      resolved: Math.floor(Math.random() * 40) + 15
    });
  }

  const topThreatTypes = threatTypes.slice(0, 5).map(type => ({
    name: type,
    count: Math.floor(Math.random() * 20) + 5,
    severity: severityOptions[Math.floor(Math.random() * severityOptions.length)]
  }));

  return {
    totalThreats: criticalThreats + highThreats + mediumThreats + lowThreats,
    criticalThreats,
    highThreats,
    mediumThreats,
    lowThreats,
    threatTrend,
    topThreatTypes,
    averageResponseTime: Math.floor(Math.random() * 120) + 30, // minutes
    mttr: Math.floor(Math.random() * 480) + 120 // minutes
  };
}

function generateSystemHealth(): SystemHealth {
  const components = [
    'Network Firewall', 'Intrusion Detection System', 'SIEM Platform',
    'Endpoint Protection', 'DNS Security', 'Email Security Gateway',
    'Web Application Firewall', 'Data Loss Prevention'
  ].map(name => ({
    name,
    status: Math.random() > 0.1 ? 'healthy' as const : 
            Math.random() > 0.5 ? 'warning' as const : 'critical' as const,
    uptime: Math.random() * 100,
    lastCheck: new Date(Date.now() - Math.random() * 300000) // Last 5 minutes
  }));

  return {
    overallScore: Math.floor(Math.random() * 20) + 80,
    components,
    networkLatency: Math.random() * 50 + 10,
    cpuUsage: Math.random() * 40 + 20,
    memoryUsage: Math.random() * 60 + 30,
    diskUsage: Math.random() * 50 + 25
  };
}

function generateNetworkNodes(): NetworkNode[] {
  const nodeTypes: Array<'server' | 'workstation' | 'router' | 'firewall' | 'database' | 'cloud'> = 
    ['server', 'workstation', 'router', 'firewall', 'database', 'cloud'];
  const riskLevels: Array<'low' | 'medium' | 'high' | 'critical'> = ['low', 'medium', 'high', 'critical'];
  
  const nodes: NetworkNode[] = [];
  const nodeCount = 15;

  for (let i = 0; i < nodeCount; i++) {
    const id = `node-${i + 1}`;
    nodes.push({
      id,
      label: `${nodeTypes[Math.floor(Math.random() * nodeTypes.length)].toUpperCase()}-${i + 1}`,
      type: nodeTypes[Math.floor(Math.random() * nodeTypes.length)],
      riskLevel: riskLevels[Math.floor(Math.random() * riskLevels.length)],
      connections: [],
      position: {
        x: Math.random() * 800 + 100,
        y: Math.random() * 600 + 100
      },
      threats: Math.floor(Math.random() * 5),
      lastActivity: generateRandomDate(0.1)
    });
  }

  // Generate connections
  nodes.forEach(node => {
    const connectionCount = Math.floor(Math.random() * 4) + 1;
    const availableNodes = nodes.filter(n => n.id !== node.id);
    
    for (let i = 0; i < connectionCount && i < availableNodes.length; i++) {
      const targetNode = availableNodes[Math.floor(Math.random() * availableNodes.length)];
      if (!node.connections.includes(targetNode.id)) {
        node.connections.push(targetNode.id);
      }
    }
  });

  return nodes;
}

// Backend API compatible mock data
export const mockBackendData = {
  // Alerts endpoint response
  alerts: {
    alerts: generateAlerts(),
    total: 25,
    filters: {
      severity: null,
      status: null,
      category: null,
      asset_id: null
    }
  },

  // Alerts summary endpoint response
  alertsSummary: {
    severity_distribution: {
      critical: 3,
      high: 8,
      medium: 12,
      low: 22
    },
    status_distribution: {
      active: 15,
      investigating: 8,
      resolved: 22
    },
    trend: [
      { date: '2025-01-20', threats: 45, resolved: 38 },
      { date: '2025-01-21', threats: 52, resolved: 41 },
      { date: '2025-01-22', threats: 38, resolved: 35 },
      { date: '2025-01-23', threats: 61, resolved: 48 },
      { date: '2025-01-24', threats: 43, resolved: 39 },
      { date: '2025-01-25', threats: 49, resolved: 42 },
      { date: '2025-01-26', threats: 35, resolved: 31 }
    ],
    total_active: 45,
    average_response_time: 45,
    mttr: 120
  },

  // Monitor status endpoint response
  monitorStatus: {
    status: "healthy",
    timestamp: new Date().toISOString(),
    components: {
      database: "healthy",
      ml_pipeline: {
        is_initialized: true,
        models: {
          anomaly_detector: true,
          threat_classifier: true,
          log_parser: true,
          graph_analyzer: true
        },
        performance: {
          average_inference_time: 0.05,
          model_accuracy: 0.92,
          false_positive_rate: 0.08
        }
      },
      data_pipeline: {
        is_initialized: true,
        kafka_status: true,
        processor_status: true,
        active_tasks: 3,
        kafka_topics: ["security_events", "security_logs", "threat_intelligence"]
      },
      websocket_connections: 5
    }
  },

  // Monitor metrics endpoint response
  monitorMetrics: {
    metrics: {
      total_events: 1250,
      event_types: {
        login: 450,
        file_access: 320,
        network_scan: 180,
        data_transfer: 300
      },
      severity_distribution: {
        critical: 15,
        high: 45,
        medium: 120,
        low: 1070
      },
      top_assets: {
        "WEB-SERVER-01": 180,
        "DB-PROD-02": 150,
        "AD-CONTROLLER": 120,
        "MAIL-SERVER": 95
      },
      time_series: [
        { timestamp: "2025-01-26T10:00:00Z", events: 45 },
        { timestamp: "2025-01-26T11:00:00Z", events: 52 },
        { timestamp: "2025-01-26T12:00:00Z", events: 38 }
      ]
    },
    time_range: "24h",
    asset_id: null,
    timestamp: new Date().toISOString()
  },

  // System health endpoint response
  systemHealth: {
    overall_score: 85,
    components: [
      {
        name: "Network Firewall",
        status: "healthy",
        uptime: 99.9,
        last_check: new Date().toISOString()
      },
      {
        name: "Intrusion Detection System",
        status: "healthy",
        uptime: 99.8,
        last_check: new Date().toISOString()
      },
      {
        name: "SIEM Platform",
        status: "healthy",
        uptime: 99.7,
        last_check: new Date().toISOString()
      },
      {
        name: "Endpoint Protection",
        status: "warning",
        uptime: 95.2,
        last_check: new Date().toISOString()
      }
    ],
    network_latency: 25.5,
    cpu_usage: 45.2,
    memory_usage: 67.8,
    disk_usage: 34.1
  },

  // Attack paths visualization endpoint response
  attackPaths: {
    nodes: generateNetworkNodes(),
    edges: [
      { from: "node-1", to: "node-2", weight: 1, alert_type: "Network Intrusion" },
      { from: "node-2", to: "node-3", weight: 2, alert_type: "Lateral Movement" },
      { from: "node-3", to: "node-4", weight: 1, alert_type: "Data Exfiltration" },
      { from: "node-1", to: "node-5", weight: 1, alert_type: "Credential Compromise" }
    ],
    metadata: {
      total_nodes: 15,
      total_edges: 4,
      attack_paths: 3,
      risk_level: null,
      time_range: "24h",
      generated_at: new Date().toISOString()
    }
  },

  // ML metrics endpoint response
  mlMetrics: {
    anomaly_detector: {
      accuracy: 0.94,
      precision: 0.92,
      recall: 0.89,
      f1_score: 0.90,
      false_positive_rate: 0.08,
      true_positive_rate: 0.89,
      auc: 0.95,
      last_updated: new Date().toISOString()
    },
    threat_classifier: {
      accuracy: 0.91,
      precision: 0.89,
      recall: 0.87,
      f1_score: 0.88,
      false_positive_rate: 0.12,
      true_positive_rate: 0.87,
      auc: 0.93,
      last_updated: new Date().toISOString()
    },
    log_parser: {
      accuracy: 0.96,
      entity_extraction_f1: 0.94,
      processing_speed: "1000 logs/sec",
      last_updated: new Date().toISOString()
    },
    graph_analyzer: {
      path_detection_accuracy: 0.88,
      lateral_movement_detection: 0.85,
      processing_speed: "1000 edges/sec",
      last_updated: new Date().toISOString()
    },
    explainability: {
      anomaly_detector: {
        feature_importance: {
          bytes_transferred: 0.25,
          login_attempts: 0.30,
          duration: 0.20,
          event_type: 0.15,
          source_ip: 0.10
        },
        shap_values_available: true
      },
      threat_classifier: {
        feature_importance: {
          bytes_transferred: 0.20,
          login_attempts: 0.25,
          duration: 0.15,
          destination_port: 0.20,
          protocol: 0.20
        },
        shap_values_available: true
      }
    }
  },

  // WebSocket real-time data
  websocketData: {
    type: "anomaly_detected",
    event: {
      id: "event-12345",
      timestamp: new Date().toISOString(),
      event_type: "suspicious_activity",
      source_ip: "192.168.1.100",
      bytes_transferred: 5000,
      login_attempts: 10
    },
    analysis: {
      anomaly_detection: {
        anomaly_score: 0.85,
        is_anomaly: true,
        threshold: 0.5
      },
      threat_classification: {
        classification: "suspicious",
        confidence: 0.78,
        probabilities: {
          benign: 0.12,
          suspicious: 0.78,
          malicious: 0.10
        }
      },
      overall_threat_score: 0.82
    },
    timestamp: new Date().toISOString()
  }
};

export function generateMockData() {
  return {
    alerts: generateAlerts(),
    threatMetrics: generateThreatMetrics(),
    systemHealth: generateSystemHealth(),
    networkNodes: generateNetworkNodes()
  };
}