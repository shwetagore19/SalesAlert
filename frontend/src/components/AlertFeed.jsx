import React from 'react';
import { AlertTriangle, AlertCircle, Info, ShieldAlert } from 'lucide-react';

export default function AlertFeed({ alerts = [] }) {
  const getSeverityBadge = (severity) => {
    switch (severity) {
      case 'CRITICAL':
        return {
          bg: 'bg-rose-500/10 border-rose-500/30 text-rose-400',
          icon: ShieldAlert,
        };
      case 'WARNING':
        return {
          bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
          icon: AlertTriangle,
        };
      default:
        return {
          bg: 'bg-blue-500/10 border-blue-500/30 text-blue-400',
          icon: Info,
        };
    }
  };

  return (
    <div className="glass-panel p-6 rounded-2xl border border-slate-800 shadow-xl shadow-slate-950/50">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-amber-400" /> Active Business Alerts
        </h3>
        <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
          {alerts.length} Warnings Triggered
        </span>
      </div>

      {alerts.length > 0 ? (
        <div className="space-y-3">
          {alerts.map((alert, idx) => {
            const badge = getSeverityBadge(alert.severity);
            const Icon = badge.icon;
            return (
              <div key={idx} className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex items-start gap-3">
                <div className={`p-2 rounded-lg border ${badge.bg} shrink-0 mt-0.5`}>
                  <Icon className="w-4 h-4" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold text-slate-200">{alert.title}</h4>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${badge.bg}`}>
                      {alert.severity}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1 leading-relaxed">{alert.message}</p>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="p-8 text-center border border-dashed border-slate-800 rounded-xl">
          <p className="text-xs text-slate-400 font-medium">✅ All business indicators are operating within normal parameters.</p>
        </div>
      )}
    </div>
  );
}
