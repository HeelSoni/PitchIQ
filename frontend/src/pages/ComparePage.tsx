import React, { useState, useEffect } from 'react';
import { usePitchStore } from '../store/usePitchStore';
import axios from 'axios';
import { ArrowLeftRight, CheckCircle2, Trophy } from 'lucide-react';

export default function ComparePage() {
  const { startups, fetchStartups } = usePitchStore();
  const [slugA, setSlugA] = useState('');
  const [slugB, setSlugB] = useState('');
  const [startupA, setStartupA] = useState<any>(null);
  const [startupB, setStartupB] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchStartups();
  }, []);

  const handleCompare = async () => {
    if (!slugA || !slugB) return;
    setLoading(true);
    try {
      const res = await axios.get(`http://127.0.0.1:8000/api/startups/compare?a_slug=${slugA}&b_slug=${slugB}`);
      setStartupA(res.data.startup_a);
      setStartupB(res.data.startup_b);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Helper to get financial values
  const getFin = (startup: any, key: string) => {
    if (!startup?.financials?.length) return 0;
    return startup.financials[0][key] || 0;
  };

  // Highlighting winner helper
  const getWinner = (valA: number, valB: number, highIsBetter = true) => {
    if (valA === valB) return '';
    if (highIsBetter) {
      return valA > valB ? 'A' : 'B';
    } else {
      return valA < valB ? 'A' : 'B';
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      <div className="space-y-4 max-w-3xl">
        <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight font-Outfit">
          Startup{' '}
          <span className="bg-gradient-to-r from-cyan-400 to-cyan-300 bg-clip-text text-transparent">
            Comparison
          </span>
        </h1>
        <p className="text-text-secondary text-sm sm:text-base">
          Select any 2 startups to trigger a side-by-side quantitative battle. PitchIQ automatically analyzes revenues, net margins, asked vs final valuations, and highlights the statistical winner for each category.
        </p>
      </div>

      {/* Selectors Panel */}
      <div className="glass p-6 rounded-3xl border border-white/5 grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
        {/* Startup A Dropdown */}
        <div className="md:col-span-5">
          <label className="block text-[10px] font-bold uppercase tracking-wider text-text-secondary mb-2">Startup A</label>
          <select
            value={slugA}
            onChange={(e) => setSlugA(e.target.value)}
            className="w-full bg-white/5 border border-white/5 rounded-2xl px-4 py-3 text-sm focus:outline-none text-text-primary"
          >
            <option value="" className="bg-background">Select a Startup...</option>
            {startups.map((s) => (
              <option key={s.slug} value={s.slug} className="bg-background">{s.name}</option>
            ))}
          </select>
        </div>

        {/* Compare Icon */}
        <div className="md:col-span-2 flex justify-center pt-6 md:pt-0">
          <button
            onClick={handleCompare}
            disabled={!slugA || !slugB || loading}
            className="bg-accent hover:bg-accent-hover disabled:bg-white/5 text-white p-3 rounded-full shadow-lg hover:shadow-accent/20 hover-lift disabled:cursor-not-allowed transition-all"
          >
            <ArrowLeftRight className="w-5 h-5" />
          </button>
        </div>

        {/* Startup B Dropdown */}
        <div className="md:col-span-5">
          <label className="block text-[10px] font-bold uppercase tracking-wider text-text-secondary mb-2">Startup B</label>
          <select
            value={slugB}
            onChange={(e) => setSlugB(e.target.value)}
            className="w-full bg-white/5 border border-white/5 rounded-2xl px-4 py-3 text-sm focus:outline-none text-text-primary"
          >
            <option value="" className="bg-background">Select a Startup...</option>
            {startups.map((s) => (
              <option key={s.slug} value={s.slug} className="bg-background">{s.name}</option>
            ))}
          </select>
        </div>
      </div>

      {loading && (
        <div className="flex justify-center py-10">
          <div className="w-10 h-10 border-4 border-accent border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {/* Comparison Grid */}
      {startupA && startupB && !loading && (
        <div className="glass rounded-3xl border border-white/5 overflow-hidden animate-fadeIn">
          {/* Header Row */}
          <div className="grid grid-cols-3 bg-white/5 border-b border-white/5 text-center p-6 items-center">
            <h3 className="text-left font-Outfit text-lg font-bold text-text-primary">{startupA.name}</h3>
            <span className="text-xs uppercase font-extrabold text-accent font-Outfit">V/S</span>
            <h3 className="text-right font-Outfit text-lg font-bold text-text-primary">{startupB.name}</h3>
          </div>

          {/* Comparison Metrics */}
          <div className="divide-y divide-white/5 text-xs text-center">
            {[
              {
                label: 'Yearly Revenue (Lakhs)',
                valA: getFin(startupA, 'revenue'),
                valB: getFin(startupB, 'revenue'),
                fmt: (v: number) => `₹${v} Lakhs`,
                highIsBetter: true
              },
              {
                label: 'Net Profits (Lakhs)',
                valA: getFin(startupA, 'profit'),
                valB: getFin(startupB, 'profit'),
                fmt: (v: number) => `₹${v.toFixed(1)} Lakhs`,
                highIsBetter: true
              },
              {
                label: 'Gross Operating Margins',
                valA: getFin(startupA, 'gross_margin'),
                valB: getFin(startupB, 'gross_margin'),
                fmt: (v: number) => `${v}%`,
                highIsBetter: true
              },
              {
                label: 'Asked Valuation',
                valA: startupA.deal?.ask_valuation || 0,
                valB: startupB.deal?.ask_valuation || 0,
                fmt: (v: number) => `₹${v} Lakhs`,
                highIsBetter: false
              },
              {
                label: 'Capital Secured',
                valA: startupA.deal?.final_deal_amount || 0,
                valB: startupB.deal?.final_deal_amount || 0,
                fmt: (v: number) => `₹${v} Lakhs`,
                highIsBetter: true
              },
              {
                label: 'Investment Health Score',
                valA: startupA.health_score?.total || 0,
                valB: startupB.health_score?.total || 0,
                fmt: (v: number) => `${v}/100`,
                highIsBetter: true
              }
            ].map((metric, idx) => {
              const winner = getWinner(metric.valA, metric.valB, metric.highIsBetter);
              return (
                <div key={idx} className="grid grid-cols-3 p-4 items-center">
                  {/* Metric A */}
                  <div className={`text-left font-medium font-Outfit flex items-center space-x-2 ${
                    winner === 'A' ? 'text-accent font-bold text-sm' : 'text-text-primary'
                  }`}>
                    {winner === 'A' && <Trophy className="w-4 h-4 text-amber-400" />}
                    <span>{metric.fmt(metric.valA)}</span>
                  </div>

                  {/* Metric Label */}
                  <span className="text-text-secondary font-semibold uppercase text-[10px] tracking-wider">
                    {metric.label}
                  </span>

                  {/* Metric B */}
                  <div className={`text-right font-medium font-Outfit flex items-center justify-end space-x-2 ${
                    winner === 'B' ? 'text-accent font-bold text-sm' : 'text-text-primary'
                  }`}>
                    <span>{metric.fmt(metric.valB)}</span>
                    {winner === 'B' && <Trophy className="w-4 h-4 text-amber-400" />}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
