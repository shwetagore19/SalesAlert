import React from 'react';
import { Newspaper, BarChart3, TrendingUp, AlertTriangle, Play, RefreshCw, Layers, Target, Store } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, dateStr, onSimulateNextDay, isSimulating }) {
  const tabs = [
    { id: 'overview', label: 'Executive Overview', icon: BarChart3 },
    { id: 'rootcause', label: 'Root-Cause & Actions', icon: Target },
    { id: 'channels', label: 'Channels & Discounts', icon: Store },
    { id: 'newspaper', label: 'AI Daily Newspaper', icon: Newspaper },
    { id: 'products', label: 'Products & Categories', icon: Layers },
    { id: 'regions', label: 'Regional Sales', icon: TrendingUp },
    { id: 'alerts', label: 'Alert Feed', icon: AlertTriangle },
  ];

  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Title */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <Newspaper className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                Sales Intelligence <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 font-medium">AI Newspaper</span>
              </h1>
              <p className="text-xs text-slate-400">Automated Daily Business Briefing & KPI Engine</p>
            </div>
          </div>

          {/* Right Action Controls */}
          <div className="flex items-center gap-4">
            <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-950/40 border border-emerald-500/30 text-xs font-medium text-emerald-300">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Data Source: <span className="text-white font-semibold">PostgreSQL/SQLite DB (Real Verified Facts)</span>
            </div>
            {dateStr && (
              <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700 text-xs font-medium text-slate-300">
                Date: <span className="text-white font-semibold">{dateStr}</span>
              </div>
            )}

            <button
              onClick={onSimulateNextDay}
              disabled={isSimulating}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-md shadow-blue-600/20 transition-all active:scale-95 disabled:opacity-50"
            >
              {isSimulating ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Generating Transactions...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-white" />
                  Simulate Next Day
                </>
              )}
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex space-x-1 border-t border-slate-800/60 pt-1 overflow-x-auto no-scrollbar">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition-all whitespace-nowrap ${
                  isActive
                    ? 'border-blue-500 text-blue-400 bg-blue-500/5'
                    : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : 'text-slate-500'}`} />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
}
