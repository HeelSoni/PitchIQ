import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import AIChat from './components/AIChat';
import HomePage from './pages/HomePage';
import StartupProfilePage from './pages/StartupProfilePage';
import SharksPage from './pages/SharksPage';
import FinancialDashboardPage from './pages/FinancialDashboardPage';
import DealBreakdownPage from './pages/DealBreakdownPage';
import ComparePage from './pages/ComparePage';
import LeaderboardPage from './pages/LeaderboardPage';
import DatasetDownloadPage from './pages/DatasetDownloadPage';
import GlossaryPage from './pages/GlossaryPage';

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-background text-text-primary flex flex-col justify-between font-sans">
        <div className="flex-1">
          <Navbar />
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/startup/:slug" element={<StartupProfilePage />} />
            <Route path="/sharks" element={<SharksPage />} />
            <Route path="/dashboard" element={<FinancialDashboardPage />} />
            <Route path="/compare" element={<ComparePage />} />
            <Route path="/leaderboard" element={<LeaderboardPage />} />
            <Route path="/download" element={<DatasetDownloadPage />} />
            <Route path="/glossary" element={<GlossaryPage />} />
            {/* Direct match standard compatibility */}
            <Route path="/deals" element={<DealBreakdownPage />} />
            {/* Fallback to home */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
        
        {/* Floating elements */}
        <AIChat />

        {/* Footer */}
        <footer className="border-t border-border py-6 bg-black/40 mt-12 text-center text-xs text-text-secondary">
          <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row justify-between items-center gap-4">
            <span className="font-Outfit font-bold text-indigo-400 text-sm">PitchIQ</span>
            <span>© 2026 PitchIQ • Shark Tank India Analytics Platform. Sourced from real pitch datasets.</span>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}
