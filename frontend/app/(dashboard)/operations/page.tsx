'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api-client';
import { formatCurrency, formatDate, getStatusColor } from '@/lib/utils';
import FashionLoader from '@/components/ui/FashionLoader';
import EmptyState from '@/components/ui/EmptyState';
import {
  ShoppingCart, TrendingUp, Package, AlertTriangle, RefreshCw,
  GitBranch, Bug, BrainCircuit, CheckSquare, ArrowUpRight, ShieldCheck, Sparkles
} from 'lucide-react';

export default function OperationsPage() {
  const [metrics, setMetrics] = useState<any>(null);
  const [orders, setOrders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true); setError(null);
    try {
      const [m, o] = await Promise.all([
        api.getDashboardMetrics().catch(() => null),
        api.getOrders().catch(() => [])
      ]);
      setMetrics(m);
      setOrders(Array.isArray(o) ? o.slice(0, 8) : (o?.orders || []).slice(0, 8));
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchData(); }, []);

  if (loading) {
    return (
      <PageShell title="Business Operations">
        <div className="flex flex-col items-center justify-center py-20">
          <FashionLoader messageIndex={1} />
        </div>
      </PageShell>
    );
  }

  if (error) {
    return (
      <PageShell title="Business Operations">
        <ErrorBox msg={error} retry={fetchData} />
      </PageShell>
    );
  }

  const stats = [
    { label: 'Total Orders', value: metrics?.total_orders ?? 0, icon: ShoppingCart, bg: '#E4EFF8', border: '#9BB7D4', text: '#1E40AF' },
    { label: 'Total Revenue', value: formatCurrency(metrics?.total_revenue), icon: TrendingUp, bg: '#E8EFE5', border: '#8BA888', text: '#065F46' },
    { label: 'Active Catalog', value: metrics?.total_products ?? 0, icon: Package, bg: '#FAF5EF', border: '#E9D8B5', text: '#8A7338' },
    { label: 'Active Incidents', value: metrics?.active_incidents ?? 0, icon: AlertTriangle, bg: '#F8E5E9', border: '#D9A9B5', text: '#9D435F' },
  ];

  const quickActions = [
    { href: '/workflows', label: 'Workflow Monitor', desc: 'Real-time order state machine execution', icon: GitBranch, color: 'text-[#1E40AF]', bg: 'hover:bg-[#E4EFF8]/40' },
    { href: '/bugs', label: 'Bug Detection & Simulator', desc: 'Inject failure scenarios & test auto-detection', icon: Bug, color: 'text-[#9D435F]', bg: 'hover:bg-[#F8E5E9]/40' },
    { href: '/war-room', label: 'AI War Rooms', desc: 'Multi-agent diagnostic investigations', icon: BrainCircuit, color: 'text-[#8A7338]', bg: 'hover:bg-[#FAF5EF]/60' },
    { href: '/approvals', label: 'Approval Center', desc: 'Human verification & atomic recovery', icon: CheckSquare, color: 'text-[#065F46]', bg: 'hover:bg-[#E8EFE5]/40' },
  ];

  return (
    <PageShell
      title="Business Operations"
      subtitle="Autonomous reliability monitoring and live operational status across storefront and fulfillment"
      action={
        <button
          onClick={fetchData}
          className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold rounded-xl bg-[#FCFBF8] border border-[#E7E8EB] text-[#383638] hover:border-[#C5A55A] transition-all shadow-xs"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Refresh Telemetry
        </button>
      }
    >
      {/* KPI Stats Grid in Pastels */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {stats.map(s => (
          <div
            key={s.label}
            className="rounded-2xl p-5 border shadow-xs transition-all hover:scale-101"
            style={{ backgroundColor: s.bg, borderColor: s.border }}
          >
            <div className="inline-flex p-2.5 rounded-xl bg-white/80 border border-white/60 mb-3 shadow-xs">
              <s.icon className="w-5 h-5" style={{ color: s.text }} />
            </div>
            <div className="text-2xl font-bold tracking-tight text-[#383638]">{s.value}</div>
            <div className="text-xs font-bold mt-1 uppercase tracking-wider" style={{ color: s.text }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Module Fast Jump Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {quickActions.map(q => (
          <Link
            key={q.href}
            href={q.href}
            className={`group bg-[#FCFBF8] rounded-2xl border border-[#E7E8EB] p-4.5 hover:border-[#C5A55A] hover:shadow-sm transition-all flex flex-col justify-between ${q.bg}`}
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <q.icon className={`w-5 h-5 ${q.color}`} />
                <ArrowUpRight className="w-4 h-4 text-[#8C95A0] group-hover:text-[#C5A55A] transition-colors" />
              </div>
              <div className="font-bold text-xs text-[#383638] group-hover:text-[#9D435F] transition-colors">
                {q.label}
              </div>
              <p className="text-[11px] text-[#71717A] mt-1 leading-relaxed">{q.desc}</p>
            </div>
            <span className="text-[11px] font-bold text-[#8A7338] mt-3 inline-flex items-center gap-1">
              Launch module →
            </span>
          </Link>
        ))}
      </div>

      {/* Recent Orders Table */}
      <div className="bg-[#FCFBF8] rounded-2xl border border-[#E7E8EB] shadow-xs overflow-hidden">
        <div className="px-6 py-4 border-b border-[#E7E8EB] bg-[#FAF5EF] flex justify-between items-center">
          <div>
            <h2 className="font-bold text-xs text-[#383638] uppercase tracking-wider">Live Transaction Queue</h2>
            <p className="text-[11px] text-[#71717A]">Real-time customer orders processed through BizGuard state machines</p>
          </div>
          <Link href="/orders" className="text-xs font-bold text-[#9D435F] hover:text-[#C5A55A] transition-colors">
            All Orders ({metrics?.total_orders ?? 0}) →
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#FAF5EF] text-[#71717A] uppercase tracking-wider border-b border-[#E7E8EB]">
              <tr>
                {['Order #', 'Customer', 'Amount', 'Status', 'Fulfillment Date'].map(h => (
                  <th key={h} className="px-6 py-3 font-semibold text-[11px]">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F3F4F6]">
              {orders.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-[#8C95A0]">
                    No live orders registered in database. Test a checkout from the lookbook.
                  </td>
                </tr>
              )}
              {orders.map((o: any) => (
                <tr key={o.id} className="hover:bg-[#FAF5EF] transition-colors">
                  <td className="px-6 py-3.5 font-mono font-bold text-[#383638]">{o.order_number}</td>
                  <td className="px-6 py-3.5 text-[#383638] font-medium">{o.customer_name}</td>
                  <td className="px-6 py-3.5 text-[#383638] font-bold">{formatCurrency(o.total_amount)}</td>
                  <td className="px-6 py-3.5"><StatusBadge status={o.status} /></td>
                  <td className="px-6 py-3.5 text-[#71717A] font-mono text-[11px]">{formatDate(o.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </PageShell>
  );
}

function StatusBadge({ status }: { status: string }) {
  return (
    <span className={`inline-flex px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${getStatusColor(status)}`}>
      {status}
    </span>
  );
}

function PageShell({
  title,
  subtitle,
  children,
  action
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  action?: React.ReactNode;
}) {
  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-[#E7E8EB]">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl lg:text-2xl font-bold tracking-tight text-[#383638]">{title}</h1>
            <span className="px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider bg-[#E8EFE5] text-[#065F46] border border-[#8BA888]">
              Live
            </span>
          </div>
          {subtitle && <p className="text-xs text-[#71717A] mt-1">{subtitle}</p>}
        </div>
        {action}
      </div>
      {children}
    </div>
  );
}

function ErrorBox({ msg, retry }: { msg: string; retry: () => void }) {
  return (
    <div className="bg-[#F8E5E9] border border-[#D9A9B5] rounded-2xl p-6 text-center">
      <p className="text-sm text-[#9D435F] mb-3 font-semibold">{msg}</p>
      <button
        onClick={retry}
        className="px-4 py-1.5 rounded-xl text-xs font-bold bg-white border border-[#D9A9B5] text-[#9D435F] hover:bg-[#F4DDE4] transition-colors"
      >
        Retry Telemetry Connection
      </button>
    </div>
  );
}
