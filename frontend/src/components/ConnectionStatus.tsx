import React from 'react';
import { Wifi, WifiOff, AlertCircle, RefreshCw, Clock, CheckCircle } from 'lucide-react';
import { useData } from '../contexts/DataContext';

const ConnectionStatus: React.FC = () => {
  const { 
    isConnected, 
    error, 
    refreshData, 
    isLoading, 
    connectionState, 
    lastUpdated,
    retryConnection 
  } = useData();

  const getStatusIcon = () => {
    switch (connectionState) {
      case 'CONNECTED':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'CONNECTING':
        return <RefreshCw className="w-4 h-4 text-yellow-500 animate-spin" />;
      case 'ERROR':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'DISCONNECTED':
      default:
        return <WifiOff className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusText = () => {
    switch (connectionState) {
      case 'CONNECTED':
        return 'Connected';
      case 'CONNECTING':
        return 'Connecting...';
      case 'ERROR':
        return 'Connection Error';
      case 'DISCONNECTED':
      default:
        return 'Disconnected';
    }
  };

  const getStatusColor = () => {
    switch (connectionState) {
      case 'CONNECTED':
        return 'text-green-600 dark:text-green-400';
      case 'CONNECTING':
        return 'text-yellow-600 dark:text-yellow-400';
      case 'ERROR':
        return 'text-red-600 dark:text-red-400';
      case 'DISCONNECTED':
      default:
        return 'text-gray-600 dark:text-gray-400';
    }
  };

  const formatLastUpdated = () => {
    if (!lastUpdated) return 'Never';
    
    const now = new Date();
    const diff = now.getTime() - lastUpdated.getTime();
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);

    if (seconds < 60) return `${seconds}s ago`;
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return lastUpdated.toLocaleDateString();
  };

  return (
    <div className="flex items-center space-x-3">
      {/* Connection Status */}
      <div className="flex items-center space-x-2">
        {getStatusIcon()}
        <span className={`text-sm font-medium ${getStatusColor()}`}>
          {getStatusText()}
        </span>
      </div>

      {/* Last Updated */}
      {lastUpdated && (
        <div className="flex items-center space-x-1 text-xs text-slate-500 dark:text-slate-400">
          <Clock className="w-3 h-3" />
          <span>{formatLastUpdated()}</span>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="flex items-center space-x-1 text-xs text-red-600 dark:text-red-400 max-w-xs truncate">
          <span title={error}>{error}</span>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex items-center space-x-1">
        {/* Refresh Button */}
        <button
          onClick={refreshData}
          disabled={isLoading || connectionState === 'CONNECTING'}
          className="p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          title="Refresh Data"
        >
          <RefreshCw className={`w-4 h-4 text-slate-600 dark:text-slate-400 ${
            isLoading ? 'animate-spin' : ''
          }`} />
        </button>

        {/* Retry Button (only show on error) */}
        {connectionState === 'ERROR' && (
          <button
            onClick={retryConnection}
            disabled={isLoading}
            className="p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title="Retry Connection"
          >
            <Wifi className="w-4 h-4 text-slate-600 dark:text-slate-400" />
          </button>
        )}
      </div>

      {/* Connection Quality Indicator */}
      <div className="flex items-center space-x-1">
        <div className="flex space-x-1">
          {[1, 2, 3].map((bar) => (
            <div
              key={bar}
              className={`w-1 h-3 rounded-full ${
                connectionState === 'CONNECTED' 
                  ? 'bg-green-500' 
                  : connectionState === 'CONNECTING'
                  ? 'bg-yellow-500'
                  : 'bg-gray-300 dark:bg-gray-600'
              }`}
              style={{
                opacity: connectionState === 'CONNECTED' ? 1 : bar === 1 ? 0.6 : 0.3
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default ConnectionStatus;