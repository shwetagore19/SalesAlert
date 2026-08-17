import React from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';
import { Award, AlertOctagon, Package } from 'lucide-react';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];

export default function ProductChart({ productData = {} }) {
  const { top_products_by_revenue = [], underperforming_products = [], category_breakdown = [] } = productData;

  const pieData = category_breakdown.map((item) => ({
    name: item.category,
    value: item.revenue,
  }));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Category Distribution Donut Chart */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 shadow-xl shadow-slate-950/50">
        <div className="flex items-center gap-2 mb-4">
          <Package className="w-5 h-5 text-blue-400" />
          <h3 className="text-base font-bold text-white">Category Revenue Share</h3>
        </div>
        <div className="h-64 w-full">
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(val) => [`Rs. ${Number(val).toLocaleString()}`, 'Revenue']}
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }}
                />
                <Legend tick={{ fontSize: 11, fill: '#94a3b8' }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-slate-500 text-xs font-medium">
              No category data available
            </div>
          )}
        </div>
      </div>

      {/* Top Performing Products Table */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 shadow-xl shadow-slate-950/50">
        <div className="flex items-center gap-2 mb-4">
          <Award className="w-5 h-5 text-emerald-400" />
          <h3 className="text-base font-bold text-white">Top Performers by Revenue</h3>
        </div>

        <div className="space-y-3 max-h-64 overflow-y-auto pr-1">
          {top_products_by_revenue.slice(0, 5).map((item, idx) => (
            <div key={idx} className="flex items-center justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <div>
                <p className="text-xs font-bold text-slate-200">{item.product}</p>
                <span className="text-[10px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded-full">{item.category}</span>
              </div>
              <div className="text-right">
                <p className="text-xs font-extrabold text-emerald-400">Rs. {item.revenue?.toLocaleString()}</p>
                <p className="text-[10px] text-slate-400">{item.margin_pct}% Margin</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Underperforming Products Table */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 shadow-xl shadow-slate-950/50">
        <div className="flex items-center gap-2 mb-4">
          <AlertOctagon className="w-5 h-5 text-rose-400" />
          <h3 className="text-base font-bold text-white">Underperforming Products</h3>
        </div>

        <div className="space-y-3 max-h-64 overflow-y-auto pr-1">
          {underperforming_products.slice(0, 5).map((item, idx) => (
            <div key={idx} className="flex items-center justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <div>
                <p className="text-xs font-bold text-slate-200">{item.product}</p>
                <span className="text-[10px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded-full">{item.category}</span>
              </div>
              <div className="text-right">
                <p className="text-xs font-extrabold text-rose-400">Rs. {item.profit?.toLocaleString()} Profit</p>
                <p className="text-[10px] text-slate-400">{item.margin_pct}% Margin</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
