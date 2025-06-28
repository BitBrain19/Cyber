import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import Alerts from './pages/Alerts';
import AttackPaths from './pages/AttackPaths';
import Reports from './pages/Reports';
import Settings from './pages/Settings';
import { ThemeProvider } from './contexts/ThemeContext';
import { DataProvider } from './contexts/DataContext';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <ThemeProvider>
      <DataProvider>
        <Router>
          <a href="#main-content" className="skip-link">Skip to main content</a>
          <div className="min-h-screen bg-slate-50 dark:bg-slate-900 transition-colors duration-200">
            <div className="flex">
              <Sidebar isOpen={sidebarOpen} />
              <div className={`flex-1 transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-16'}`}>
                <Header 
                  onMenuClick={() => setSidebarOpen(!sidebarOpen)} 
                  sidebarOpen={sidebarOpen}
                />
                <main id="main-content" className="p-6" tabIndex={-1} role="main">
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/alerts" element={<Alerts />} />
                    <Route path="/attack-paths" element={<AttackPaths />} />
                    <Route path="/reports" element={<Reports />} />
                    <Route path="/settings" element={<Settings />} />
                  </Routes>
                </main>
              </div>
            </div>
          </div>
        </Router>
      </DataProvider>
    </ThemeProvider>
  );
}

export default App;