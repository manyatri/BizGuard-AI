'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api-client';
import { formatDate, getStatusColor } from '@/lib/utils';
import FashionLoader from '@/components/ui/FashionLoader';
import EmptyState from '@/components/ui/EmptyState';
import { RefreshCw, CheckCircle, XCircle, AlertCircle, Circle, GitBranch } from 'lucide-react';

const STEPS = [
  { key: 'ORDER_PLACED', label: 'Order Placed', step: 1 },
  { key: 'PAYMENT_CAPTURED', label: 'Payment', step: 2 },
  { key: 'INVENTORY_ALLOCATED', label: 'Inventory', step: 3 },
  { key: 'INVOICE_GENERATED', label: 'Invoice', step: 4 },
  { key: 'SHIPPED', label: 'Shipped', step: 5 },
  { key: 'DELIVERED', label: 'Delivered', step: 6 },
];

function StepNode({ event, stepDef }: { event: any | undefined; stepDef: typeof STEPS[0] }) {
  const status = event?.status;
  let Icon = Circle;
  let color = 'text-[#D1D5DB]';

  if (!event) { Icon = Circle; color = 'text-[#D1D5DB]'; }
  else if (status === 'SUCCESS') { Icon = CheckCircle; color = 'text-[#059669]'; }
  else if (status === 'FAILED') { Icon = XCircle; color = 'text-[#9D435F]'; }
  else if (status === 'INVARIANT_BREACH') { Icon = AlertCircle; color = 'text-[#9D435F]'; }
  else { Icon = Circle; color = 'text-[#C5A55A]'; }

  return (
    <div className="flex flex-col items-center gap-1 min-w-[80px]">
      <Icon className={`w-5 h-5 ${color}`} />
      <span className="text-[11px] text-center text-[#4B5563] font-semibold">{stepDef.label}</span>
      {event && <span className="text-[10px] text-[#8C95A0] font-mono">{formatDate(event.created_at)}</span>}
    </div>
  );
}

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [selected, setSelected] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true); setError(null);
    try {
      const d = await api.getWorkflows().catch(() => []);
      const wfs = Array.isArray(d) ? d : (d?.executions || []);
      setWorkflows(wfs);
      if (wfs.length > 0 && !selected) setSelected(wfs[0]);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchData(); }, []);

  const eventMap: Record<string, any> = {};
  if (selected?.events) {
    for (const e of selected.events) eventMap[e.event_name] = e;
  }

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
            <h1 className="text-xl lg:text-2xl font-bold tracking-tight text-[#383638]">Workflow Monitor</h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-[#E4EFF8] text-[#1E40AF] border border-[#9BB7D4]">
              State Machine
            </span>
          </div>
          <p className="text-xs text-[#71717A] mt-1">
            Real-time step execution tracking, state transitions, and automatic stalling upon invariant breaches.
          </p>
        </div>
        <button
          onClick={fetchData}
          className="flex items-center gap-1.5 px-3.5 py-2 border border-[#E7E8EB] bg-[#FCFBF8] text-[#383638] rounded-xl text-xs font-bold hover:border-[#C5A55A] shadow-xs transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Refresh
        </button>
      </div>

      {error && <p className="text-xs text-[#9D435F]">{error}</p>}

      {!loading && !error && (
        <div className="flex flex-col lg:flex-row gap-6">
          {/* List */}
          <div className="w-full lg:w-80 shrink-0">
            <div className="bg-[#FCFBF8] rounded-2xl border border-[#E7E8EB] overflow-hidden shadow-xs">
              <div className="px-4 py-3 border-b border-[#E7E8EB] bg-[#FAF5EF] text-xs font-bold uppercase tracking-wider text-[#383638]">
                {workflows.length} Execution Instances
              </div>
              <ul className="divide-y divide-[#F3F4F6] max-h-[600px] overflow-y-auto">
                {workflows.length === 0 && (
                  <li className="px-4 py-6 text-center text-xs text-[#8C95A0]">No workflows recorded</li>
                )}
                {workflows.map((wf: any) => (
                  <li
                    key={wf.id}
                    onClick={() => setSelected(wf)}
                    className={`px-4 py-3 cursor-pointer hover:bg-[#FAF5EF] transition-colors ${
                      selected?.id === wf.id ? 'bg-[#F8E5E9] border-l-3 border-[#C5A55A]' : ''
                    }`}
                  >
                    <div className="text-xs font-mono font-bold text-[#383638]">{wf.correlation_id}</div>
                    <div className="text-[11px] text-[#71717A] mt-0.5">{wf.workflow_name}</div>
                    <div className="mt-1.5">
                      <span className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-semibold border ${getStatusColor(wf.status)}`}>
                        {wf.status}
                      </span>
                    </div>
                    <div className="text-[10px] text-[#8C95A0] mt-1 font-mono">{formatDate(wf.started_at)}</div>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Detail */}
          {selected ? (
            <div className="flex-1 space-y-4">
              {selected.status === 'STALLED_INCONSISTENT' && (
                <div className="bg-[#F8E5E9] border border-[#D9A9B5] rounded-2xl p-4.5 flex items-start gap-3 shadow-xs">
                  <AlertCircle className="w-5 h-5 text-[#9D435F] mt-0.5 shrink-0" />
                  <div>
                    <div className="font-bold text-xs text-[#9D435F]">Workflow Stalled — Invariant Breach Detected</div>
                    <div className="text-xs text-[#832B45] mt-1 leading-relaxed">
                      A business rule inconsistency halted this order state machine to prevent downstream corruption.
                      Visit <Link href="/bugs" className="underline font-bold text-[#9D435F]">Bug Detection</Link> to view root cause analysis.
                    </div>
                  </div>
                </div>
              )}

              <div className="bg-[#FCFBF8] rounded-2xl border border-[#E7E8EB] p-6 shadow-xs">
                <div className="flex justify-between items-start mb-6 pb-4 border-b border-[#F8F5EF]">
                  <div>
                    <div className="text-sm font-bold text-[#383638]">{selected.workflow_name}</div>
                    <div className="text-xs font-mono text-[#8C95A0] mt-0.5">{selected.correlation_id}</div>
                  </div>
                  <span className={`inline-flex px-2.5 py-1 rounded-full text-xs font-semibold border ${getStatusColor(selected.status)}`}>
                    {selected.status}
                  </span>
                </div>

                {/* Step flow */}
                <div className="flex items-start gap-2 overflow-x-auto pb-4">
                  {STEPS.map((stepDef, idx) => {
                    const ev = eventMap[stepDef.key];
                    return (
                      <div key={stepDef.key} className="flex items-center">
                        <StepNode event={ev} stepDef={stepDef} />
                        {idx < STEPS.length - 1 && (
                          <div className={`w-8 h-0.5 mx-1 ${ev?.status === 'SUCCESS' ? 'bg-[#8BA888]' : 'bg-[#E7E8EB]'}`} />
                        )}
                      </div>
                    );
                  })}
                  {/* Invariant Breach step if stalled */}
                  {eventMap['INVARIANT_BREACH'] && (
                    <div className="flex items-center">
                      <div className="w-8 h-0.5 bg-[#D9A9B5] mx-1" />
                      <div className="flex flex-col items-center gap-1 min-w-[90px]">
                        <AlertCircle className="w-5 h-5 text-[#9D435F]" />
                        <span className="text-[10px] text-center text-[#9D435F] font-bold uppercase">Breach Block</span>
                        <span className="text-[10px] text-[#8C95A0] font-mono">{formatDate(eventMap['INVARIANT_BREACH']?.created_at)}</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Event log */}
              <div className="bg-[#FCFBF8] rounded-2xl border border-[#E7E8EB] overflow-hidden shadow-xs">
                <div className="px-5 py-3 border-b border-[#E7E8EB] bg-[#FAF5EF] text-xs font-bold uppercase tracking-wider text-[#383638]">
                  State Transition Audit Log
                </div>
                <div className="divide-y divide-[#F3F4F6]">
                  {(selected.events || []).length === 0 && (
                    <div className="px-5 py-6 text-center text-xs text-[#8C95A0]">No events recorded</div>
                  )}
                  {(selected.events || []).map((e: any) => (
                    <div key={e.id} className={`px-5 py-3 ${e.status === 'INVARIANT_BREACH' ? 'bg-[#F8E5E9]/50' : e.status === 'FAILED' ? 'bg-[#F8E5E9]/50' : 'hover:bg-[#FAF5EF]'}`}>
                      <div className="flex justify-between items-center">
                        <div className="flex items-center gap-2">
                          <span className={`text-xs font-mono font-bold ${
                            e.status === 'SUCCESS' ? 'text-[#065F46]' :
                            e.status === 'INVARIANT_BREACH' || e.status === 'FAILED' ? 'text-[#9D435F]' :
                            'text-[#1E40AF]'
                          }`}>
                            [{e.step_number}] {e.event_name}
                          </span>
                          <span className={`inline-flex px-2 py-0.5 rounded text-[10px] font-semibold border ${getStatusColor(e.status)}`}>
                            {e.status}
                          </span>
                        </div>
                        <span className="text-[10px] text-[#8C95A0] font-mono">{formatDate(e.created_at)}</span>
                      </div>
                      {e.error_message && <div className="text-xs text-[#9D435F] mt-1 font-mono font-medium">{e.error_message}</div>}
                      {e.event_payload && Object.keys(e.event_payload).length > 0 && (
                        <div className="text-[11px] text-[#383638] mt-1.5 font-mono bg-[#FAF5EF] border border-[#E7E8EB] rounded-xl p-2.5 overflow-x-auto">
                          {JSON.stringify(e.event_payload, null, 2)}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1">
              <EmptyState
                type="no-workflows"
                title="Select a Workflow to Inspect"
                description="Choose an order execution instance from the left sidebar to trace state machine events."
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
