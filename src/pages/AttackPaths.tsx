import React, { useState, useRef, useEffect } from 'react';
import { Network, ZoomIn, ZoomOut, RotateCcw, Settings, Filter } from 'lucide-react';
import { useData } from '../contexts/DataContext';
import type { NetworkNode } from '../types';

const AttackPaths: React.FC = () => {
  const { networkNodes } = useData();
  const [selectedNode, setSelectedNode] = useState<NetworkNode | null>(null);
  const [zoom, setZoom] = useState(1);
  const [filter, setFilter] = useState<string>('all');
  const svgRef = useRef<SVGSVGElement>(null);

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'critical': return '#ef4444';
      case 'high': return '#f97316';
      case 'medium': return '#eab308';
      case 'low': return '#10b981';
      default: return '#64748b';
    }
  };

  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'server': return '🖥️';
      case 'workstation': return '💻';
      case 'router': return '📡';
      case 'firewall': return '🛡️';
      case 'database': return '🗄️';
      case 'cloud': return '☁️';
      default: return '🔷';
    }
  };

  const filteredNodes = networkNodes.filter(node => 
    filter === 'all' || node.riskLevel === filter
  );

  const handleZoomIn = () => setZoom(prev => Math.min(prev * 1.2, 3));
  const handleZoomOut = () => setZoom(prev => Math.max(prev / 1.2, 0.3));
  const handleReset = () => setZoom(1);

  return (
    <div className="h-full flex flex-col space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Attack Path Analysis</h1>
          <p className="text-slate-600 dark:text-slate-400 mt-1">Visualize network topology and potential attack vectors</p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1 text-sm rounded-lg transition-colors ${
              filter === 'all' 
                ? 'bg-cyber-500 text-white' 
                : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('critical')}
            className={`px-3 py-1 text-sm rounded-lg transition-colors ${
              filter === 'critical' 
                ? 'bg-red-500 text-white' 
                : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
            }`}
          >
            Critical
          </button>
          <button
            onClick={() => setFilter('high')}
            className={`px-3 py-1 text-sm rounded-lg transition-colors ${
              filter === 'high' 
                ? 'bg-orange-500 text-white' 
                : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
            }`}
          >
            High Risk
          </button>
        </div>
      </div>

      <div className="flex-1 flex space-x-6">
        {/* Network Visualization */}
        <div className="flex-1 bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700">
          <div className="p-4 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Network Topology</h3>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleZoomOut}
                className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                title="Zoom Out"
              >
                <ZoomOut className="w-4 h-4 text-slate-600 dark:text-slate-400" />
              </button>
              <button
                onClick={handleZoomIn}
                className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                title="Zoom In"
              >
                <ZoomIn className="w-4 h-4 text-slate-600 dark:text-slate-400" />
              </button>
              <button
                onClick={handleReset}
                className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                title="Reset View"
              >
                <RotateCcw className="w-4 h-4 text-slate-600 dark:text-slate-400" />
              </button>
            </div>
          </div>
          
          <div className="p-4 h-96 overflow-hidden">
            <svg
              ref={svgRef}
              width="100%"
              height="100%"
              viewBox="0 0 1000 800"
              className="bg-slate-50 dark:bg-slate-900 rounded-lg"
              style={{ transform: `scale(${zoom})`, transformOrigin: 'center' }}
            >
              {/* Grid Background */}
              <defs>
                <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
                  <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#e2e8f0" strokeWidth="1" opacity="0.3"/>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />

              {/* Connections */}
              {filteredNodes.map(node => 
                node.connections.map(connectionId => {
                  const targetNode = networkNodes.find(n => n.id === connectionId);
                  if (!targetNode || !filteredNodes.includes(targetNode)) return null;
                  
                  return (
                    <line
                      key={`${node.id}-${connectionId}`}
                      x1={node.position.x}
                      y1={node.position.y}
                      x2={targetNode.position.x}
                      y2={targetNode.position.y}
                      stroke="#64748b"
                      strokeWidth="2"
                      strokeOpacity="0.6"
                      className="animate-pulse"
                    />
                  );
                })
              )}

              {/* Nodes */}
              {filteredNodes.map(node => (
                <g key={node.id}>
                  {/* Node Circle */}
                  <circle
                    cx={node.position.x}
                    cy={node.position.y}
                    r="25"
                    fill={getRiskColor(node.riskLevel)}
                    stroke="white"
                    strokeWidth="3"
                    className="cursor-pointer hover:r-30 transition-all duration-200 drop-shadow-lg"
                    onClick={() => setSelectedNode(node)}
                    style={{
                      filter: `drop-shadow(0 0 10px ${getRiskColor(node.riskLevel)}40)`
                    }}
                  />
                  
                  {/* Node Icon */}
                  <text
                    x={node.position.x}
                    y={node.position.y + 5}
                    textAnchor="middle"
                    fontSize="16"
                    className="pointer-events-none select-none"
                  >
                    {getNodeIcon(node.type)}
                  </text>
                  
                  {/* Node Label */}
                  <text
                    x={node.position.x}
                    y={node.position.y + 45}
                    textAnchor="middle"
                    fontSize="12"
                    fill="#475569"
                    className="pointer-events-none select-none font-medium"
                  >
                    {node.label}
                  </text>
                  
                  {/* Threat Indicator */}
                  {node.threats > 0 && (
                    <circle
                      cx={node.position.x + 18}
                      cy={node.position.y - 18}
                      r="8"
                      fill="#ef4444"
                      className="animate-pulse"
                    />
                  )}
                  {node.threats > 0 && (
                    <text
                      x={node.position.x + 18}
                      y={node.position.y - 14}
                      textAnchor="middle"
                      fontSize="10"
                      fill="white"
                      className="pointer-events-none select-none font-bold"
                    >
                      {node.threats}
                    </text>
                  )}
                </g>
              ))}
            </svg>
          </div>
        </div>

        {/* Node Details Panel */}
        <div className="w-80 bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700">
          <div className="p-4 border-b border-slate-200 dark:border-slate-700">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Node Details</h3>
          </div>
          
          <div className="p-4">
            {selectedNode ? (
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold text-slate-900 dark:text-white text-lg">
                    {selectedNode.label}
                  </h4>
                  <p className="text-slate-600 dark:text-slate-400 capitalize">
                    {selectedNode.type}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-slate-500 dark:text-slate-400">Risk Level</label>
                    <div 
                      className="mt-1 px-2 py-1 rounded text-sm font-medium inline-block text-white"
                      style={{ backgroundColor: getRiskColor(selectedNode.riskLevel) }}
                    >
                      {selectedNode.riskLevel.toUpperCase()}
                    </div>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-slate-500 dark:text-slate-400">Active Threats</label>
                    <div className="mt-1 text-lg font-bold text-slate-900 dark:text-white">
                      {selectedNode.threats}
                    </div>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-slate-500 dark:text-slate-400">Connections</label>
                  <div className="mt-1 text-slate-900 dark:text-white">
                    {selectedNode.connections.length} nodes
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-slate-500 dark:text-slate-400">Last Activity</label>
                  <div className="mt-1 text-slate-900 dark:text-white">
                    {selectedNode.lastActivity.toLocaleString()}
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
                  <h5 className="font-medium text-slate-900 dark:text-white mb-2">Risk Assessment</h5>
                  <div className="space-y-2">
                    {selectedNode.riskLevel === 'critical' && (
                      <div className="text-sm text-red-600 dark:text-red-400">
                        ⚠️ High vulnerability exposure detected
                      </div>
                    )}
                    {selectedNode.threats > 0 && (
                      <div className="text-sm text-orange-600 dark:text-orange-400">
                        🔍 Active threats require attention
                      </div>
                    )}
                    {selectedNode.connections.length > 5 && (
                      <div className="text-sm text-yellow-600 dark:text-yellow-400">
                        🌐 High connectivity increases attack surface
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex space-x-2">
                  <button className="flex-1 bg-cyber-500 text-white py-2 px-3 rounded-lg hover:bg-cyber-600 transition-colors text-sm">
                    Investigate
                  </button>
                  <button className="flex-1 bg-slate-500 text-white py-2 px-3 rounded-lg hover:bg-slate-600 transition-colors text-sm">
                    Isolate
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <Network className="w-12 h-12 text-slate-400 mx-auto mb-4" />
                <p className="text-slate-600 dark:text-slate-400">
                  Click on a node to view details
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AttackPaths;