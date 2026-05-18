import React, { useEffect } from 'react';
import { usePitchStore } from '../store/usePitchStore';
import { Search, SlidersHorizontal, ArrowRight, DollarSign, TrendingUp, Percent, UserCheck } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function HomePage() {
  const {
    startups,
    industries,
    sharks,
    stats,
    loading,
    filters,
    setFilter,
    resetFilters,
    fetchStartups,
    fetchIndustries,
    fetchSharks,
    fetchStats
  } = usePitchStore();

  useEffect(() => {
    fetchStartups();
    fetchIndustries();
    fetchSharks();
    fetchStats();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      {/* Hero Section */}
      <div className="text-center space-y-4 max-w-3xl mx-auto py-8">
        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight font-Outfit">
          Decode every pitch.{' '}
          <span className="bg-gradient-to-r from-cyan-400 via-cyan-300 to-cyan-200 bg-clip-text text-transparent">
            Understand every deal.
          </span>
        </h1>
        <p className="text-text-secondary text-base sm:text-lg max-w-xl mx-auto">
          The ultimate Shark Tank India analytics platform. Real data, financial ratios, investment health metrics, and deep shark insights for Seasons 1 to 5.
        </p>
      </div>

      {/* Stats Bar */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Total Pitches', value: stats.total_pitches, icon: SlidersHorizontal, color: 'text-accent' },
            { label: 'Deals Secured', value: stats.total_deals, icon: UserCheck, color: 'text-cyan-400' },
            { label: 'Total Investment', value: `₹${(stats.total_investment / 100).toFixed(1)} Cr`, icon: DollarSign, color: 'text-amber-400' },
            { label: 'Success Rate', value: `${stats.success_rate}%`, icon: TrendingUp, color: 'text-accent' }
          ].map((item, index) => {
            const Icon = item.icon;
            return (
              <div key={index} className="glass p-5 rounded-2xl border border-white/5 flex items-center justify-between">
                <div className="space-y-1">
                  <span className="text-xs text-text-secondary font-medium uppercase tracking-wider">{item.label}</span>
                  <h3 className="text-2xl sm:text-3xl font-bold font-Outfit">{item.value}</h3>
                </div>
                <div className={`p-3 bg-white/5 rounded-xl ${item.color}`}>
                  <Icon className="w-6 h-6" />
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Controls & Advanced Filters */}
      <div className="glass p-6 rounded-3xl border border-white/5 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
          {/* Search bar */}
          <div className="md:col-span-6 relative">
            <Search className="absolute left-3 top-3.5 w-4 h-4 text-text-secondary" />
            <input
              type="text"
              placeholder="Search startup by name..."
              value={filters.search}
              onChange={(e) => setFilter('search', e.target.value)}
              className="w-full bg-white/5 border border-white/5 rounded-2xl pl-10 pr-4 py-3 text-sm focus:outline-none focus:border-accent/50 text-text-primary"
            />
          </div>

          {/* Season Filter */}
          <div className="md:col-span-3">
            <select
              value={filters.season}
              onChange={(e) => setFilter('season', e.target.value)}
              className="w-full bg-white/5 border border-white/5 rounded-2xl px-4 py-3 text-sm focus:outline-none text-text-primary"
            >
              <option value="" className="bg-background">All Seasons</option>
              {[1, 2, 3, 4, 5].map((s) => (
                <option key={s} value={s} className="bg-background">Season {s}</option>
              ))}
            </select>
          </div>

          {/* Deal Status */}
          <div className="md:col-span-3">
            <select
              value={filters.deal_status}
              onChange={(e) => setFilter('deal_status', e.target.value)}
              className="w-full bg-white/5 border border-white/5 rounded-2xl px-4 py-3 text-sm focus:outline-none text-text-primary"
            >
              <option value="" className="bg-background">All Deal Statuses</option>
              <option value="funded" className="bg-background">Funded Only</option>
              <option value="not funded" className="bg-background">Rejected/No Deal</option>
            </select>
          </div>
        </div>

        {/* Micro-checkbox row */}
        <div className="flex flex-wrap gap-4 pt-2 border-t border-white/5 text-xs text-text-secondary font-medium">
          <label className="flex items-center space-x-2 cursor-pointer hover:text-text-primary">
            <input
              type="checkbox"
              checked={filters.profitable}
              onChange={(e) => setFilter('profitable', e.target.checked)}
              className="rounded bg-white/5 border-white/10 text-accent focus:ring-accent"
            />
            <span>Profitable Only</span>
          </label>
          
          <label className="flex items-center space-x-2 cursor-pointer hover:text-text-primary">
            <input
              type="checkbox"
              checked={filters.revenue_gt_1cr}
              onChange={(e) => setFilter('revenue_gt_1cr', e.target.checked)}
              className="rounded bg-white/5 border-white/10 text-accent focus:ring-accent"
            />
            <span>Revenue &gt; 1Cr</span>
          </label>

          <label className="flex items-center space-x-2 cursor-pointer hover:text-text-primary">
            <input
              type="checkbox"
              checked={filters.margin_gt_30}
              onChange={(e) => setFilter('margin_gt_30', e.target.checked)}
              className="rounded bg-white/5 border-white/10 text-accent focus:ring-accent"
            />
            <span>Margin &gt; 30%</span>
          </label>

          <button onClick={resetFilters} className="ml-auto text-accent hover:text-accent-hover font-bold">
            Clear Filters
          </button>
        </div>
      </div>

      {/* Featured Startup Grid */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold font-Outfit">Explore Startup Pitches</h2>
          <span className="text-sm text-text-secondary">{startups.length} startups found</span>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="glass h-64 rounded-3xl animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {startups.map((startup) => (
              <Link
                key={startup.slug}
                to={`/startup/${startup.slug}`}
                className="glass p-6 rounded-3xl border border-white/5 hover-lift flex flex-col justify-between space-y-4"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-accent bg-accent/10 px-2.5 py-1 rounded-full border border-accent/20">
                      {startup.industry}
                    </span>
                    <span className="text-xs text-text-secondary font-medium">
                      S{startup.season} • E{startup.id % 20 + 1}
                    </span>
                  </div>
                  <h3 className="text-lg font-bold font-Outfit group-hover:text-accent">{startup.name}</h3>
                  <p className="text-text-secondary text-xs line-clamp-3 leading-relaxed">
                    {startup.description}
                  </p>
                </div>

                <div className="pt-4 border-t border-white/5 flex items-center justify-between text-xs">
                  <div>
                    <span className="text-text-secondary block">ASK AMOUNT</span>
                    <span className="font-bold text-text-primary">
                      {startup.deal?.ask_amount ? `₹${startup.deal.ask_amount} Lakhs` : 'Not Disclosed'}
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-text-secondary block">DEAL STATUS</span>
                    <span className={`font-bold ${
                      startup.deal?.deal_status === 'funded' ? 'text-accent' : 'text-danger'
                    }`}>
                      {startup.deal?.deal_status === 'funded' ? 'Funded' : 'Not Funded'}
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
