'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api-client';
import { formatDate, getStatusColor } from '@/lib/utils';
import FashionLoader from '@/components/ui/FashionLoader';
import EmptyState from '@/components/ui/EmptyState';
import { BrainCircuit, Play, Loader2, ShieldCheck, CheckCircle2, ArrowRight } from 'lucide-react';

const AGENT_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  '@monitor-agent': { bg: '#E4EFF8', text: '#1E40AF', border: '#9BB7D4' },
  '@investigator-agent': { bg: '#F8E5E9', text: '#9D435F', border: '#D9A9B5' },
  '@developer-agent': { bg: '#FAF5EF', text: '#8A7338', border: '#E9D8B5' },
  '@tester-agent': { bg: '#E8EFE5', text: '#065F46', border: '#8BA888' },
  '@auditor-agent': { bg: '#E7E8EB', text: '#383638', border: '#C5A55A' },
};

const MSG_TYPE_PASTELS: Record<string, { bg: string; border: string }> = {
  SCAN_REPORT: { bg: '#E4EFF8', border: '#9BB7D4' },
  EVIDENCE: { bg: '#F8E5E9', border: '#D9A9B5' },
  PROPOSAL_NOTICE: { bg: '#FAF5EF', border: '#E9D8B5' },
  TEST_RESULTS: { bg: '#E8EFE5', border: '#8BA888' },
  AUDIT_VERDICT: { bg: '#FCFBF8', border: '#C5A55A' },
  HYPOTHESIS: { bg: '#E4EFF8', border: '#9BB7D4' },
};

