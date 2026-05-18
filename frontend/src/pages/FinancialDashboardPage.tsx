import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, BarChart, Bar, LineChart, Line, ScatterChart, Scatter, ZAxis } from 'recharts';
import { BarChart3, TrendingUp, DollarSign, RefreshCw } from 'lucide-react';
import { API_BASE } from '../config';

export default function FinancialDashboardPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const res = await axios.get(`${API_BASE}/analytics/dashboard`);
        setData(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 flex justify-center items-center">
        <div className="w-10 h-10 border-4 border-accent border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      <div className="space-y-4 max-w-3xl">
        <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight font-Outfit">
          Financial{' '}
          <span className="bg-gradient-to-r from-cyan-400 to-cyan-300 bg-clip-text text-transparent">
            Dashboard
          </span>
        </h1>
        <p className="text-text-secondary text-sm sm:text-base">
          Interactive deep-dive charts showing macro revenue trajectories, margins trends, asked vs final deals, and equity dilutions aggregated dynamically across all seasons of Shark Tank India.
        </p>
      </div>

      {/* Chart Row 1: Season-by-Season Revenue & Profit Ratios */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Revenue Area Chart */}
        <div className="glass p-6 rounded-3xl border border-white/5 space-y-4">
          <h3 className="text-base font-bold font-Outfit flex items-center space-x-2">
            <TrendingUp className="w-4 h-4 text-accent" />
            <span>Average Yearly Startup Revenue Trends</span>
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.season_trends}>
                <defs>
                  <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00F2FE" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#00F2FE" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="season" stroke="#4B5563" fontSize={11} />
                <YAxis stroke="#4B5563" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#141414', border: '1px solid #1F1F1F', borderRadius: '8px' }} />
                <Area type="monotone" dataKey="avg_revenue_lakhs" name="Avg Revenue (Lakhs)" stroke="#00F2FE" fillOpacity={1} fill="url(#colorRev)" strokeWidth={3} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Profit Trend Chart */}
        <div className="glass p-6 rounded-3xl border border-white/5 space-y-4">
          <h3 className="text-base font-bold font-Outfit flex items-center space-x-2">
            <DollarSign className="w-4 h-4 text-accent" />
            <span>Average Net Profitability Trends</span>
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.season_trends}>
                <defs>
                  <linearGradient id="colorProfit" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#4FACFE" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#4FACFE" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="season" stroke="#4B5563" fontSize={11} />
                <YAxis stroke="#4B5563" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#141414', border: '1px solid #1F1F1F', borderRadius: '8px' }} />
                <Area type="monotone" dataKey="avg_profit_lakhs" name="Avg Profit (Lakhs)" stroke="#4FACFE" fillOpacity={1} fill="url(#colorProfit)" strokeWidth={3} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Chart Row 2: Valuation Gap & Dilution Comparative Analysis */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Margin Trend Lines */}
        <div className="glass p-6 rounded-3xl border border-white/5 space-y-4">
          <h3 className="text-base font-bold font-Outfit">Operating & Gross Margins Averages</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.season_trends}>
                <XAxis dataKey="season" stroke="#4B5563" fontSize={11} />
                <YAxis stroke="#4B5563" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#141414', border: '1px solid #1F1F1F', borderRadius: '8px' }} />
                <Line type="monotone" dataKey="avg_gross_margin" name="Avg Gross Margin (%)" stroke="#00F2FE" strokeWidth={3} />
                <Line type="monotone" dataKey="avg_net_margin" name="Avg Net Margin (%)" stroke="#4FACFE" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Asked vs Final Valuation Comparer */}
        <div className="glass p-6 rounded-3xl border border-white/5 space-y-4">
          <h3 className="text-base font-bold font-Outfit flex items-center space-x-2">
            <RefreshCw className="w-4 h-4 text-accent" />
            <span>Asked Valuation vs Final Valuation (Top Deals)</span>
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.valuation_comparisons}>
                <XAxis dataKey="name" stroke="#4B5563" fontSize={9} />
                <YAxis stroke="#4B5563" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#141414', border: '1px solid #1F1F1F', borderRadius: '8px' }} />
                <Bar dataKey="asked_valuation_lakhs" name="Asked Valuation (Lakhs)" fill="#00F2FE" radius={[4, 4, 0, 0]} />
                <Bar dataKey="final_valuation_lakhs" name="Final Valuation (Lakhs)" fill="#4FACFE" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
