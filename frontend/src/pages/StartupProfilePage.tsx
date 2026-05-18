import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, ExternalLink, ShieldCheck, Heart, Award, Users, Activity, Sparkles, DollarSign, Percent } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { API_BASE } from '../config';

export default function StartupProfilePage() {
  const { slug } = useParams<{ slug: string }>();
  const [startup, setStartup] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDetail = async () => {
      try {
        const res = await axios.get(`${API_BASE}/startups/detail/${slug}`);
        setStartup(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [slug]);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 flex justify-center items-center">
        <div className="w-10 h-10 border-4 border-accent border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!startup) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center space-y-4">
        <h3 className="text-2xl font-bold">Startup Not Found</h3>
        <Link to="/" className="text-accent hover:underline">Back to Homepage</Link>
      </div>
    );
  }

  // Prepping chart data
  const chartData = startup.financials.map((f: any) => ({
    year: f.year || '2023',
    revenue: f.revenue || 0,
    profit: f.profit || 0,
  }));

  const deal = startup.deal;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Back button */}
      <Link to="/" className="flex items-center space-x-2 text-sm text-text-secondary hover:text-text-primary transition-all">
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Directory</span>
      </Link>

      {/* Header Info */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center p-8 glass rounded-3xl border border-white/5 gap-4">
        <div className="space-y-3">
          <div className="flex flex-wrap gap-2">
            <span className="text-[10px] uppercase font-bold tracking-wider text-accent bg-accent/10 px-3 py-1 rounded-full border border-accent/20">
              {startup.industry}
            </span>
            <span className="text-[10px] uppercase font-bold tracking-wider text-accent bg-accent/10 px-3 py-1 rounded-full border border-accent/20">
              {startup.business_model}
            </span>
            <span className="text-xs text-text-secondary py-1 px-2 font-medium">
              Season {startup.season}
            </span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-extrabold font-Outfit">{startup.name}</h1>
          <p className="text-text-secondary text-sm leading-relaxed max-w-2xl">{startup.description}</p>
        </div>

        <div className="flex items-center space-x-3 bg-white/5 px-4 py-3 rounded-2xl border border-white/5">
          <ExternalLink className="w-4 h-4 text-accent" />
          <a href={startup.website} target="_blank" rel="noopener noreferrer" className="text-sm font-bold text-accent hover:underline">
            Visit Website
          </a>
        </div>
      </div>

      {/* Main Breakdown Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Side (Metrics, Deal Summary, Financials) */}
        <div className="lg:col-span-8 space-y-6">
          {/* Deal Comparison Card */}
          <div className="glass p-6 rounded-3xl border border-white/5 space-y-4">
            <h3 className="text-lg font-bold font-Outfit flex items-center space-x-2">
              <ShieldCheck className="w-5 h-5 text-accent" />
              <span>Investment Deal Summary</span>
            </h3>
            
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {/* Asked details */}
              <div className="p-4 bg-white/5 rounded-2xl border border-white/5">
                <span className="text-[10px] font-bold text-text-secondary uppercase">Asked Terms</span>
                <div className="text-lg font-bold mt-1 font-Outfit text-text-primary">
                  {deal?.ask_amount ? `₹${deal.ask_amount} Lakhs` : 'Not Disclosed'}
                </div>
                <div className="text-xs text-text-secondary mt-1">
                  for {deal?.ask_equity ? `${deal.ask_equity}%` : 'Not Disclosed'} equity
                </div>
                <div className="text-[10px] text-accent mt-2">
                  Valuation Asked: {deal?.ask_valuation ? `₹${deal.ask_valuation} Lakhs` : 'Not Disclosed'}
                </div>
              </div>

              {/* Final Details */}
              <div className="p-4 bg-white/5 rounded-2xl border border-white/5">
                <span className="text-[10px] font-bold text-text-secondary uppercase">Final Deal</span>
                <div className="text-lg font-bold mt-1 font-Outfit text-accent">
                  {deal?.final_deal_amount ? `₹${deal.final_deal_amount} Lakhs` : 'Rejected / No Deal'}
                </div>
                <div className="text-xs text-text-secondary mt-1">
                  for {deal?.final_equity ? `${deal.final_equity}%` : 'No Equity'} equity
                </div>
                <div className="text-[10px] text-accent mt-2">
                  Deal Valuation: {deal?.final_valuation ? `₹${deal.final_valuation} Lakhs` : 'Not Disclosed'}
                </div>
              </div>

              {/* Deal Status Banner */}
              <div className="p-4 bg-white/5 rounded-2xl border border-white/5 flex flex-col justify-center">
                <span className="text-[10px] font-bold text-text-secondary uppercase">Deal Status</span>
                <div className={`text-xl font-black mt-1 uppercase font-Outfit ${
                  deal?.deal_status === 'funded' ? 'text-accent' : 'text-danger'
                }`}>
                  {deal?.deal_status === 'funded' ? 'Funded' : 'Not Funded'}
                </div>
                <span className="text-[10px] text-text-secondary mt-1">
                  {deal?.notes || 'End of round pitch result.'}
                </span>
              </div>
            </div>
          </div>

          {/* Revenue & Profit Trends Recharts */}
          {chartData.length > 0 && (
            <div className="glass p-6 rounded-3xl border border-white/5 space-y-4">
              <h3 className="text-lg font-bold font-Outfit">Financial Growth Trends</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <XAxis dataKey="year" stroke="#4B5563" fontSize={11} />
                    <YAxis stroke="#4B5563" fontSize={11} />
                    <Tooltip contentStyle={{ backgroundColor: '#141414', border: '1px solid #1F1F1F', borderRadius: '8px' }} />
                    <Line type="monotone" dataKey="revenue" name="Revenue (Lakhs)" stroke="#00F2FE" strokeWidth={3} activeDot={{ r: 8 }} />
                    <Line type="monotone" dataKey="profit" name="Profit (Lakhs)" stroke="#4FACFE" strokeWidth={3} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Financial details table */}
          {startup.financials.length > 0 && (
            <div className="glass p-6 rounded-3xl border border-white/5 space-y-4">
              <h3 className="text-lg font-bold font-Outfit">Financial Performance Grid</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-white/5 text-text-secondary uppercase">
                      <th className="py-2">Year</th>
                      <th className="py-2">Revenue (Lakhs)</th>
                      <th className="py-2">Gross Margin (%)</th>
                      <th className="py-2">Net Margin (%)</th>
                      <th className="py-2">EBITDA Margin (%)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {startup.financials.map((f: any, idx: number) => (
                      <tr key={idx} className="border-b border-white/5">
                        <td className="py-3 font-bold text-text-primary">{f.year || '2023'}</td>
                        <td className="py-3 font-Outfit">{f.revenue ? `₹${f.revenue} Lakhs` : 'Not Disclosed'}</td>
                        <td className="py-3 font-Outfit">{f.gross_margin ? `${f.gross_margin}%` : 'Not Disclosed'}</td>
                        <td className="py-3 font-Outfit">{f.net_margin ? `${f.net_margin}%` : 'Not Disclosed'}</td>
                        <td className="py-3 font-Outfit">{f.ebitda_margin ? `${f.ebitda_margin.toFixed(1)}%` : 'Not Disclosed'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* Right Side (Health Score, Sharks, Insights) */}
        <div className="lg:col-span-4 space-y-6">
          {/* Health Score Gauge */}
          {startup.health_score && (
            <div className="glass p-6 rounded-3xl border border-white/5 space-y-6 text-center">
              <h3 className="text-base font-bold font-Outfit flex items-center justify-center space-x-2">
                <Activity className="w-4 h-4 text-accent" />
                <span>Investment Health Score</span>
              </h3>
              
              <div className="relative inline-flex items-center justify-center">
                <div className="w-32 h-32 rounded-full border-8 border-white/5 flex items-center justify-center">
                  <span className="text-4xl font-extrabold text-accent font-Outfit">
                    {startup.health_score.total}
                  </span>
                </div>
              </div>

              {/* Progress Bar Breakdown */}
              <div className="space-y-3 text-left text-xs pt-4 border-t border-white/5">
                {[
                  { label: 'Growth Velocity', val: startup.health_score.breakdown.growth, max: 25 },
                  { label: 'Profitability Profile', val: startup.health_score.breakdown.profitability, max: 25 },
                  { label: 'Margin Structure', val: startup.health_score.breakdown.margins, max: 20 },
                  { label: 'Target Market Size', val: startup.health_score.breakdown.market_size, max: 15 },
                  { label: 'Founder Pedigree', val: startup.health_score.breakdown.founder_strength, max: 15 },
                ].map((item, index) => (
                  <div key={index} className="space-y-1">
                    <div className="flex justify-between font-medium">
                      <span className="text-text-secondary">{item.label}</span>
                      <span className="text-accent font-bold">{item.val}/{item.max}</span>
                    </div>
                    <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                      <div className="h-full bg-accent rounded-full" style={{ width: `${(item.val / item.max) * 100}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI Insight Box */}
          {startup.ai_insight && (
            <div className="glass p-6 rounded-3xl border border-accent/20 bg-accent/[0.02] space-y-3">
              <h3 className="text-sm font-bold font-Outfit flex items-center space-x-2 text-accent">
                <Sparkles className="w-4 h-4" />
                <span>PitchIQ AI Insight</span>
              </h3>
              <p className="text-xs text-text-primary leading-relaxed whitespace-pre-line" dangerouslySetInnerHTML={{ __html: startup.ai_insight }} />
            </div>
          )}

          {/* Invested Sharks */}
          {startup.shark_deals.length > 0 && (
            <div className="glass p-6 rounded-3xl border border-white/5 space-y-4">
              <h3 className="text-base font-bold font-Outfit flex items-center space-x-2">
                <Users className="w-4 h-4 text-accent" />
                <span>Sharks Invested</span>
              </h3>

              <div className="grid grid-cols-1 gap-3">
                {startup.shark_deals.map((sd: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-white/5 rounded-2xl border border-white/5">
                    <div>
                      <h4 className="text-xs font-bold text-text-primary">{sd.shark.name}</h4>
                      <span className="text-[10px] text-text-secondary block">{sd.shark.company}</span>
                    </div>
                    <div className="text-right text-xs">
                      <span className="font-bold text-accent font-Outfit block">₹{sd.amount_invested} Lakhs</span>
                      <span className="text-[10px] text-text-secondary">{sd.equity_taken}% Equity Taken</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