export default function WarRoomPage() {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [selectedId, setSelectedId] = useState<string>('');
  const [messages, setMessages] = useState<any[]>([]);
  const [tasks, setTasks] = useState<any[]>([]);
  const [investigating, setInvestigating] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchIncidents = async () => {
    setLoading(true); setError(null);
    try {
      const d = await api.getIncidents().catch(() => ({ incidents: [] }));
      const incs = d?.incidents || [];
      setIncidents(incs);
      if (incs.length > 0 && !selectedId) setSelectedId(incs[0].id);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  const fetchWarRoom = async (id: string) => {
    try {
      const [msgs, tsk] = await Promise.all([
        api.getWarRoomMessages(id).catch(() => ({ messages: [] })),
        api.getAgentTasks(id).catch(() => ({ tasks: [] })),
      ]);
      setMessages(msgs?.messages || []);
      setTasks(tsk?.tasks || []);
    } catch {}
  };

  useEffect(() => { fetchIncidents(); }, []);
  useEffect(() => { if (selectedId) fetchWarRoom(selectedId); }, [selectedId]);

  const handleInvestigate = async () => {
    if (!selectedId) return;
    setInvestigating(true); setError(null);
    try {
      const r = await api.triggerInvestigation(selectedId);
      setMessages(r?.messages || []);
      await fetchWarRoom(selectedId);
      await fetchIncidents();
    } catch (e: any) { setError(e.message); }
    finally { setInvestigating(false); }
  };

  const selectedIncident = incidents.find(i => i.id === selectedId);

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-[#E7E8EB]">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl lg:text-2xl font-bold tracking-tight text-[#383638]">AI Collaborative War Room</h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-[#F8E5E9] text-[#9D435F] border border-[#D9A9B5]">
              Multi-Agent Mesh
            </span>
          </div>
          <p className="text-xs text-[#71717A] mt-1">
            Autonomous 5-agent diagnosis (@monitor, @investigator, @developer, @tester, @auditor) for zero-downtime recovery.
          </p>
        </div>
      </div>

      {error && (
        <div className="bg-[#F8E5E9] border border-[#D9A9B5] rounded-2xl px-5 py-3 text-[#9D435F] text-xs">
          {error}
        </div>
      )}

      {loading && (
        <div className="py-20 flex items-center justify-center">
          <FashionLoader messageIndex={2} />
        </div>
      )}

      {!loading && incidents.length === 0 && (
        <EmptyState
          type="no-incidents"
          title="No Active Incidents for War Room"
          description="The AI agent mesh is standing by. When an invariant anomaly is detected, specialist agents collaborate here to synthesize recovery plans."
          actionText="Inject a Test Failure"
          actionHref="/bugs"
        />
      )}

      {!loading && incidents.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: selector, investigation trigger, tasks */}
          <div className="space-y-4">
            {/* Incident selector */}
            <div className="bg-[#FCFBF8] rounded-2xl border border-[#E7E8EB] p-5 shadow-xs">
              <label className="text-[10px] font-bold text-[#8C95A0] uppercase tracking-wider mb-2 block">
                Target Incident in Scope
              </label>
              <select
                value={selectedId}
                onChange={e => setSelectedId(e.target.value)}
                className="w-full border border-[#E7E8EB] rounded-xl px-3 py-2 text-xs text-[#383638] font-semibold focus:ring-1 focus:ring-[#C5A55A] focus:outline-none bg-[#FAF5EF]"
              >
                {incidents.map((inc: any) => (
                  <option key={inc.id} value={inc.id}>
                    {inc.incident_code} — {inc.severity} ({inc.status})
                  </option>
                ))}
              </select>
              {selectedIncident && (
                <div className="mt-3 text-xs text-[#383638] bg-[#FAF5EF] p-3 rounded-xl border border-[#E7E8EB]">
                  <p className="font-bold text-[#383638]">{selectedIncident.title}</p>
                  <p className="text-[#8C95A0] mt-1 font-mono text-[10px]">{selectedIncident.detection_rule}</p>
                </div>
              )}
            </div>

            {/* Investigation trigger button */}
            <button
              onClick={handleInvestigate}
              disabled={investigating}
              className="w-full flex items-center justify-center gap-2 py-3.5 bg-[#383638] hover:bg-black text-white rounded-2xl font-bold text-xs disabled:opacity-50 transition-colors shadow-sm"
            >
              {investigating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-[#C5A55A]" />
                  <span>5-Agent Diagnostic Mesh Operating...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 text-[#C5A55A]" />
                  <span>Trigger 5-Agent Investigation</span>
                </>
              )}
            </button>

            {/* Agent tasks list */}
            {tasks.length > 0 && (
              <div className="bg-[#FCFBF8] rounded-2xl border border-[#E7E8EB] overflow-hidden shadow-xs">
                <div className="px-5 py-3 border-b border-[#E7E8EB] text-[10px] font-bold text-[#383638] uppercase tracking-wider bg-[#FAF5EF]">
                  Agent Tasks & Specializations ({tasks.length})
                </div>
                <div className="divide-y divide-[#F3F4F6] max-h-64 overflow-y-auto">
                  {tasks.map((t: any) => (
                    <div key={t.id} className="px-4 py-3 flex items-center justify-between text-xs">
                      <div>
                        <span className="font-bold text-[#383638] block">{t.agent_role}</span>
                        <span className="text-[10px] text-[#8C95A0] truncate max-w-[180px] block font-mono">{t.prompt_spec}</span>
                      </div>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getStatusColor(t.status)}`}>
                        {t.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recovery Ready CTA */}
            {messages.length > 0 && selectedId && (
              <div className="bg-[#E8EFE5] rounded-2xl border border-[#8BA888] p-4.5 shadow-xs text-xs">
                <div className="flex items-center gap-2 font-bold text-[#065F46] mb-1">
                  <ShieldCheck className="w-4 h-4 text-[#059669]" />
                  Recovery Proposal Synthesized
                </div>
                <p className="text-[#245229] mb-3 text-[11px] leading-relaxed">
                  Specialist agents verified root cause and compiled cryptographically locked recovery action.
                </p>
                <Link
                  href="/approvals"
                  className="block text-center w-full py-2.5 bg-[#065F46] text-white rounded-xl font-bold text-xs hover:bg-[#047857] transition-colors shadow-xs"
                >
                  Review in Approval Center →
                </Link>
              </div>
            )}
          </div>

          {/* Right Column: Multi-Agent Message Feed */}
          <div className="lg:col-span-2">
            <div className="bg-[#FCFBF8] rounded-2xl border border-[#E7E8EB] overflow-hidden shadow-xs flex flex-col h-[650px]">
              <div className="px-5 py-3 border-b border-[#E7E8EB] flex justify-between items-center bg-[#FAF5EF]">
                <span className="font-bold text-xs uppercase tracking-wider text-[#383638]">Agent Swarm Communication Stream</span>
                <span className="text-xs text-[#8C95A0] font-medium">{messages.length} messages</span>
              </div>

              <div className="flex-1 divide-y divide-[#F3F4F6] overflow-y-auto p-4 space-y-3.5 bg-[#FAF5EF]/30">
                {messages.length === 0 && (
                  <div className="py-24 text-center text-[#8C95A0]">
                    <BrainCircuit className="w-12 h-12 mx-auto mb-2 text-[#C5A55A]" />
                    <p className="text-xs font-bold text-[#383638]">War room awaiting investigation launch</p>
                    <p className="text-[11px] text-[#8C95A0] mt-1">Click &quot;Trigger 5-Agent Investigation&quot; to coordinate agent specialists.</p>
                  </div>
                )}

                {messages.map((msg: any) => {
                  const agentStyle = AGENT_COLORS[msg.sender_agent] || { bg: '#FCFBF8', text: '#383638', border: '#E7E8EB' };
                  const msgStyle = MSG_TYPE_PASTELS[msg.message_type] || { bg: '#FCFBF8', border: '#E7E8EB' };

                  return (
                    <div
                      key={msg.id}
                      className="p-4 rounded-2xl border transition-all shadow-xs"
                      style={{ backgroundColor: msgStyle.bg, borderColor: msgStyle.border }}
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <span
                          className="inline-flex px-2.5 py-0.5 rounded-full text-[11px] font-bold border"
                          style={{
                            backgroundColor: agentStyle.bg,
                            color: agentStyle.text,
                            borderColor: agentStyle.border,
                          }}
                        >
                          {msg.sender_agent}
                        </span>
                        <span className="text-[10px] font-bold text-[#8C95A0] uppercase tracking-wider">
                          {msg.message_type}
                        </span>
                        <span className="ml-auto text-[10px] text-[#8C95A0] font-mono">
                          {formatDate(msg.created_at)}
                        </span>
                      </div>
                      <div className="text-xs text-[#383638] whitespace-pre-wrap leading-relaxed font-sans">
                        {msg.content}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
