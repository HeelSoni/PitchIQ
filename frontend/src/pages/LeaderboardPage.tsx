import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Award, Zap, Award as GoldIcon, ShieldAlert } from 'lucide-react';
import { Link } from 'react-router-dom';
import { API_BASE } from '../config';

export default function LeaderboardPage() {
  const [leaderboard, setLeaderboard] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const res = await axios.get(`${API_BASE}/analytics/leaderboard`);
        setLeaderboard(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchLeaderboard();
  }, []);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 flex justify-center items-center">
        <div className="w-10 h-10 border-4 border-accent border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const items = [
    { title: 'Biggest Deal Secured', data: leaderboard.biggest_deal, desc: 'Highest absolute capital invested in a single round.' },
    { title: 'Highest Valuation Secured', data: leaderboard.biggest_valuation, desc: 'Highest implied post-money valuation at deal close.' },
    { title: 'Highest Disclosed Revenue', data: leaderboard.highest_revenue, desc: 'Top-ranking startup by yearly sales figures.' },
    { title: 'Fastest Profit Engine', data: leaderboard.fastest_growing, desc: 'Highest absolute net profitability record.' },
    { title: 'Lowest Funded Valuation', data: leaderboard.lowest_valuation_funded, desc: 'Lowest valuation that successfully secured a shark partnership.' },
    { title: 'Highest EBITDA Operating Margins', data: leaderboard.highest_ebitda_margin, desc: 'Cleanest operating model with premium operational efficiency.' },
    { title: 'Most Active Shark', data: leaderboard.most_active_shark, desc: 'Shark with the absolute highest transaction/deal volume.' },
    { title: 'Sector with Most Deals', data: leaderboard.industry_most_deals, desc: 'Top industrial sector by aggregate funding count.' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      <div className="space-y-4 max-w-3xl">
        <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight font-Outfit">
          Hall of{' '}
          <span className="bg-gradient-to-r from-cyan-400 to-cyan-300 bg-clip-text text-transparent">
            Fame
          </span>
        </h1>
        <p className="text-text-secondary text-sm sm:text-base">
          PitchIQ dynamic leaderboards showcasing record-breaking milestones, biggest investments, highest margin companies, and active shark portfolios.
        </p>
      </div>

      {/* Grid List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {items.map((item, index) => (
          <div key={index} className="glass p-6 rounded-3xl border border-white/5 space-y-4 flex flex-col justify-between hover-lift">
            <div className="space-y-2">
              <div className="flex items-center space-x-2 text-accent">
                <GoldIcon className="w-5 h-5 text-amber-400" />
                <h3 className="font-bold font-Outfit text-base text-text-primary">{item.title}</h3>
              </div>
              <p className="text-text-secondary text-xs">{item.desc}</p>
            </div>

            <div className="p-4 bg-white/5 border border-white/5 rounded-2xl flex items-center justify-between">
              <div>
                {item.data.slug ? (
                  <Link to={`/startup/${item.data.slug}`} className="text-sm font-bold text-text-primary hover:text-accent">
                    {item.data.name}
                  </Link>
                ) : (
                  <span className="text-sm font-bold text-text-primary">{item.data.name}</span>
                )}
                <span className="text-[10px] text-text-secondary block mt-0.5">RECORD HOLDER</span>
              </div>

              <div className="text-right">
                <span className="text-base font-extrabold text-accent font-Outfit">{item.data.value}</span>
                <span className="text-[10px] text-text-secondary block mt-0.5">MILESTONE</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
