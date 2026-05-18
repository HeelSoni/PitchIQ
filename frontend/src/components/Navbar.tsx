import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, BarChart3, TrendingUp, Users, Download, HelpCircle, Award, RefreshCw } from 'lucide-react';

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const links = [
    { name: 'Dashboard', path: '/dashboard', icon: BarChart3 },
    { name: 'Compare', path: '/compare', icon: RefreshCw },
    { name: 'Leaderboard', path: '/leaderboard', icon: Award },
    { name: 'Sharks', path: '/sharks', icon: Users },
    { name: 'Glossary', path: '/glossary', icon: HelpCircle },
    { name: 'Download', path: '/download', icon: Download },
  ];

  return (
    <nav className="sticky top-0 z-50 glass border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <span className="font-extrabold text-2xl tracking-tight bg-gradient-to-r from-cyan-400 to-cyan-300 bg-clip-text text-transparent font-Outfit animate-pulse">
                PitchIQ
              </span>
              <span className="hidden sm:inline-block px-2 py-0.5 text-[10px] uppercase font-bold tracking-wider bg-cyan-500/10 text-cyan-400 rounded-full border border-cyan-500/20">
                Season 1-5
              </span>
            </Link>
          </div>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center space-x-1">
            {links.map((link) => {
              const Icon = link.icon;
              const isActive = location.pathname === link.path;
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                      : 'text-text-secondary hover:text-text-primary hover:bg-white/5 border border-transparent'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{link.name}</span>
                </Link>
              );
            })}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="p-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-white/5 focus:outline-none"
            >
              {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden glass border-t border-border px-2 pt-2 pb-4 space-y-1">
          {links.map((link) => {
            const Icon = link.icon;
            const isActive = location.pathname === link.path;
            return (
              <Link
                key={link.path}
                to={link.path}
                onClick={() => setIsOpen(false)}
                className={`flex items-center space-x-3 px-3 py-3 rounded-lg text-base font-medium transition-all ${
                  isActive
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                    : 'text-text-secondary hover:text-text-primary hover:bg-white/5 border border-transparent'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{link.name}</span>
              </Link>
            );
          })}
        </div>
      )}
    </nav>
  );
}
