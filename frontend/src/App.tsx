import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Home from './pages/Home';
import AnalysisResult from './pages/AnalysisResult';
import './index.css';

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
      </Routes>
    </BrowserRouter>
  );
}

export default App;
