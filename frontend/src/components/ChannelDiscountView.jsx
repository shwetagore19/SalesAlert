import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Legend, Cell } from 'recharts';
import { Store, Percent, ShoppingBag, DollarSign } from 'lucide-react';

export default function ChannelDiscountView({ channels = [], discountData = {} }) {
  const discountTiers = discountData.discount_tiers || [];
  const overallAvgDisc = discountData.overall_avg_discount_pct || 0;

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444'];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Top Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Total Sales Channels</span>
            <h3 className="text-2xl font-black text-white mt-1">{channels.length} Channels Active</h3>
            <p className="text-xs text-slate-400 mt-1">Direct Store, Online, Enterprise B2B</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
            <Store className="w-5 h-5" />
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Overall Avg Discount Rate</span>
            <h3 className="text-2xl font-black text-amber-400 mt-1">{overallAvgDisc}%</h3>
            <p className="text-xs text-slate-400 mt-1">Across all completed orders</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <Percent className="w-5 h-5" />
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Top Channel Margin</span>
            <h3 className="text-2xl font-black text-emerald-400 mt-1">
              {channels.length > 0 ? `${Math.max(...channels.map(c => c.margin_pct)).toFixed(1)}%` : '0%'}
            </h3>
            <p className="text-xs text-slate-400 mt-1">Highest margin profitability</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <DollarSign className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* SALES CHANNEL PERFORMANCE GRID */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-6">
        <div>
          <h3 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
            <Store className="w-5 h-5 text-blue-400" /> Sales Channel Breakdown
          </h3>
          <p className="text-xs text-slate-400 mt-1">Comparative revenue, net profit, average order value, and profit margin across sales channels.</p>
        </div>

        {/* Channel Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {channels.map((ch, idx) => (
            <div key={ch.sales_channel} className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white tracking-wide uppercase">{ch.sales_channel}</span>
                <span className="text-xs font-extrabold px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  {ch.margin_pct}% Margin
                </span>
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">Revenue:</span>
                  <span className="font-extrabold text-white">Rs. {ch.revenue.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">Profit:</span>
                  <span className="font-extrabold text-emerald-400">Rs. {ch.profit.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">Orders / AOV:</span>
                  <span className="font-semibold text-slate-300">{ch.orders} orders (Rs. {Math.round(ch.aov).toLocaleString()})</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Channel Bar Chart */}
        <div className="h-64 pt-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={channels} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="sales_channel" stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <YAxis stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', color: '#fff' }} />
              <Legend />
              <Bar dataKey="revenue" name="Revenue (Rs)" fill="#3b82f6" radius={[6, 6, 0, 0]} />
              <Bar dataKey="profit" name="Profit (Rs)" fill="#10b981" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* DISCOUNT RATE EROSION ANALYSIS */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-6">
        <div>
          <h3 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
            <Percent className="w-5 h-5 text-amber-400" /> Discount Tier Margin Erosion Analysis
          </h3>
          <p className="text-xs text-slate-400 mt-1">Impact of discount rate tiers on profit margin %. Higher discount rates degrade bottom-line profitability.</p>
        </div>

        {/* Discount Tier Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left text-slate-300">
            <thead className="bg-slate-900 text-slate-400 uppercase font-semibold border-b border-slate-800">
              <tr>
                <th className="p-3">Discount Tier</th>
                <th className="p-3">Order Volume</th>
                <th className="p-3">Revenue (Rs)</th>
                <th className="p-3">Profit (Rs)</th>
                <th className="p-3">Effective Margin</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {discountTiers.map((tier, idx) => (
                <tr key={tier.discount_tier} className="hover:bg-slate-900/40 transition-all">
                  <td className="p-3 font-bold text-white">{tier.discount_tier}</td>
                  <td className="p-3">{tier.orders} orders</td>
                  <td className="p-3 font-semibold text-slate-200">Rs. {tier.revenue.toLocaleString()}</td>
                  <td className="p-3 font-semibold text-emerald-400">Rs. {tier.profit.toLocaleString()}</td>
                  <td className="p-3 font-extrabold">
                    <span className={`px-2 py-0.5 rounded-full border ${
                      tier.margin_pct >= 20 ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                    }`}>
                      {tier.margin_pct}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
