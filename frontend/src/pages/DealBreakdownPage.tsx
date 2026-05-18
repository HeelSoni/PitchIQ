import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { ShieldAlert, TrendingUp, Users, ArrowUpRight, DollarSign } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function DealBreakdownPage() {
  const [deals, setDeals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDeals = async () => {
      try {
        const res = await axios.get('http://127.0.0.1:8000/api/startups/?deal_status=funded&order_by=valuation');
        setDeals(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchDeals();
  }, []);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 flex justify-center items-center">
        <div className="w-10 h-10 border-4 border-accent border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      <div className="space-y-4 max-w-3xl">
        <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight font-Outfit">
          Deal{' '}
          <span className="bg-gradient-to-r from-cyan-400 to-cyan-300 bg-clip-text text-transparent">
            Breakdown
          </span>
        </h1>
        <p className="text-text-secondary text-sm sm:text-base">
          Analyze every funded pitch, looking at valuation drops, founder equity dilutions, total capital raised, and details of which sharks pooled their capital.
        </p>
      </div>

      {/* Grid List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {deals.map((d: any, idx: number) => {
          const askVal = d.deal?.ask_valuation || 0;
          const finalVal = d.deal?.final_valuation || 0;
          const valuationDrop = askVal > 0 && finalVal > 0 ? ((askVal - finalVal) / askVal) * 100 : 0;
          const dilution = d.deal?.final_equity || 0;
          
          return (
            <div key={idx} className="glass p-6 rounded-3xl border border-white/5 space-y-5 hover-lift">
              <div className="flex justify-between items-start">
                <div>
                  <Link to={`/startup/${d.slug}`} className="text-lg font-bold font-Outfit text-text-primary hover:text-accent flex items-center space-x-1.5">
                    <span>{d.name}</span>
                    <ArrowUpRight className="w-4 h-4 text-text-secondary" />
                  </Link>
                  <span className="text-[10px] text-text-secondary uppercase tracking-wider block font-bold mt-1">
                    {d.industry} • Season {d.season}
                  </span>
                </div>
                
                <span className="text-[10px] font-bold text-accent bg-accent/10 px-2.5 py-1 rounded-full border border-accent/20">
                  Funded Deal
                </span>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-3 gap-3 text-xs pt-4 border-t border-white/5">
                <div className="p-3 bg-white/5 rounded-2xl border border-white/5">
                  <span className="text-[10px] text-text-secondary block font-medium">CAPITAL RAISED</span>
                  <span className="font-Outfit font-bold text-text-primary mt-0.5 block">
                    ₹{d.deal?.final_deal_amount} Lakhs
                  </span>
                </div>
                <div className="p-3 bg-white/5 rounded-2xl border border-white/5">
                  <span className="text-[10px] text-text-secondary block font-medium">FINAL VALUATION</span>
                  <span className="font-Outfit font-bold text-accent mt-0.5 block">
                    ₹{finalVal ? `${(finalVal/100).toFixed(1)} Cr` : 'Not Disclosed'}
                  </span>
                </div>
                <div className="p-3 bg-white/5 rounded-2xl border border-white/5">
                  <span className="text-[10px] text-text-secondary block font-medium">DILUTION (%)</span>
                  <span className="font-Outfit font-bold text-accent mt-0.5 block">
                    {dilution}% Equity
                  </span>
                </div>
              </div>

              {/* Valuation gap details */}
              {valuationDrop > 0 && (
                <div className="flex items-center space-x-2 text-[11px] text-accent bg-accent/5 px-3 py-2 rounded-xl border border-accent/10">
                  <TrendingUp className="w-3.5 h-3.5" />
                  <span>
                    Valuation negotiated down by <strong>{valuationDrop.toFixed(1)}%</strong> from the initial ask.
                  </span>
                </div>
              )}

              {/* Investor Split */}
              {d.shark_deals.length > 0 && (
                <div className="space-y-2 pt-2">
                  <span className="text-[10px] text-text-secondary font-bold uppercase tracking-wider block">
                    Investor Equity Splits
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {d.shark_deals.map((sd: any, sIdx: number) => (
                      <span key={sIdx} className="text-[10px] bg-white/5 border border-white/5 px-2.5 py-1 rounded-xl text-text-primary">
                        {sd.shark.name}: <strong>{sd.equity_taken}%</strong>
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
