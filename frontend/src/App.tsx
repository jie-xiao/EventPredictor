import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Home as HomeIcon, AlertCircle } from 'lucide-react';
import Home from './pages/Home';
import AnalysisResult from './pages/AnalysisResult';
import './index.css';

function NotFound() {
  return (
    <div className="min-h-screen bg-background-dark flex items-center justify-center">
      <div className="text-center">
        <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-[#1E293B] flex items-center justify-center">
          <AlertCircle className="w-10 h-10 text-primary-cyan" />
        </div>
        <h1 className="text-6xl font-bold text-text-primary mb-4">404</h1>
        <p className="text-text-secondary mb-6">Page not found</p>
        <a
          href="/"
          className="inline-flex items-center gap-2 px-6 py-3 bg-primary-cyan/20 text-primary-cyan rounded-lg hover:bg-primary-cyan/30 transition-colors"
        >
          <HomeIcon className="w-4 h-4" />
          Back to Home
        </a>
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 主页 - 全屏地球+抽屉系统 */}
        <Route path="/" element={<Home />} />
        <Route path="/analysis" element={<AnalysisResult />} />
        {/* Redirect old routes */}
        <Route path="/dashboard" element={<Navigate to="/" replace />} />
        <Route path="/drawers" element={<Navigate to="/" replace />} />
        {/* 404 - Not Found */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
