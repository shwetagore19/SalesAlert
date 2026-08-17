import React, { useState } from 'react';
import { Newspaper, Mail, Send, CheckCircle2, AlertTriangle, Target, Award, Sparkles } from 'lucide-react';
import { reportApi } from '../services/api';

export default function NewspaperView({ reportData = {}, dateStr }) {
  const [emailSent, setEmailSent] = useState(false);
  const [waSent, setWaSent] = useState(false);
  const [loadingEmail, setLoadingEmail] = useState(false);
  const [loadingWa, setLoadingWa] = useState(false);

  const handleSendEmail = async () => {
    setLoadingEmail(true);
    try {
      await reportApi.sendEmail({ date: dateStr });
      setEmailSent(true);
      setTimeout(() => setEmailSent(false), 4000);
    } catch (err) {
      console.error('Email trigger failed', err);
    } finally {
      setLoadingEmail(false);
    }
  };

  const handleSendWhatsApp = async () => {
    setLoadingWa(true);
    try {
      await reportApi.sendWhatsApp({ date: dateStr });
      setWaSent(true);
      setTimeout(() => setWaSent(false), 4000);
    } catch (err) {
      console.error('WhatsApp trigger failed', err);
    } finally {
      setLoadingWa(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Newspaper Header Controls */}
      <div className="flex items-center justify-between glass-panel p-4 rounded-2xl border border-slate-800">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
          <Sparkles className="w-4 h-4 text-blue-400" />
          AI Newspaper Issue • <span className="text-white">{dateStr}</span>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleSendEmail}
            disabled={loadingEmail}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition-all active:scale-95"
          >
            {emailSent ? (
              <>
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Email Briefing Sent!
              </>
            ) : (
              <>
                <Mail className="w-3.5 h-3.5 text-blue-400" /> Send Email Report
              </>
            )}
          </button>

          <button
            onClick={handleSendWhatsApp}
            disabled={loadingWa}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition-all active:scale-95"
          >
            {waSent ? (
              <>
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> WhatsApp Dispatched!
              </>
            ) : (
              <>
                <Send className="w-3.5 h-3.5 text-emerald-400" /> Send WhatsApp Briefing
              </>
            )}
          </button>
        </div>
      </div>

      {/* Main Executive Newspaper Paper Component */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 sm:p-12 shadow-2xl shadow-slate-950 text-slate-200 relative overflow-hidden">
        {/* Newspaper Top Bar */}
        <div className="border-b-2 border-slate-700 pb-4 mb-8 flex flex-col sm:flex-row sm:items-center justify-between text-xs font-bold text-slate-400 tracking-widest uppercase">
          <span>The Daily Sales Chronicle</span>
          <span>Vol. 1 • Executive Briefing</span>
          <span>{dateStr}</span>
        </div>

        {/* Big Headline */}
        <h1 className="font-serif-newspaper text-2xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight mb-6 text-balance">
          {reportData.headline || 'Daily Sales & Operations Summary'}
        </h1>

        {/* Two-Column Newspaper Layout */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 text-sm leading-relaxed text-slate-300">
          
          {/* Left Column: Executive Summary & Top Performers */}
          <div className="space-y-6">
            <div>
              <h3 className="text-xs font-bold text-blue-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <Newspaper className="w-4 h-4" /> Executive Overview
              </h3>
              <p className="font-sans text-slate-300 leading-relaxed bg-slate-800/40 p-4 rounded-2xl border border-slate-800">
                {reportData.executive_summary || 'Analyzing daily transactions...'}
              </p>
            </div>

            <div>
              <h3 className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <Award className="w-4 h-4" /> Top Performers & Highlights
              </h3>
              <p className="font-sans text-slate-300 leading-relaxed bg-slate-800/40 p-4 rounded-2xl border border-slate-800">
                {reportData.top_performers || 'Loading top product and regional performance facts...'}
              </p>
            </div>
          </div>

          {/* Right Column: Warnings & Action Focus */}
          <div className="space-y-6">
            <div>
              <h3 className="text-xs font-bold text-amber-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4" /> Critical Business Warnings
              </h3>
              <div className="font-sans text-slate-300 leading-relaxed bg-amber-500/10 border border-amber-500/20 p-4 rounded-2xl whitespace-pre-line text-xs">
                {reportData.critical_alerts || 'No critical business alerts recorded.'}
              </div>
            </div>

            <div>
              <h3 className="text-xs font-bold text-blue-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <Target className="w-4 h-4" /> Recommended Action Focus
              </h3>
              <div className="font-sans text-slate-300 leading-relaxed bg-blue-500/10 border border-blue-500/20 p-4 rounded-2xl whitespace-pre-line text-xs font-medium">
                {reportData.recommended_focus || 'Loading recommended focus checklist...'}
              </div>
            </div>
          </div>
        </div>

        {/* Newspaper Footer */}
        <div className="border-t border-slate-800 mt-10 pt-4 text-center text-xs text-slate-500 font-medium">
          Generated automatically by AI Sales Intelligence System • Verified Fact Engine
        </div>
      </div>
    </div>
  );
}
