import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import KPICard from './components/KPICard';
import TrendChart from './components/TrendChart';
import ProductChart from './components/ProductChart';
import RegionalChart from './components/RegionalChart';
import AlertFeed from './components/AlertFeed';
import NewspaperView from './components/NewspaperView';
import RootCauseView from './components/RootCauseView';
import ChannelDiscountView from './components/ChannelDiscountView';
import { dashboardApi, salesApi, alertApi, reportApi, intelligenceApi } from './services/api';
import { RefreshCw } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [isSimulating, setIsSimulating] = useState(false);

  const [todayKpis, setTodayKpis] = useState({});
  const [trends, setTrends] = useState([]);
  const [productData, setProductData] = useState({});
  const [regionalData, setRegionalData] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [report, setReport] = useState({});
  const [rootCauseData, setRootCauseData] = useState({});
  const [recommendations, setRecommendations] = useState([]);
  const [channels, setChannels] = useState([]);
  const [discountData, setDiscountData] = useState({});

  const fetchAllData = async (targetDateStr = null) => {
    try {
      setLoading(true);
      const [
        kpiRes,
        trendRes,
        prodRes,
        regRes,
        alertRes,
        repRes,
        rcRes,
        recRes,
        chRes,
        discRes
      ] = await Promise.all([
        dashboardApi.getToday(targetDateStr),
        dashboardApi.getTrends(30),
        salesApi.getProducts(targetDateStr),
        salesApi.getRegions(targetDateStr),
        alertApi.getAlerts(targetDateStr),
        reportApi.getLatest(targetDateStr),
        intelligenceApi.getRootCause(targetDateStr),
        intelligenceApi.getRecommendations(targetDateStr),
        intelligenceApi.getChannels(targetDateStr),
        intelligenceApi.getDiscountImpact()
      ]);

      setTodayKpis(kpiRes || {});
      setTrends(trendRes || []);
      setProductData(prodRes || {});
      setRegionalData(regRes || {});
      setAlerts(alertRes || []);
      setReport(repRes || {});
      setRootCauseData(rcRes || {});
      setRecommendations(recRes || []);
      setChannels(chRes || []);
      setDiscountData(discRes || {});
    } catch (err) {
      console.error('Error fetching sales intelligence data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  const handleSimulateNextDay = async () => {
    setIsSimulating(true);
    try {
      const updateRes = await reportApi.triggerDailyUpdate({});
      if (updateRes && updateRes.date) {
        await fetchAllData(updateRes.date);
      } else {
        await fetchAllData();
      }
    } catch (err) {
      console.error('Failed to trigger daily simulation:', err);
    } finally {
      setIsSimulating(false);
    }
  };

  const comps = todayKpis.comparisons || {};

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        dateStr={todayKpis.date}
        onSimulateNextDay={handleSimulateNextDay}
        isSimulating={isSimulating}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {loading ? (
          <div className="h-96 flex flex-col items-center justify-center gap-3">
            <RefreshCw className="w-8 h-8 text-blue-500 animate-spin" />
            <p className="text-sm font-semibold text-slate-400">Loading AI Sales Intelligence Engine...</p>
          </div>
        ) : (
          <>
            {/* TAB 1: EXECUTIVE OVERVIEW */}
            {activeTab === 'overview' && (
              <div className="space-y-8 animate-fadeIn">
                {/* Top KPI Cards Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                  <KPICard
                    type="revenue"
                    title="Daily Revenue"
                    value={todayKpis.revenue || 0}
                    prefix="Rs. "
                    changePct={comps.revenue_dod_pct}
                    subtext={`WoW: ${comps.revenue_wow_pct >= 0 ? '+' : ''}${comps.revenue_wow_pct || 0}%`}
                  />
                  <KPICard
                    type="profit"
                    title="Net Profit"
                    value={todayKpis.profit || 0}
                    prefix="Rs. "
                    changePct={comps.profit_dod_pct}
                    subtext={`WoW: ${comps.profit_wow_pct >= 0 ? '+' : ''}${comps.profit_wow_pct || 0}%`}
                  />
                  <KPICard
                    type="margin"
                    title="Profit Margin"
                    value={todayKpis.profit_margin || 0}
                    suffix="%"
                    subtext="Benchmark: >15.0%"
                  />
                  <KPICard
                    type="orders"
                    title="Total Orders"
                    value={todayKpis.total_orders || 0}
                    subtext={`AOV: Rs. ${Math.round(todayKpis.average_order_value || 0).toLocaleString()}`}
                  />
                </div>

                {/* Trend Chart Component */}
                <TrendChart trends={trends} />

                {/* Grid split: Alert Feed & Top Products Quick Summary */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  <AlertFeed alerts={alerts} />
                  
                  {/* Quick Highlight Box */}
                  <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col justify-between">
                    <div>
                      <span className="text-xs font-semibold uppercase tracking-wider text-blue-400">Today's Executive Highlight</span>
                      <h3 className="text-xl font-bold text-white mt-2 leading-snug">
                        {report.headline || 'Sales Update'}
                      </h3>
                      <p className="text-xs text-slate-300 mt-3 leading-relaxed">
                        {report.executive_summary}
                      </p>
                    </div>

                    <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between">
                      <span className="text-xs text-slate-400 font-medium">Investigate Root Cause & Actions</span>
                      <button
                        onClick={() => setActiveTab('rootcause')}
                        className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition-all"
                      >
                        Root-Cause Diagnosis →
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 2: ROOT-CAUSE & MANAGER ACTIONS */}
            {activeTab === 'rootcause' && (
              <RootCauseView rootCauseData={rootCauseData} recommendations={recommendations} />
            )}

            {/* TAB 3: CHANNELS & DISCOUNTS */}
            {activeTab === 'channels' && (
              <ChannelDiscountView channels={channels} discountData={discountData} />
            )}

            {/* TAB 4: AI DAILY NEWSPAPER */}
            {activeTab === 'newspaper' && (
              <div className="animate-fadeIn">
                <NewspaperView reportData={report} dateStr={todayKpis.date} />
              </div>
            )}

            {/* TAB 5: PRODUCTS & CATEGORIES */}
            {activeTab === 'products' && (
              <div className="animate-fadeIn">
                <ProductChart productData={productData} />
              </div>
            )}

            {/* TAB 6: REGIONAL INTELLIGENCE */}
            {activeTab === 'regions' && (
              <div className="animate-fadeIn">
                <RegionalChart regionalData={regionalData} />
              </div>
            )}

            {/* TAB 7: ALERT FEED */}
            {activeTab === 'alerts' && (
              <div className="max-w-4xl mx-auto animate-fadeIn">
                <AlertFeed alerts={alerts} />
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
