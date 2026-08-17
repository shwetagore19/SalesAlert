import React from 'react';
import { ArrowUpRight, ArrowDownRight, DollarSign, ShoppingBag, TrendingUp, Users, Percent } from 'lucide-react';

const iconMap = {
  revenue: DollarSign,
  profit: TrendingUp,
  margin: Percent,
  orders: ShoppingBag,
  customers: Users,
};

export default function KPICard({ type, title, value, changePct, prefix = '', suffix = '', subtext }) {
  const Icon = iconMap[type] || TrendingUp;
  const isPositive = changePct >= 0;

  return (
    <div className="glass-panel p-5 rounded-2xl border border-slate-800 hover:border-slate-700 transition-all shadow-xl shadow-slate-950/50">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold text-slate-400 tracking-wider uppercase">{title}</span>
        <div className="w-8 h-8 rounded-lg bg-slate-800/80 border border-slate-700/80 flex items-center justify-center text-blue-400">
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div className="flex items-baseline justify-between">
        <h3 className="text-2xl font-extrabold text-white tracking-tight">
          {prefix}{typeof value === 'number' ? value.toLocaleString() : value}{suffix}
        </h3>

        {changePct !== undefined && changePct !== null && (
          <div
            className={`inline-flex items-center gap-0.5 px-2 py-0.5 rounded-full text-xs font-bold border ${
              isPositive
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
            }`}
          >
            {isPositive ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
            {Math.abs(changePct)}%
          </div>
        )}
      </div>

      {subtext && <p className="text-xs text-slate-500 mt-2 font-medium">{subtext}</p>}
    </div>
  );
}
