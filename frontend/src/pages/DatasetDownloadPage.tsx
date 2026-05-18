import React, { useState, useEffect } from 'react';
import { usePitchStore } from '../store/usePitchStore';
import { Download, Table, Sparkles, FileSpreadsheet } from 'lucide-react';
import { API_BASE } from '../config';

export default function DatasetDownloadPage() {
  const { industries, sharks, fetchIndustries, fetchSharks } = usePitchStore();
  const [season, setSeason] = useState('');
  const [industry, setIndustry] = useState('');
  const [dealStatus, setDealStatus] = useState('');
  const [sharkId, setSharkId] = useState('');

  useEffect(() => {
    fetchIndustries();
    fetchSharks();
  }, []);

  const handleDownload = () => {
    const params = new URLSearchParams();
    if (season) params.append('season', season);
    if (industry) params.append('industry', industry);
    if (dealStatus) params.append('deal_status', dealStatus);
    if (sharkId) params.append('shark_id', sharkId);

    window.open(`${API_BASE}/download/csv?${params.toString()}`);
  };

  const columns = [
    'startup_name', 'industry', 'season', 'episode',
    'ask_amount_lakhs', 'ask_equity_percent', 'ask_valuation_lakhs',
    'final_amount_lakhs', 'final_equity_percent', 'final_valuation_lakhs',
    'deal_status', 'sharks_invested', 'revenue_lakhs',
    'profit_lakhs', 'ebitda_margin_percent', 'gross_margin_percent',
    'net_margin_percent', 'burn_rate_lakhs', 'runway_months', 'health_score'
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      <div className="space-y-4 max-w-3xl">
        <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight font-Outfit">
          Dataset{' '}
          <span className="bg-gradient-to-r from-cyan-400 to-cyan-300 bg-clip-text text-transparent">
            Download Hub
          </span>
        </h1>
        <p className="text-text-secondary text-sm sm:text-base">
          Download the fully clean, filtered Shark Tank India Seasons 1-5 dataset as a CSV. Zero logins, zero signups, completely free. Perfect for students, data analysts, and research projects.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Side: Filter and Download */}
        <div className="lg:col-span-7 glass p-8 rounded-3xl border border-white/5 space-y-6">
          <h3 className="text-lg font-bold font-Outfit flex items-center space-x-2">
            <FileSpreadsheet className="w-5 h-5 text-accent" />
            <span>Customize CSV Download Fields</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Season */}
            <div className="space-y-2">
              <label className="text-[10px] font-bold uppercase tracking-wider text-text-secondary">Season</label>
              <select
                value={season}
                onChange={(e) => setSeason(e.target.value)}
                className="w-full bg-white/5 border border-white/5 rounded-2xl px-4 py-3 text-xs focus:outline-none text-text-primary"
              >
                <option value="" className="bg-background">All Seasons</option>
                {[1, 2, 3, 4, 5].map((s) => (
                  <option key={s} value={s} className="bg-background">Season {s}</option>
                ))}
              </select>
            </div>

            {/* Industry */}
            <div className="space-y-2">
              <label className="text-[10px] font-bold uppercase tracking-wider text-text-secondary">Industry</label>
              <select
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                className="w-full bg-white/5 border border-white/5 rounded-2xl px-4 py-3 text-xs focus:outline-none text-text-primary"
              >
                <option value="" className="bg-background">All Industries</option>
                {industries.map((ind) => (
                  <option key={ind} value={ind} className="bg-background">{ind}</option>
                ))}
              </select>
            </div>

            {/* Deal Status */}
            <div className="space-y-2">
              <label className="text-[10px] font-bold uppercase tracking-wider text-text-secondary">Deal Status</label>
              <select
                value={dealStatus}
                onChange={(e) => setDealStatus(e.target.value)}
                className="w-full bg-white/5 border border-white/5 rounded-2xl px-4 py-3 text-xs focus:outline-none text-text-primary"
              >
                <option value="" className="bg-background">All Deal Statuses</option>
                <option value="funded" className="bg-background">Funded Deals Only</option>
                <option value="not funded" className="bg-background">Rejected / No Deal Only</option>
              </select>
            </div>

            {/* Shark */}
            <div className="space-y-2">
              <label className="text-[10px] font-bold uppercase tracking-wider text-text-secondary">Investor Shark</label>
              <select
                value={sharkId}
                onChange={(e) => setSharkId(e.target.value)}
                className="w-full bg-white/5 border border-white/5 rounded-2xl px-4 py-3 text-xs focus:outline-none text-text-primary"
              >
                <option value="" className="bg-background">All Sharks</option>
                {sharks.map((s) => (
                  <option key={s.id} value={s.id} className="bg-background">{s.name}</option>
                ))}
              </select>
            </div>
          </div>

          <button
            onClick={handleDownload}
            className="w-full flex items-center justify-center space-x-2 bg-accent hover:bg-accent-hover text-white font-bold py-4 rounded-2xl shadow-lg hover:shadow-accent/20 transition-all font-Outfit"
          >
            <Download className="w-5 h-5" />
            <span>Generate & Download Filtered CSV</span>
          </button>
        </div>

        {/* Right Side: Columns Preview list */}
        <div className="lg:col-span-5 glass p-8 rounded-3xl border border-white/5 space-y-4">
          <div className="flex items-center space-x-2 text-accent">
            <Table className="w-5 h-5" />
            <h3 className="font-bold font-Outfit text-base text-text-primary">Included CSV Columns</h3>
          </div>
          <p className="text-text-secondary text-xs">
            The generated export uses PitchIQ fully reconciled metrics. The columns included out-of-the-box are:
          </p>

          <div className="grid grid-cols-2 gap-2 max-h-[250px] overflow-y-auto pr-2 pt-2 text-xs">
            {columns.map((col, idx) => (
              <span key={idx} className="p-2 bg-white/5 border border-white/5 rounded-xl font-mono text-[10px] text-accent">
                {col}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
