'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api-client';
import { formatDate } from '@/lib/utils';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import FashionLoader from '@/components/ui/FashionLoader';
import EmptyState from '@/components/ui/EmptyState';
import { RefreshCw, TrendingUp, Clock, CheckCircle2, AlertTriangle, BarChart3 } from 'lucide-react';

const PIE_COLORS = { HEALTHY: '#8BA888', LOW_STOCK: '#E9D8B5', OUT_OF_STOCK: '#D9A9B5' };

export default function AnalyticsPage() {
  const [metrics, setMetrics] = useState<any>(null);
  const [invHealth, setInvHealth] = useState<any>(null);
  const [incTimeline, setIncTimeline] = useState<any>(null);
  const [wfStats, setWfStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true); setError(null);
    try {
      const [m, ih, it, ws] = await Promise.all([
        api.getDashboardMetrics().catch(() => null),
        api.getInventoryHealth().catch(() => null),
        api.getIncidentTimeline(30).catch(() => ({ timeline: [] })),
        api.getWorkflowStats().catch(() => null),
      ]);
      setMetrics(m); setInvHealth(ih); setIncTimeline(it); setWfStats(ws);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchData(); }, []);

  const orderChartData = metrics ? Object.entries(metrics.orders_by_status || {}).map(([status, count]) => ({ status, count })) : [];
  const invPieData = invHealth ? [
    { name: 'Healthy', value: invHealth.summary?.healthy || 0 },
    { name: 'Low Stock', value: invHealth.summary?.low_stock || 0 },
    { name: 'Out of Stock', value: invHealth.summary?.out_of_stock || 0 },
  ].filter(d => d.value > 0) : [];
  const timelineData = incTimeline?.timeline?.map((t: any) => ({ date: t.date, incidents: t.count })) || [];

  if (loading) {
    return (
      <div className="p-8 max-w-7xl mx-auto flex items-center justify-center min-h-[500px]">
        <FashionLoader messageIndex={1} />
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-[#E7E8EB]">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl lg:text-2xl font-bold tracking-tight text-[#383638]">Reliability Analytics</h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-[#E4EFF8] text-[#1E40AF] border border-[#9BB7D4]">
              Telemetry Live
            </span>
          </div>
          <p className="text-xs text-[#71717A] mt-1">
            Mean time to detect (MTTD), resolution metrics (MTTR), catalog health distributions, and incident frequency.
          </p>
        </div>
        <button
          onClick={fetchData}
          className="flex items-center gap-1.5 px-3.5 py-2 border border-[#E7E8EB] bg-[#FCFBF8] text-[#383638] rounded-xl text-xs font-bold hover:border-[#C5A55A] shadow-xs transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Refresh
        </button>
      </div>

      {error && <p className="text-xs text-[#9D435F]">{error} <button onClick={fetchData} className="underline ml-2">Retry</button></p>}

      {!loading && !error && metrics && (
        <>
          {/* KPI Cards in Pastels */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {[
              { label: 'MTTD', value: metrics.mttd_minutes != null ? `${metrics.mttd_minutes}m` : '—', sub: 'Mean Time to Detect', icon: Clock, bg: '#E4EFF8', border: '#9BB7D4', text: '#1E40AF' },
              { label: 'MTTR', value: metrics.mttr_minutes != null ? `${metrics.mttr_minutes}m` : '—', sub: 'Mean Time to Resolve', icon: TrendingUp, bg: '#FAF5EF', border: '#E9D8B5', text: '#8A7338' },
              { label: 'Workflow Success', value: `${metrics.workflow_success_rate}%`, sub: 'of state executions completed', icon: CheckCircle2, bg: '#E8EFE5', border: '#8BA888', text: '#065F46' },
              { label: 'Active Incidents', value: metrics.active_incidents, sub: `${metrics.resolved_incidents} resolved`, icon: AlertTriangle, bg: '#F8E5E9', border: '#D9A9B5', text: '#9D435F' },
            ].map(k => (
              <div
                key={k.label}
                className="rounded-2xl p-5 border shadow-xs transition-all hover:scale-101"
                style={{ backgroundColor: k.bg, borderColor: k.border }}
              >
                <div className="flex items-center gap-2 mb-1">
                  <k.icon className="w-4 h-4" style={{ color: k.text }} />
                  <span className="text-[11px] font-bold uppercase tracking-wider" style={{ color: k.text }}>{k.label}</span>
                </div>
                <div className="text-2xl font-bold text-[#383638] mt-1 tracking-tight">{k.value}</div>
                <div className="text-[11px] text-[#71717A] mt-0.5">{k.sub}</div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* Orders by status bar */}
            <div className="bg-[#FCFBF8] rounded-2xl border border-[#E7E8EB] p-5 shadow-xs">
              <h2 className="text-xs font-bold uppercase tracking-wider text-[#383638] mb-4">Orders by Pipeline Status</h2>
              {orderChartData.length === 0 ? <p className="text-xs text-[#8C95A0] text-center py-8">No order telemetry recorded</p> : (
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={orderChartData}>
                    <XAxis dataKey="status" tick={{ fontSize: 10, fill: '#71717A' }} angle={-15} textAnchor="end" height={45} />
                    <YAxis tick={{ fontSize: 10, fill: '#71717A' }} />
                    <Tooltip contentStyle={{ backgroundColor: '#FCFBF8', borderColor: '#E7E8EB', borderRadius: 12, fontSize: 11 }} />
                    <Bar dataKey="count" fill="#E9D8B5" stroke="#C5A55A" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>

            {/* Inventory health pie in pastels */}
            <div className="bg-[#FCFBF8] rounded-2xl border border-[#E7E8EB] p-5 shadow-xs">
              <h2 className="text-xs font-bold uppercase tracking-wider text-[#383638] mb-4">Catalog Inventory Integrity</h2>
              {invPieData.length === 0 ? <p className="text-xs text-[#8C95A0] text-center py-8">No inventory data available</p> : (
                <div className="flex items-center justify-around gap-4">
                  <ResponsiveContainer width={180} height={180}>
                    <PieChart>
                      <Pie data={invPieData} cx="50%" cy="50%" innerRadius={48} outerRadius={75} dataKey="value">
                        {invPieData.map((entry: any) => (
                          <Cell key={entry.name} fill={(PIE_COLORS as any)[entry.name.replace(' ', '_')] || '#E7E8EB'} stroke="#FCFBF8" strokeWidth={2} />
                        ))}
                      </Pie>
                      <Tooltip contentStyle={{ backgroundColor: '#FCFBF8', borderColor: '#E7E8EB', borderRadius: 12, fontSize: 11 }} />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="space-y-2.5">
                    {invPieData.map((d: any) => (
                      <div key={d.name} className="flex items-center gap-2.5 text-xs">
                        <div className="w-3.5 h-3.5 rounded-full" style={{ background: (PIE_COLORS as any)[d.name.replace(' ', '_')] || '#E7E8EB' }} />
                        <span className="text-[#4B5563] font-medium">{d.name}</span>
                        <span className="font-bold text-[#383638] ml-auto">{d.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Incident timeline */}
          <div className="bg-[#FCFBF8] rounded-2xl border border-[#E7E8EB] p-5 mb-6 shadow-xs">
            <h2 className="text-xs font-bold uppercase tracking-wider text-[#383638] mb-4">Incident Frequency Trend — Last 30 Days</h2>
            {timelineData.length === 0 ? <p className="text-xs text-[#8C95A0] text-center py-8">No incident events recorded</p> : (
              <ResponsiveContainer width="100%" height={170}>
                <LineChart data={timelineData}>
                  <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#71717A' }} />
                  <YAxis tick={{ fontSize: 10, fill: '#71717A' }} allowDecimals={false} />
                  <Tooltip contentStyle={{ backgroundColor: '#FCFBF8', borderColor: '#E7E8EB', borderRadius: 12, fontSize: 11 }} />
                  <Line type="monotone" dataKey="incidents" stroke="#D9A9B5" strokeWidth={2.5} dot={{ r: 4, fill: '#C5A55A', stroke: '#FCFBF8', strokeWidth: 1.5 }} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* Workflow stats */}
          {wfStats && (
            <div className="bg-[#FCFBF8] rounded-2xl border border-[#E7E8EB] p-5 shadow-xs">
              <h2 className="text-xs font-bold uppercase tracking-wider text-[#383638] mb-3">Workflow Execution Performance</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <div className="text-xl font-bold text-[#383638]">{wfStats.total_executions}</div>
                  <div className="text-[11px] text-[#8C95A0] font-medium mt-0.5">Total Executions</div>
                </div>
                <div>
                  <div className="text-xl font-bold text-[#059669]">{wfStats.success_rate_percent}%</div>
                  <div className="text-[11px] text-[#8C95A0] font-medium mt-0.5">Success Completion</div>
                </div>
                <div>
                  <div className="text-xl font-bold text-[#383638]">{wfStats.avg_duration_seconds != null ? `${wfStats.avg_duration_seconds}s` : '—'}</div>
                  <div className="text-[11px] text-[#8C95A0] font-medium mt-0.5">Average Duration</div>
                </div>
                <div>
                  {Object.entries(wfStats.by_status || {}).map(([s, c]) => (
                    <div key={s} className="text-[11px] text-[#4B5563]">
                      {s}: <strong className="text-[#383638]">{c as any}</strong>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
