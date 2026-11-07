'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api-client';
import { formatDate, getStatusColor, getSeverityColor } from '@/lib/utils';
import FashionLoader from '@/components/ui/FashionLoader';
import EmptyState from '@/components/ui/EmptyState';
import {
  Bug, Zap, RotateCcw, Search, AlertTriangle, ChevronDown, ChevronUp,
  Cpu, Activity, CheckCircle2, RefreshCw, Radio, ArrowRight, ShieldAlert, Sparkles
} from 'lucide-react';

export default function BugsPage() {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [scenarios, setScenarios] = useState<any[]>([]);
  const [simStatus, setSimStatus] = useState<any>(null);
  const [scanResult, setScanResult] = useState<any>(null);
  const [injectResult, setInjectResult] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [injectingKey, setInjectingKey] = useState<string | null>(null);
  const [resetting, setResetting] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [filterCategory, setFilterCategory] = useState<string>('ALL');
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true); setError(null);
    try {
      const [inc, sim, scen] = await Promise.all([
        api.getIncidents().catch(err => {
          console.warn('Failed to fetch incidents:', err);
          return { incidents: [] };
        }),
        api.getSimulationStatus().catch(err => {
          console.warn('Failed to fetch simulation status:', err);
          return { bug_injected: false, stalled_orders: 0 };
        }),
        api.getScenarios().catch(err => {
          console.warn('Failed to fetch scenarios:', err);
          return { scenarios: [] };
        }),
      ]);
      setIncidents(inc?.incidents || []);
      setSimStatus(sim);
      setScenarios(scen?.scenarios || []);
    } catch (e: any) {
      setError(e.message || 'Unable to connect to simulation engine.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const handleScan = async () => {
    setScanning(true); setScanResult(null); setError(null);
    try {
      const r = await api.detectBugs();
      setScanResult(r);
      await fetchData();
    } catch (e: any) { setError(e.message); }
    finally { setScanning(false); }
  };

  const handleInjectScenario = async (key: string) => {
    setInjectingKey(key); setInjectResult(null); setError(null);
    try {
      const res = await api.injectScenario(key);
      setInjectResult(res);
      // Auto-trigger invariant scan after injection
      await api.detectBugs();
      await fetchData();
    } catch (e: any) { setError(e.message); }
    finally { setInjectingKey(null); }
  };

  const handleReset = async () => {
    if (!confirm('Reset all simulation state? This deletes incidents and restores inventory reservations.')) return;
    setResetting(true); setError(null);
    try {
      await api.resetSimulation();
      setScanResult(null);
      setInjectResult(null);
      await fetchData();
    } catch (e: any) { setError(e.message); }
    finally { setResetting(false); }
  };

  const filteredScenarios = scenarios.filter(s => filterCategory === 'ALL' || s.category === filterCategory);

  if (loading) {
    return (
      <div className="p-8 max-w-7xl mx-auto flex items-center justify-center min-h-[500px]">
        <FashionLoader messageIndex={1} />
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-[#E7E8EB]">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl lg:text-2xl font-bold tracking-tight text-[#383638]">
              Bug Detection & Failure Simulator
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-[#F8E5E9] text-[#9D435F] border border-[#D9A9B5]">
              Simulator Ready
            </span>
          </div>
          <p className="text-xs text-[#71717A] mt-1">
            Deterministic business anomaly injection, invariant state checking, and autonomous multi-agent alerting.
          </p>
        </div>

        <div className="flex items-center gap-2.5 flex-wrap">
          <button
            onClick={handleScan}
            disabled={scanning}
            className="flex items-center gap-2 px-4 py-2 bg-[#383638] text-white rounded-xl text-xs font-semibold hover:bg-black disabled:opacity-50 transition-colors shadow-xs"
          >
            <Search className={`w-3.5 h-3.5 text-[#C5A55A] ${scanning ? 'animate-spin' : ''}`} />
            {scanning ? 'Auditing Invariants...' : 'Run Invariant Audit'}
          </button>

          <button
            onClick={handleReset}
            disabled={resetting}
            className="flex items-center gap-2 px-3.5 py-2 border border-[#E7E8EB] bg-[#FCFBF8] text-[#383638] rounded-xl text-xs font-semibold hover:border-[#C5A55A] disabled:opacity-50 transition-colors shadow-xs"
          >
            <RotateCcw className={`w-3.5 h-3.5 ${resetting ? 'animate-spin' : ''}`} />
            {resetting ? 'Resetting...' : 'Reset State'}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-[#F8E5E9] border border-[#D9A9B5] rounded-2xl px-5 py-3.5 text-[#9D435F] text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={fetchData} className="underline font-bold text-xs ml-4">Retry</button>
        </div>
      )}

      {/* Injection notice banner */}
      {injectResult && (
        <div className="bg-[#E8EFE5] border border-[#8BA888] rounded-2xl px-5 py-3.5 text-[#065F46] text-xs flex items-center justify-between shadow-xs">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-[#059669]" />
            <span>
              Injected failure scenario: <strong>{injectResult.scenario_label}</strong> ({injectResult.affected_rule}).
              Invariant scan executed automatically!
            </span>
          </div>
          <button onClick={() => setInjectResult(null)} className="text-[#059669] text-xs font-bold hover:underline">
            Dismiss
          </button>
        </div>
      )}

      {/* Failure Scenario Injection Panel */}
      <div className="bg-[#FCFBF8] border border-[#E7E8EB] rounded-2xl p-6 shadow-xs">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
          <div>
            <h2 className="text-xs font-bold text-[#383638] uppercase tracking-wider flex items-center gap-2">
              <Zap className="w-4 h-4 text-[#C5A55A]" />
              Controlled Failure Injection Suite
            </h2>
            <p className="text-[11px] text-[#71717A] mt-0.5">
              Inject real corrupted database states to test detection rules and self-healing agent pipelines.
            </p>
          </div>

          <div className="flex items-center gap-1 bg-[#FAF5EF] p-1 rounded-xl text-xs font-medium text-[#71717A] border border-[#E7E8EB]">
            {['ALL', 'BUSINESS', 'TECHNICAL', 'WORKFLOW'].map(cat => (
              <button
                key={cat}
                onClick={() => setFilterCategory(cat)}
                className={`px-3 py-1 rounded-lg transition-all text-[11px] ${
                  filterCategory === cat
                    ? 'bg-[#FCFBF8] text-[#383638] shadow-xs font-bold border border-[#E7E8EB]'
                    : 'hover:text-[#383638]'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredScenarios.map(s => {
            const isInjecting = injectingKey === s.key;
            return (
              <div
                key={s.key}
                className="border border-[#E7E8EB] rounded-2xl p-4.5 hover:border-[#C5A55A] transition-all flex flex-col justify-between bg-[#FAF5EF]/50 shadow-2xs"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider border ${
                      s.category === 'BUSINESS' ? 'bg-[#F8E5E9] text-[#9D435F] border-[#D9A9B5]' :
                      s.category === 'TECHNICAL' ? 'bg-[#E4EFF8] text-[#1E40AF] border-[#9BB7D4]' :
                      'bg-[#FAF5EF] text-[#8A7338] border-[#E9D8B5]'
                    }`}>
                      {s.category}
                    </span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                      s.severity === 'CRITICAL' ? 'bg-[#F8E5E9] text-[#9D435F] border-[#D9A9B5]' : 'bg-[#FAF5EF] text-[#8A7338] border-[#E9D8B5]'
                    }`}>
                      {s.severity}
                    </span>
                  </div>

                  <h3 className="text-xs font-bold text-[#383638] mb-1">{s.label}</h3>
                  <p className="text-[11px] text-[#71717A] leading-relaxed mb-3">{s.description}</p>
                </div>

                <div className="pt-2.5 border-t border-[#E7E8EB] flex items-center justify-between">
                  <span className="text-[10px] font-mono text-[#8C95A0] truncate max-w-[150px]">
                    {s.affected_rule}
                  </span>
                  <button
                    onClick={() => handleInjectScenario(s.key)}
                    disabled={isInjecting}
                    className="px-3 py-1.5 bg-[#383638] hover:bg-black text-white text-[11px] font-bold rounded-xl disabled:opacity-50 flex items-center gap-1.5 transition-colors shadow-xs"
                  >
                    <Zap className={`w-3 h-3 ${isInjecting ? 'animate-bounce text-[#C5A55A]' : 'text-[#C5A55A]'}`} />
                    {isInjecting ? 'Injecting...' : 'Inject Bug'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Incidents Table */}
      <div className="bg-[#FCFBF8] border border-[#E7E8EB] rounded-2xl overflow-hidden shadow-xs">
        <div className="p-6 border-b border-[#E7E8EB] bg-[#FAF5EF] flex justify-between items-center">
          <div>
            <h2 className="text-xs font-bold text-[#383638] uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4 text-[#C5A55A]" />
              Detected Business Invariant Breaches ({incidents.length})
            </h2>
            <p className="text-[11px] text-[#71717A] mt-0.5">Real-time state violations flagged by rule-based invariant checks.</p>
          </div>
          <button
            onClick={fetchData}
            className="p-1.5 text-[#71717A] hover:text-[#383638] rounded-xl border border-[#E7E8EB] bg-[#FCFBF8] hover:bg-[#FAF5EF] transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>

        {incidents.length === 0 ? (
          <div className="p-8">
            <EmptyState
              type="no-incidents"
              title="All Business Invariants in Harmony"
              description="Zero anomalies or state drift detected. All orders, inventory reservations, and payment syncs are running flawlessly. Use the simulator above to inject a scenario."
              className="border-0 shadow-none bg-transparent"
            />
          </div>
        ) : (
          <div className="divide-y divide-[#F3F4F6]">
            {incidents.map((inc) => {
              const isExpanded = expanded === inc.id;
              return (
                <div key={inc.id} className="p-5 hover:bg-[#FAF5EF]/60 transition-colors">
                  <div
                    className="flex items-center justify-between cursor-pointer"
                    onClick={() => setExpanded(isExpanded ? null : inc.id)}
                  >
                    <div className="flex items-center gap-4">
                      <span className={`text-[10px] px-2.5 py-1 rounded-full font-bold uppercase border ${
                        inc.severity === 'CRITICAL' ? 'bg-[#F8E5E9] text-[#9D435F] border-[#D9A9B5]' : 'bg-[#FAF5EF] text-[#8A7338] border-[#E9D8B5]'
                      }`}>
                        {inc.severity}
                      </span>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs font-bold text-[#8C95A0]">{inc.incident_code}</span>
                          <h3 className="font-bold text-xs text-[#383638]">{inc.title}</h3>
                        </div>
                        <p className="text-[11px] text-[#71717A] mt-0.5">
                          Detected via <span className="font-mono text-[#383638]">{inc.detection_rule}</span> • {formatDate(inc.detected_at)}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <span className={`text-xs px-2.5 py-1 rounded-full font-semibold border ${getStatusColor(inc.status)}`}>
                        {inc.status}
                      </span>
                      {isExpanded ? <ChevronUp className="w-4 h-4 text-[#8C95A0]" /> : <ChevronDown className="w-4 h-4 text-[#8C95A0]" />}
                    </div>
                  </div>

                  {isExpanded && (
                    <div className="mt-4 pt-4 border-t border-[#E7E8EB] grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                      <div>
                        <h4 className="font-bold text-[#383638] mb-1">Root Cause Summary</h4>
                        <p className="text-[#383638] bg-[#FAF5EF] p-3 rounded-xl border border-[#E7E8EB] leading-relaxed whitespace-pre-wrap font-sans">
                          {inc.root_cause_summary || 'Analysis pending investigation.'}
                        </p>
                      </div>
                      <div>
                        <h4 className="font-bold text-[#383638] mb-1">Blast Radius & Anomaly Details</h4>
                        <pre className="bg-[#FAF5EF] p-3 rounded-xl border border-[#E7E8EB] text-[#383638] font-mono overflow-x-auto text-[11px]">
                          {JSON.stringify(inc.blast_radius_analysis, null, 2)}
                        </pre>
                        <div className="mt-3 flex justify-end">
                          <Link
                            href="/war-room"
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-[#383638] text-white rounded-xl text-xs font-bold hover:bg-black transition-colors"
                          >
                            Open AI War Room →
                          </Link>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
