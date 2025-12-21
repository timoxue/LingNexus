import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { PluginList } from './pages/PluginList';
import { PluginDetailPage } from './pages/PluginDetail';

export const App: React.FC = () => {
  return (
    <Router>
      <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
        <Routes>
          <Route path="/" element={<PluginList />} />
          <Route path="/plugin/:pluginId" element={<PluginDetailPage />} />
        </Routes>
      </div>
    </Router>
  );
};
