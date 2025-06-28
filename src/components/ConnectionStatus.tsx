import React from 'react';
import { Wifi, WifiOff, AlertCircle, RefreshCw } from 'lucide-react';
import { useData } from '../contexts/DataContext';

const ConnectionStatus: React.FC = () => {
  const { isConnected, error, refreshData, isLoading } = useData();

  if (isConnected && !error) {
    return (
      <div className="flex items-center space-x-2 text-green-600 dark:text-green-400">
        <Wifi className="w-4 h-4" />
        <span className="text-sm font-medium">Connected</span>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-2">
      {error ? (
        <>
          <AlertCircle className="w-4 h-4 text-red-500" />
          <span className="text-sm text-red-600 dark:text-red-400">
            {error}
          </span>
        </>
      ) : (
        <>
          <WifiOff className="w-4 h-4 text-yellow-500" />
          <span className="text-sm text-yellow-600 dark:text-yellow-400">
            Disconnected
          </span>
        </>
      )}
      
      <button
        onClick={refreshData}
        disabled={isLoading}
        className="p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors disabled:opacity-50"
        title="Retry Connection"
      >
        <RefreshCw className={`w-4 h-4 text-slate-600 dark:text-slate-400 ${isLoading ? 'animate-spin' : ''}`} />
      </button>
    </div>
  );
};

export default ConnectionStatus;