import React, { useEffect, useState } from 'react';
import { usePitchStore } from '../store/usePitchStore';
import { Users, Award, ShieldCheck, Heart, ArrowUpRight, TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';
import axios from 'axios';

export default function SharksPage() {
  const { sharks, fetchSharks } = usePitchStore();
  const [selectedShark, setSelectedShark] = useState<any>(null);
  const [loadingPortfolio, setLoadingPortfolio] = useState(false);

  useEffect(() => {
    fetchSharks();
  }, []);

  const selectShark = async (sharkId: number) => {
    setLoadingPortfolio(true);
    try {
      const res = await axios.get(`http://127.0.0.1:8000/api/sharks/${sharkId}`);
      setSelectedShark(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingPortfolio(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      <div className="space-y-4 max-w-3xl">
        <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight font-Outfit">
          Meet the{' '}
          <span className="bg-gradient-to-r from-cyan-400 to-cyan-300 bg-clip-text text-transparent">
            Sharks
          </span>
        </h1>
        <p className="text-text-secondary text-sm sm:text-base">
          Click on any shark card below to dynamically query their real-time investment aggregates, ticket size averages, favorite sectors, and their full active startups portfolio grid.
        </p>
      </div>

      {/* Sharks Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {sharks.map((s) => (
          <button
            key={s.id}
            onClick={() => selectShark(s.id)}
            className={`text-left glass p-6 rounded-3xl border transition-all duration-300 hover-lift ${
              selectedShark?.id === s.id ? 'border-accent/50 bg-accent/[0.02]' : 'border-white/5'
            }`}
          >
            <div className="space-y-4">
              <div className="space-y-1">
                <span className="text-[10px] font-bold text-accent bg-accent/10 px-2 py-0.5 rounded-full">
                  {s.company || 'Shark'}
                </span>
                <h3 className="text-lg font-bold font-Outfit text-text-primary">{s.name}</h3>
                <p className="text-[11px] text-text-secondary">{s.title}</p>
              </div>

              {/* Bio snippet */}
              <p className="text-text-secondary text-[11px] line-clamp-2 leading-relaxed">
                {s.bio}
              </p>

              {/* Quick metrics */}
              <div className="flex justify-between items-center pt-3 border-t border-white/5 text-[11px]">
                <div>
                  <span className="text-text-secondary block">NET WORTH</span>
                  <span className="font-bold text-text-primary">{s.net_worth}</span>
                </div>
                <div className="text-right">
                  <span className="text-text-secondary block">DEALS MADE</span>
                  <span className="font-bold text-accent">{s.stats.total_deals} Deals</span>
                </div>
              </div>
            </div>
          </button>
        ))}
      </div>

      {/* Selected Shark Portfolio and Analytics panel */}
      {selectedShark && (
        <div className="glass p-8 rounded-3xl border border-white/5 space-y-8 animate-fadeIn">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-white/5 pb-6 gap-4">
            <div className="space-y-2">
              <h2 className="text-2xl font-bold font-Outfit text-text-primary">
                {selectedShark.name} Investment Analytics
              </h2>
              <p className="text-text-secondary text-xs max-w-2xl">{selectedShark.bio}</p>
            </div>
            
            <div className="flex flex-wrap gap-2">
              {selectedShark.expertise.map((e: string, i: number) => (
                <span key={i} className="text-[10px] font-bold uppercase tracking-wider text-accent bg-accent/10 px-2.5 py-1 rounded-full">
                  {e}
                </span>
              ))}
            </div>
          </div>

          {/* Aggregated stats row */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Total Invested', val: `₹${(selectedShark.stats.total_invested_lakhs / 100).toFixed(2)} Cr` },
              { label: 'Avg Ticket Size', val: `₹${selectedShark.stats.avg_ticket_size_lakhs.toFixed(1)} Lakhs` },
              { label: 'Avg Equity Taken', val: `${selectedShark.stats.avg_equity_percent.toFixed(1)}%` },
              { label: 'Active Seasons', val: selectedShark.seasons.join(', ') },
            ].map((item, index) => (
              <div key={index} className="p-4 bg-white/5 rounded-2xl border border-white/5 text-center">
                <span className="text-[10px] text-text-secondary uppercase block font-bold tracking-wider">{item.label}</span>
                <span className="text-lg sm:text-2xl font-Outfit font-bold mt-1 block text-accent">{item.val}</span>
              </div>
            ))}
          </div>

          {/* Top sectors and portfolio */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
            {/* Sectors */}
            <div className="md:col-span-4 space-y-4">
              <h3 className="text-base font-bold font-Outfit text-text-primary flex items-center space-x-2">
                <TrendingUp className="w-4 h-4 text-accent" />
                <span>Top Investment Industries</span>
              </h3>
              
              <div className="space-y-3 pt-2">
                {selectedShark.stats.favorite_industries.map((ind: string, idx: number) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-white/5 rounded-2xl border border-white/5 text-xs">
                    <span className="font-bold text-text-primary">{ind}</span>
                    <span className="text-[10px] uppercase font-bold text-accent">Rank #{idx+1}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Portfolio startups grid */}
            <div className="md:col-span-8 space-y-4">
              <h3 className="text-base font-bold font-Outfit text-text-primary">
                Active Startups Portfolio ({selectedShark.portfolio.length} Deals)
              </h3>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-h-[300px] overflow-y-auto pr-2">
                {selectedShark.portfolio.map((p: any, idx: number) => (
                  <Link
                    key={idx}
                    to={`/startup/${p.slug}`}
                    className="p-4 bg-white/5 border border-white/5 hover:border-accent/30 rounded-2xl hover-lift flex items-center justify-between text-xs"
                  >
                    <div>
                      <h4 className="font-bold text-text-primary">{p.name}</h4>
                      <span className="text-[10px] text-text-secondary block">{p.industry} • Season {p.season}</span>
                    </div>
                    <div className="text-right">
                      <span className="font-Outfit font-bold text-accent block">₹{p.deal_amount_lakhs} Lakhs</span>
                      <span className="text-[10px] text-text-secondary">{p.equity_taken}% Equity</span>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
