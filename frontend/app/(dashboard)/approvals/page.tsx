'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api-client';
import { formatDate, getStatusColor, getSeverityColor } from '@/lib/utils';
import FashionLoader from '@/components/ui/FashionLoader';
import EmptyState from '@/components/ui/EmptyState';
import {
  CheckSquare, RefreshCw, ChevronDown, ChevronUp, ShieldCheck, ShieldX,
  AlertTriangle, ArrowRight, Zap, CheckCircle2, Lock, History, Scale
} from 'lucide-react';

export default function ApprovalsPage() {
  const [pending, setPending] = useState<any[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [deciding, setDeciding] = useState<string | null>(null);
  const [approver, setApprover] = useState('manager@fashionretail.com');
  const [comment, setComment] = useState('');
  const [executing, setExecuting] = useState<string | null>(null);
  const [preChecking, setPreChecking] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true); setError(null);
    try {
      const [p, h] = await Promise.all([
        api.getPendingApprovals().catch(() => ({ proposals: [] })),
        api.getApprovalHistory().catch(() => ({ approvals: [] })),
      ]);
      setPending(p?.proposals || []);
      setHistory(h?.approvals || []);
      if (p?.proposals?.length > 0 && !expanded) {
        setExpanded(p.proposals[0].id);
      }
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchData(); }, []);

  const handleDecide = async (proposalId: string, decision: 'APPROVED' | 'REJECTED') => {
    if (!approver.trim()) { setError('Please enter a manager name or email'); return; }
    setDeciding(proposalId); setError(null); setSuccessMsg(null);
    try {
      await api.decideApproval(proposalId, { decision, approver_user: approver, comments: comment });
      setDeciding(null); setComment('');
      setSuccessMsg(`Proposal marked as ${decision}. Audit record cryptographically hashed with SHA-256.`);
      await fetchData();
    } catch (e: any) {
      setError(e.message);
      setDeciding(null);
    }
  };

  const handlePreCheck = async (proposalId: string) => {
    setPreChecking(proposalId); setError(null); setSuccessMsg(null);
    try {
      await api.runPreChecks(proposalId);
      setSuccessMsg('Automated pre-check tests verified successfully!');
      await fetchData();
    } catch (e: any) { setError(e.message); }
    finally { setPreChecking(null); }
  };

  const handleExecute = async (proposalId: string) => {
    if (!confirm('Execute authorized recovery? This will perform an atomic database inventory swap and resume order fulfillment.')) return;
    setExecuting(proposalId); setError(null); setSuccessMsg(null);
    try {
      const res = await api.executeProposal(proposalId, approver);
      setExecuting(null);
      setSuccessMsg(`Recovery executed successfully! Order ${res.order_number} advanced to INVOICED. Incident VERIFIED_RESOLVED.`);
      await fetchData();
    } catch (e: any) {
      setError(e.message);
      setExecuting(null);
    }
  };

  if (loading) {
    return (
      <div className="p-8 max-w-7xl mx-auto flex items-center justify-center min-h-[500px]">
        <FashionLoader messageIndex={2} />
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-[#E7E8EB]">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl lg:text-2xl font-bold tracking-tight text-[#383638]">Human Approval Center</h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-[#FAF5EF] text-[#8A7338] border border-[#E9D8B5]">
              Safety Gate Active
            </span>
          </div>
          <p className="text-xs text-[#71717A] mt-1">
            Supervise autonomous recovery actions. All proposals require human authorization and pass automated pre-checks.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchData}
            className="flex items-center gap-1.5 px-3.5 py-2 border border-[#E7E8EB] bg-[#FCFBF8] text-[#383638] rounded-xl text-xs font-bold hover:border-[#C5A55A] shadow-xs transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-[#F8E5E9] border border-[#D9A9B5] rounded-2xl px-5 py-3 text-[#9D435F] text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {successMsg && (
        <div className="bg-[#E8EFE5] border border-[#8BA888] rounded-2xl px-5 py-3.5 text-[#065F46] text-xs flex items-center justify-between shadow-xs">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-[#059669] shrink-0" />
            <span>{successMsg}</span>
          </div>
          <button onClick={() => setSuccessMsg(null)} className="text-[#059669] text-xs font-bold hover:underline">Dismiss</button>
        </div>
      )}

      {/* Supervisor Identity Card */}
      <div className="bg-[#FCFBF8] border border-[#E7E8EB] rounded-2xl p-4 shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-[#FAF5EF] border border-[#E9D8B5] rounded-xl">
            <Lock className="w-4 h-4 text-[#C5A55A]" />
          </div>
          <div>
            <span className="text-xs font-bold text-[#383638] block">Supervisor Signature Binding</span>
            <span className="text-[11px] text-[#71717A]">Approvals are cryptographically bound to your identity and signed with SHA-256.</span>
          </div>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <input
            value={approver}
            onChange={e => setApprover(e.target.value)}
            className="border border-[#E7E8EB] rounded-xl px-3 py-1.5 text-xs text-[#383638] font-semibold focus:ring-1 focus:ring-[#C5A55A] focus:outline-none w-full sm:w-64 bg-[#FAF5EF]"
            placeholder="manager@fashionretail.com"
          />
        </div>
      </div>

      {/* Main Grid: Pending Approvals & History */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Pending Proposals Column (Span 2) */}
        <div className="xl:col-span-2 space-y-4">
          <h2 className="text-xs font-bold text-[#383638] uppercase tracking-wider flex items-center justify-between">
            <span>Proposals Awaiting Review ({pending.length})</span>
            <span className="text-[11px] font-normal text-[#8C95A0]">Strict Safety Enforcement</span>
          </h2>

          {pending.length === 0 && (
            <EmptyState
              type="no-approvals"
              title="All Approvals Cleared"
              description="No autonomous proposals require supervisor intervention right now. All orders are flowing smoothly through the fulfillment pipeline."
            />
          )}

          {pending.map((p: any) => {
            const isExpanded = expanded === p.id;
            const checksPassed = p.pre_check_test_results?.all_passed;

            return (
              <div key={p.id} className="bg-[#FCFBF8] border border-[#E7E8EB] rounded-2xl overflow-hidden shadow-xs">
                {/* Header */}
                <div className="p-5 border-b border-[#E7E8EB] bg-[#FAF5EF]">
                  <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold bg-[#383638] text-white px-2.5 py-0.5 rounded-lg">
                          {p.proposal_code}
                        </span>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase border ${
                          p.risk_level === 'LOW' ? 'bg-[#E8EFE5] text-[#065F46] border-[#8BA888]' : 'bg-[#F8E5E9] text-[#9D435F] border-[#D9A9B5]'
                        }`}>
                          {p.risk_level} RISK
                        </span>
                        <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${getStatusColor(p.status)}`}>
                          {p.status}
                        </span>
                      </div>
                      <h3 className="text-sm font-bold text-[#383638] mt-2">{p.title}</h3>
                    </div>

                    <button
                      onClick={() => setExpanded(isExpanded ? null : p.id)}
                      className="text-xs text-[#71717A] hover:text-[#383638] flex items-center gap-1 font-semibold"
                    >
                      {isExpanded ? 'Collapse Analysis' : 'Expand Full Analysis'}
                      {isExpanded ? <ChevronUp className="w-4 h-4 text-[#8C95A0]" /> : <ChevronDown className="w-4 h-4 text-[#8C95A0]" />}
                    </button>
                  </div>

                  {p.incident_code && (
                    <div className="mt-2 text-xs text-[#71717A] flex items-center gap-2">
                      <span>Linked Incident: <strong className="font-mono text-[#383638]">{p.incident_code}</strong></span>
                      <span>•</span>
                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${getSeverityColor(p.incident_severity || '')}`}>
                        {p.incident_severity}
                      </span>
                      <span>•</span>
                      <span>Created {formatDate(p.created_at)}</span>
                    </div>
                  )}
                </div>

                {/* Body Content */}
                <div className="p-5 space-y-5">
                  <p className="text-xs text-[#4B5563] leading-relaxed bg-[#FAF5EF] p-3.5 rounded-2xl border border-[#E7E8EB]">
                    {p.description}
                  </p>

                  {/* Before & After Comparison Grid in Pastels */}
                  <div>
                    <h4 className="text-xs font-bold text-[#383638] uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <Scale className="w-3.5 h-3.5 text-[#C5A55A]" />
                      Before & After Recovery Comparison
                    </h4>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                      {/* Before State (Blush Pink) */}
                      <div className="bg-[#F8E5E9] border border-[#D9A9B5] rounded-2xl p-3.5 shadow-2xs">
                        <div className="font-bold text-[#9D435F] mb-2 flex items-center gap-1">
                          <AlertTriangle className="w-3.5 h-3.5" />
                          Current Faulty State
                        </div>
                        <ul className="space-y-1 text-[#832B45] text-[11px]">
                          <li>• Ordered Variant: <strong>Size M</strong> (Reserved: 0 ❌)</li>
                          <li>• Incorrect Variant: <strong>Size L</strong> (Reserved: ≥1 ⚠️)</li>
                          <li>• Order Status: <span className="font-mono font-semibold">STALLED_INCONSISTENT</span></li>
                          <li>• Customer Impact: Blocked from packing & shipment</li>
                        </ul>
                      </div>

                      {/* Expected After State (Sage Green) */}
                      <div className="bg-[#E8EFE5] border border-[#8BA888] rounded-2xl p-3.5 shadow-2xs">
                        <div className="font-bold text-[#065F46] mb-2 flex items-center gap-1">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          Target State Post-Execution
                        </div>
                        <ul className="space-y-1 text-[#245229] text-[11px]">
                          <li>• Ordered Variant: <strong>Size M</strong> (Reserved: 1 ✅)</li>
                          <li>• Incorrect Variant: <strong>Size L</strong> (Restocked safely ✅)</li>
                          <li>• Order Status: <span className="font-mono font-semibold">INVOICED</span> (Resumed)</li>
                          <li>• Verification: Double-entry invariant guarantee</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* Automated Testing Status (Powder Blue) */}
                  <div className={`p-4 rounded-2xl border ${checksPassed ? 'bg-[#E8EFE5] border-[#8BA888]' : 'bg-[#FAF5EF] border-[#E9D8B5]'}`}>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-xs font-bold flex items-center gap-1.5 text-[#383638]">
                        {checksPassed ? '✅ Automated Pre-Checks: PASSED' : '⚠️ Pre-Checks: PENDING OR FAILED'}
                      </span>
                      {!checksPassed && (
                        <button
                          onClick={() => handlePreCheck(p.id)}
                          disabled={preChecking === p.id}
                          className="px-2.5 py-1 bg-[#383638] text-white text-[11px] font-bold rounded-lg hover:bg-black disabled:opacity-50"
                        >
                          {preChecking === p.id ? 'Running...' : 'Run Pre-Checks'}
                        </button>
                      )}
                    </div>

                    <div className="space-y-1 text-[11px]">
                      {(p.pre_check_test_results?.checks || []).map((c: any, idx: number) => (
                        <div key={idx} className={c.passed ? 'text-[#065F46]' : 'text-[#854D0E]'}>
                          {c.passed ? '✓' : '✗'} <strong>{c.check}</strong>: {c.detail}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Expanded: Execution & Rollback Steps */}
                  {isExpanded && (
                    <div className="space-y-4 pt-3 border-t border-[#E7E8EB]">
                      <div>
                        <h4 className="text-xs font-bold text-[#383638] uppercase tracking-wider mb-2">
                          Proposed Action Sequence ({p.execution_steps?.length || 0} Steps)
                        </h4>
                        <div className="space-y-1.5 bg-[#FAF5EF] p-3 rounded-2xl border border-[#E7E8EB] text-xs">
                          {(p.execution_steps || []).map((s: any) => (
                            <div key={s.step} className="flex gap-2">
                              <span className="font-mono font-bold text-[#8C95A0]">{s.step}.</span>
                              <div>
                                <strong className="text-[#383638]">{s.action}</strong>
                                <span className="text-[#71717A] ml-1">({s.target})</span>
                                <p className="text-[11px] text-[#4B5563]">{s.description}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h4 className="text-xs font-bold text-[#383638] uppercase tracking-wider mb-2">
                          Rollback Safety Plan ({p.rollback_steps?.length || 0} Steps)
                        </h4>
                        <div className="space-y-1.5 bg-[#FAF5EF] p-3 rounded-2xl border border-[#E7E8EB] text-xs">
                          {(p.rollback_steps || []).map((s: any) => (
                            <div key={s.step} className="flex gap-2">
                              <span className="font-mono font-bold text-[#8C95A0]">{s.step}.</span>
                              <div>
                                <strong className="text-[#383638]">{s.action}</strong>
                                <p className="text-[11px] text-[#4B5563]">{s.description}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Comments & Decision Buttons */}
                  <div className="pt-3 border-t border-[#E7E8EB] flex flex-col gap-3">
                    <input
                      value={comment}
                      onChange={e => setComment(e.target.value)}
                      placeholder="Supervisor review notes / reasoning..."
                      className="w-full border border-[#E7E8EB] rounded-xl px-3 py-2 text-xs text-[#383638] focus:outline-none focus:ring-1 focus:ring-[#C5A55A] bg-[#FAF5EF]"
                    />

                    <div className="flex items-center gap-3 flex-wrap">
                      <button
                        onClick={() => handleDecide(p.id, 'APPROVED')}
                        disabled={deciding === p.id || !checksPassed || p.status === 'APPROVED'}
                        className="flex items-center gap-1.5 px-4 py-2 bg-[#065F46] hover:bg-[#047857] text-white rounded-xl text-xs font-bold disabled:opacity-40 transition-colors shadow-xs"
                      >
                        <ShieldCheck className="w-4 h-4" />
                        {deciding === p.id ? 'Signing...' : p.status === 'APPROVED' ? 'Approved ✓' : 'Approve Proposal'}
                      </button>

                      <button
                        onClick={() => handleDecide(p.id, 'REJECTED')}
                        disabled={deciding === p.id || p.status === 'REJECTED'}
                        className="flex items-center gap-1.5 px-4 py-2 bg-[#9D435F] hover:bg-[#832B45] text-white rounded-xl text-xs font-bold disabled:opacity-40 transition-colors shadow-xs"
                      >
                        <ShieldX className="w-4 h-4" />
                        {deciding === p.id ? 'Processing...' : 'Reject Proposal'}
                      </button>

                      {p.status === 'APPROVED' && (
                        <button
                          onClick={() => handleExecute(p.id)}
                          disabled={executing === p.id}
                          className="flex items-center gap-1.5 px-4 py-2 bg-[#383638] hover:bg-black text-[#FAF5EF] border border-[#E9D8B5] rounded-xl text-xs font-bold disabled:opacity-50 transition-colors ml-auto shadow-xs"
                        >
                          <Zap className={`w-4 h-4 ${executing === p.id ? 'animate-bounce text-[#C5A55A]' : 'text-[#C5A55A]'}`} />
                          {executing === p.id ? 'Executing & Verifying...' : '⚡ Execute Authorized Recovery'}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Audit History Column (Span 1) */}
        <div>
          <h2 className="text-xs font-bold text-[#383638] uppercase tracking-wider mb-4 flex items-center gap-2">
            <History className="w-4 h-4 text-[#C5A55A]" />
            Decision Audit Trail ({history.length})
          </h2>

          <div className="bg-[#FCFBF8] border border-[#E7E8EB] rounded-2xl overflow-hidden shadow-xs">
            {history.length === 0 ? (
              <div className="p-8 text-center text-[#8C95A0] text-xs">
                No past decisions recorded yet.
              </div>
            ) : (
              <div className="divide-y divide-[#F3F4F6] max-h-[600px] overflow-y-auto">
                {history.map((a: any) => (
                  <div key={a.id} className="p-4 text-xs space-y-1.5">
                    <div className="flex justify-between items-center">
                      <span className="font-mono font-bold text-[#383638]">{a.proposal_code || 'PROPOSAL'}</span>
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${
                        a.decision === 'APPROVED' ? 'bg-[#E8EFE5] text-[#065F46] border-[#8BA888]' : 'bg-[#F8E5E9] text-[#9D435F] border-[#D9A9B5]'
                      }`}>
                        {a.decision}
                      </span>
                    </div>

                    <p className="text-[#71717A] text-[11px]">
                      Reviewed by <strong className="text-[#383638]">{a.approver_user}</strong> • {formatDate(a.decided_at)}
                    </p>

                    {a.comments && (
                      <p className="text-[#383638] bg-[#FAF5EF] p-2 rounded-xl text-[11px] italic border border-[#E7E8EB]">
                        &quot;{a.comments}&quot;
                      </p>
                    )}

                    <div className="pt-1 text-[10px] font-mono text-[#8C95A0] truncate">
                      SHA256: {a.signature_hash}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
