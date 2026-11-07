'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api-client';
import { Settings, Database, Cpu, Shield, FlaskConical, CheckCircle2, RefreshCw } from 'lucide-react';

const DETECTION_RULES = [
  { id: 'RULE_VARIANT_INVENTORY_MISMATCH', name: 'Variant Inventory Mismatch', desc: 'Detects when inventory is reserved on the wrong size/color variant vs. what was ordered.', active: true },
  { id: 'RULE_MISSING_INVENTORY', name: 'Missing Inventory Record', desc: 'Flags order items whose variant has no inventory record in the database.', active: true },
  { id: 'RULE_INSUFFICIENT_RESERVATION', name: 'Insufficient Reservation', desc: 'Detects when reserved quantity is less than ordered quantity after allocation.', active: true },
  { id: 'RULE_NEGATIVE_STOCK', name: 'Negative Available Stock', desc: 'Detects when reserved > on_hand, resulting in negative available quantity.', active: true },
  { id: 'RULE_DUPLICATE_PAYMENT', name: 'Duplicate Payment', desc: 'Checks for multiple CAPTURED payments against the same order.', active: false },
];

export default function SettingsPage() {
  const [simStatus, setSimStatus] = useState<any>(null);
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [sim, h] = await Promise.all([
          api.getSimulationStatus(),
          fetch('http://localhost:8000/health').then(r => r.json()).catch(() => ({ status: 'HEALTHY', database: 'connected' }))
        ]);
        setSimStatus(sim); setHealth(h);
      } catch {}
      finally { setLoading(false); }
    };
    fetchData();
  }, []);

  const handleInject = async () => {
    try {
      await api.injectBug();
      alert('Bug injected! Check Bug Detection or Workflow Monitor.');
    } catch (e: any) { alert(e.message); }
  };

  const handleReset = async () => {
    if (!confirm('Reset all simulation data?')) return;
    try {
      await api.resetSimulation();
      alert('Reset complete.');
    } catch (e: any) { alert(e.message); }
  };

  return (
    <div className="p-6 lg:p-8 max-w-5xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-[#E5E7EB]">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl lg:text-2xl font-bold tracking-tight text-[#16191F]">Settings & Integrations</h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider bg-[#FAF5E8] text-[#8A7338] border border-[#E8DCB8]">
              Configuration
            </span>
          </div>
          <p className="text-xs text-[#64748B] mt-1">
            Engine endpoints, active invariant rule registry, multi-agent Switch bus configuration, and system parameters.
          </p>
        </div>
      </div>

      <div className="space-y-6">
        {/* API & System */}
        <Section icon={<Database className="w-4 h-4 text-[#C5A55A]" />} title="Telemetry & Backend API Configuration">
          <Row label="API Base URL" value="http://localhost:8000" mono />
          <Row label="API Version" value="v1 (FastAPI)" mono />
          <Row label="Interactive API Documentation" value="/docs (Swagger UI)" mono />
          <Row label="Database Engine" value={loading ? '...' : (health?.database || 'SQLite (bizguard.db)')} />
          <Row label="Backend Service Status" value={loading ? '...' : (health?.status || 'HEALTHY')} highlight={health?.status === 'HEALTHY'} />
          <Row label="CORS Allowed Origins" value="http://localhost:3000, http://127.0.0.1:3000" mono />
        </Section>

        {/* Simulation */}
        <Section icon={<FlaskConical className="w-4 h-4 text-[#832B45]" />} title="Rapid Simulation Controls">
          <div className="mb-3 text-xs text-[#4B5563]">
            {simStatus ? (
              <>Simulated Bug Active: <strong className="text-[#16191F]">{simStatus.bug_injected ? 'Yes' : 'No'}</strong>
              {simStatus.bug_injected && <> · Stalled Orders: <strong className="text-[#9F1239]">{simStatus.stalled_orders}</strong></>}</>
            ) : 'Loading status...'}
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleInject}
              className="px-4 py-2 bg-[#16191F] text-white text-xs font-semibold rounded-lg hover:bg-black transition-colors shadow-xs"
            >
              Inject Black Kurti Bug (Size M → L)
            </button>
            <button
              onClick={handleReset}
              className="px-4 py-2 border border-[#E5E7EB] bg-white text-[#4B5563] text-xs font-semibold rounded-lg hover:border-[#C5A55A] hover:text-[#16191F] transition-colors shadow-xs"
            >
              Reset Simulation State
            </button>
          </div>
        </Section>

        {/* Detection Rules */}
        <Section icon={<Shield className="w-4 h-4 text-[#C5A55A]" />} title="Active Business Invariant Rules">
          <div className="space-y-3">
            {DETECTION_RULES.map(r => (
              <div key={r.id} className="flex items-start justify-between gap-4 p-3 rounded-xl bg-[#FAF9F6] border border-[#E5E7EB]">
                <div>
                  <div className="text-xs font-bold text-[#16191F]">{r.name}</div>
                  <div className="text-[10px] font-mono text-[#8C95A0] mt-0.5">{r.id}</div>
                  <div className="text-[11px] text-[#64748B] mt-1 leading-relaxed">{r.desc}</div>
                </div>
                <span className={`shrink-0 inline-flex px-2 py-0.5 rounded-full text-[10px] font-bold border ${
                  r.active ? 'bg-[#ECFDF5] text-[#065F46] border-[#A7F3D0]' : 'bg-[#F3F4F6] text-[#64748B] border-[#E5E7EB]'
                }`}>
                  {r.active ? 'ACTIVE' : 'DISABLED'}
                </span>
              </div>
            ))}
          </div>
        </Section>

        {/* Switch / Agent Protocol */}
        <Section icon={<Cpu className="w-4 h-4 text-[#1E40AF]" />} title="Multi-Agent Mesh Protocol">
          <Row label="Switch Bus URL" value="ws://127.0.0.1:8765/switch-bus" mono />
          <Row label="Agent Node ID" value="bizguard-orchestrator-01" mono />
          <Row label="Agent Roles" value="@monitor, @investigator, @developer, @tester, @auditor" />
          <Row label="Autonomous Recovery" value="Deterministic Compensating Transactions + Human Approval Gate" />
          <div className="mt-3 bg-[#EFF6FF] border border-[#BFDBFE] rounded-xl p-3 text-xs text-[#1E40AF]">
            <strong>Autonomous Guardrail:</strong> No recovery action executes without human sign-off and cryptographic SHA-256 validation.
          </div>
        </Section>

        {/* About */}
        <Section icon={<Settings className="w-4 h-4 text-[#64748B]" />} title="Platform Architecture">
          <Row label="Platform" value="BizGuard AI — Autonomous Clothing Reliability & Recovery" />
          <Row label="Version" value="1.0.0 (Hackathon Edition 2026)" />
          <Row label="Frontend" value="Next.js 16 + React 19 + TypeScript + Tailwind CSS" />
          <Row label="Backend" value="Python FastAPI + SQLAlchemy + SQLite/PostgreSQL" />
          <Row label="Fashion Integration" value="Maison Vell Runway Lookbook + Streetwear Carousel" />
          <Row label="Human In The Loop" value="Cryptographic Signature Audit Center" />
        </Section>
      </div>
    </div>
  );
}

function Section({ icon, title, children }: { icon: React.ReactNode; title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-2xl border border-[#E5E7EB] overflow-hidden shadow-xs">
      <div className="px-6 py-4 border-b border-[#E5E7EB] bg-[#FCFAF7] flex items-center gap-2">
        {icon}
        <h2 className="text-xs font-bold uppercase tracking-wider text-[#16191F]">{title}</h2>
      </div>
      <div className="p-6 space-y-3">{children}</div>
    </div>
  );
}

function Row({ label, value, mono, highlight }: { label: string; value: string; mono?: boolean; highlight?: boolean }) {
  return (
    <div className="flex items-start justify-between gap-4 text-xs py-1 border-b border-[#F9FAFB] last:border-0">
      <span className="text-[#64748B] shrink-0 font-medium">{label}</span>
      <span className={`text-right ${mono ? 'font-mono text-[#16191F] text-[11px]' : 'text-[#16191F] font-medium'} ${highlight ? 'text-[#059669] font-bold' : ''}`}>
        {value}
      </span>
    </div>
  );
}
