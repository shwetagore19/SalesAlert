import React from 'react';
import { Target, HelpCircle, AlertOctagon, CheckCircle2, TrendingUp, TrendingDown, Layers, ArrowUpRight, ArrowDownRight, Lightbulb } from 'lucide-react';

export default function RootCauseView({ rootCauseData, recommendations = [] }) {
  if (!rootCauseData || !rootCauseData.date) {
    return (
      <div className="glass-panel p-8 rounded-2xl border border-slate-800 text-center text-slate-400">
        Loading Root-Cause Intelligence Engine...
      </div>
    );
  }

  const {
    date,
    previous_date,
    summary_narrative,
    total_revenue_delta = 0,
    revenue_change_pct = 0,
    total_profit_delta = 0,
    profit_change_pct = 0,
    discount_rate_delta_pct = 0,
    category_decomposition = [],
    top_product_gainers = [],
    top_product_losers = [],
    channel_contributors = []
  } = rootCauseData;

  const isRevPos = total_revenue_delta >= 0;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Top Banner Header */}
      <div className="glass-panel p-6 rounded-2xl border border-blue-500/20 bg-gradient-to-r from-blue-950/40 via-indigo-950/20 to-slate-900 shadow-2xl">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 text-xs font-semibold uppercase tracking-wider mb-2">
              <Target className="w-3.5 h-3.5" /> Root-Cause Intelligence Engine
            </div>
            <h2 className="text-2xl font-black text-white tracking-tight">
              Executive Diagnosis: {date} vs {previous_date}
            </h2>
            <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
              Mathematical variance decomposition analyzing exact contributors behind top-line and profit shifts.
            </p>
          </div>

          <div className="flex items-center gap-4 bg-slate-900/80 p-3 rounded-xl border border-slate-800">
            <div>
              <span className="text-xs text-slate-400 font-medium">Revenue Delta</span>
              <div className={`text-lg font-black flex items-center gap-1 ${isRevPos ? 'text-emerald-400' : 'text-rose-400'}`}>
                {isRevPos ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                Rs. {total_revenue_delta >= 0 ? '+' : ''}{total_revenue_delta.toLocaleString()} ({revenue_change_pct >= 0 ? '+' : ''}{revenue_change_pct.toFixed(1)}%)
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 5 MANAGERIAL QUESTIONS GRID */}

      {/* QUESTION 1 & 2: WHAT HAPPENED TODAY & WHY DID IT HAPPEN? */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center gap-2 text-blue-400 font-bold text-sm tracking-wide uppercase">
            <HelpCircle className="w-4 h-4" /> 1. What Happened Today?
          </div>
          <p className="text-slate-200 text-sm leading-relaxed bg-slate-900/60 p-4 rounded-xl border border-slate-800/80">
            {summary_narrative}
          </p>
          <div className="grid grid-cols-2 gap-4 pt-2">
            <div className="p-3 rounded-xl bg-slate-900/40 border border-slate-800">
              <span className="text-xs text-slate-400 font-medium">Net Profit Delta</span>
              <p className={`text-base font-extrabold ${total_profit_delta >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                Rs. {total_profit_delta >= 0 ? '+' : ''}{total_profit_delta.toLocaleString()} ({profit_change_pct >= 0 ? '+' : ''}{profit_change_pct.toFixed(1)}%)
              </p>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/40 border border-slate-800">
              <span className="text-xs text-slate-400 font-medium">Discount Rate Shift</span>
              <p className="text-base font-extrabold text-amber-400">
                {discount_rate_delta_pct >= 0 ? '+' : ''}{discount_rate_delta_pct.toFixed(1)}% pts
              </p>
            </div>
          </div>
        </div>

        {/* QUESTION 2: WHY DID IT HAPPEN? (CATEGORY VARIANCE) */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center gap-2 text-indigo-400 font-bold text-sm tracking-wide uppercase">
            <Layers className="w-4 h-4" /> 2. Why Did It Happen? (Category Variance)
          </div>
          <div className="space-y-3 max-h-64 overflow-y-auto pr-1">
            {category_decomposition.map((cat) => {
              const isPos = cat.delta >= 0;
              return (
                <div key={cat.name} className="flex items-center justify-between p-3 rounded-xl bg-slate-900/50 border border-slate-800/80">
                  <div>
                    <span className="text-xs font-bold text-white">{cat.name}</span>
                    <p className="text-xs text-slate-400">Rs. {cat.current.toLocaleString()} (prev: Rs. {cat.previous.toLocaleString()})</p>
                  </div>
                  <div className="text-right">
                    <span className={`text-xs font-extrabold px-2 py-0.5 rounded-full border ${
                      isPos ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                    }`}>
                      {isPos ? '+' : ''}Rs. {cat.delta.toLocaleString()}
                    </span>
                    <p className="text-xs text-slate-500 mt-1">{cat.share_pct}% of total delta</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* QUESTION 3: WHICH PRODUCTS & CHANNELS CAUSED THE CHANGE? */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center gap-2 text-amber-400 font-bold text-sm tracking-wide uppercase">
          <TrendingUp className="w-4 h-4" /> 3. Which Products & Channels Caused the Change?
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Top Gainers */}
          <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/20 space-y-3">
            <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
              <TrendingUp className="w-3.5 h-3.5" /> Top 3 Revenue Gainers
            </h4>
            {top_product_gainers.map((g) => (
              <div key={g.product} className="flex items-center justify-between text-xs py-1 border-b border-emerald-900/30 last:border-0">
                <span className="font-semibold text-slate-200">{g.product}</span>
                <span className="font-extrabold text-emerald-400">+Rs. {g.delta.toLocaleString()}</span>
              </div>
            ))}
          </div>

          {/* Top Losers */}
          <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-500/20 space-y-3">
            <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
              <TrendingDown className="w-3.5 h-3.5" /> Top 3 Revenue Drag Products
            </h4>
            {top_product_losers.map((l) => (
              <div key={l.product} className="flex items-center justify-between text-xs py-1 border-b border-rose-900/30 last:border-0">
                <span className="font-semibold text-slate-200">{l.product}</span>
                <span className="font-extrabold text-rose-400">Rs. {l.delta.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* QUESTION 4 & 5: RISKS/OPPORTUNITIES & MANAGER ACTION ITEMS */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm tracking-wide uppercase">
          <Lightbulb className="w-4 h-4" /> 4 & 5. Key Risks, Opportunities & Manager Action Plan
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {recommendations.map((rec, idx) => {
            const isHigh = rec.priority === 'HIGH';
            const isMed = rec.priority === 'MEDIUM';
            return (
              <div
                key={idx}
                className={`p-5 rounded-xl border flex flex-col justify-between transition-all ${
                  isHigh
                    ? 'bg-rose-950/20 border-rose-500/30 hover:border-rose-500/50'
                    : isMed
                    ? 'bg-amber-950/20 border-amber-500/30 hover:border-amber-500/50'
                    : 'bg-blue-950/20 border-blue-500/30 hover:border-blue-500/50'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{rec.area}</span>
                    <span
                      className={`text-[10px] font-extrabold px-2 py-0.5 rounded-full border ${
                        isHigh
                          ? 'bg-rose-500/20 text-rose-400 border-rose-500/40'
                          : isMed
                          ? 'bg-amber-500/20 text-amber-400 border-amber-500/40'
                          : 'bg-blue-500/20 text-blue-400 border-blue-500/40'
                      }`}
                    >
                      {rec.priority} PRIORITY
                    </span>
                  </div>
                  <h4 className="text-sm font-extrabold text-white mb-2 leading-snug">{rec.title}</h4>
                  <p className="text-xs text-slate-300 leading-relaxed">{rec.description}</p>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                  <span className="text-slate-400 font-medium">Expected Impact:</span>
                  <span className="font-bold text-emerald-400">{rec.expected_impact}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
