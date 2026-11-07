'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api-client';
import { formatCurrency, formatDate, getStatusColor } from '@/lib/utils';
import { RefreshCw, CreditCard } from 'lucide-react';

export default function PaymentsPage() {
  const [orders, setOrders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true); setError(null);
    try {
      const d = await api.getOrders();
      setOrders(Array.isArray(d) ? d : (d?.orders || []));
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchData(); }, []);

  // Flatten all payments from orders
  const payments = orders.flatMap((o: any) =>
    (o.payments || []).map((p: any) => ({ ...p, order_number: o.order_number, customer_name: o.customer_name }))
  );

  const totalCaptured = payments.filter(p => p.status === 'CAPTURED').reduce((s, p) => s + parseFloat(p.amount || 0), 0);
  const totalRefunded = payments.filter(p => p.status === 'REFUNDED').reduce((s, p) => s + parseFloat(p.amount || 0), 0);
  const pending = payments.filter(p => p.status === 'INITIATED').length;

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-[#E5E7EB]">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl lg:text-2xl font-bold tracking-tight text-[#16191F]">Payments & Invoices</h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider bg-[#FAF5E8] text-[#8A7338] border border-[#E8DCB8]">
              Ledger Live
            </span>
          </div>
          <p className="text-xs text-[#64748B] mt-1">
            Payment gateway settlements, captured revenues, refunds, and transactional integrity records.
          </p>
        </div>
        <button
          onClick={fetchData}
          className="flex items-center gap-1.5 px-3 py-1.5 border border-[#E5E7EB] bg-white text-[#4B5563] rounded-lg text-xs font-semibold hover:border-[#C5A55A] hover:text-[#16191F] shadow-xs transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Refresh
        </button>
      </div>

      {loading && <p className="text-xs text-[#8C95A0]">Loading payment ledger...</p>}
      {error && <p className="text-xs text-[#9F1239]">{error} <button onClick={fetchData} className="underline ml-2">Retry</button></p>}

      {!loading && !error && (
        <>
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-white rounded-2xl border border-[#E5E7EB] p-5 shadow-xs">
              <div className="text-[11px] text-[#065F46] font-semibold uppercase tracking-wider mb-1">Total Captured</div>
              <div className="text-2xl font-bold text-[#065F46]">{formatCurrency(totalCaptured)}</div>
            </div>
            <div className="bg-[#FEFCE8] rounded-2xl border border-[#FEF08A] p-5 shadow-xs">
              <div className="text-[11px] text-[#854D0E] font-semibold uppercase tracking-wider mb-1">Pending Gateways</div>
              <div className="text-2xl font-bold text-[#854D0E]">{pending}</div>
            </div>
            <div className="bg-[#FDF2F4] rounded-2xl border border-[#FBCFE8] p-5 shadow-xs">
              <div className="text-[11px] text-[#9D435F] font-semibold uppercase tracking-wider mb-1">Total Refunded</div>
              <div className="text-2xl font-bold text-[#9D435F]">{formatCurrency(totalRefunded)}</div>
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-[#E5E7EB] overflow-hidden shadow-xs">
            <div className="px-6 py-4 border-b border-[#E5E7EB] bg-[#FCFAF7] flex justify-between items-center">
              <h2 className="text-xs font-bold uppercase tracking-wider text-[#16191F]">Settlement Transaction Log</h2>
              <span className="text-xs text-[#8C95A0] font-medium">{payments.length} transactions</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="text-left text-[#64748B] border-b border-[#E5E7EB] bg-[#FAF9F6] uppercase tracking-wider text-[11px]">
                    {['Transaction Ref', 'Order #', 'Customer Name', 'Authorized Amount', 'Payment Gateway', 'Capture Status', 'Captured At'].map(h =>
                      <th key={h} className="px-5 py-3 font-semibold">{h}</th>)}
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F3F4F6]">
                  {payments.length === 0 && (
                    <tr><td colSpan={7} className="px-6 py-10 text-center text-[#8C95A0]">No payment transactions found</td></tr>
                  )}
                  {payments.map((p: any) => (
                    <tr key={p.id} className="hover:bg-[#FDFCF7] transition-colors">
                      <td className="px-5 py-3.5 font-mono text-[11px] text-[#64748B] font-medium">{p.transaction_reference}</td>
                      <td className="px-5 py-3.5 font-mono font-bold text-[#16191F]">{p.order_number}</td>
                      <td className="px-5 py-3.5 text-[#374151] font-medium">{p.customer_name}</td>
                      <td className="px-5 py-3.5 font-bold text-[#16191F]">{formatCurrency(p.amount)}</td>
                      <td className="px-5 py-3.5 text-[#4B5563]">{p.payment_gateway}</td>
                      <td className="px-5 py-3.5">
                        <span className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-semibold border ${getStatusColor(p.status)}`}>
                          {p.status}
                        </span>
                      </td>
                      <td className="px-5 py-3.5 text-[#8C95A0] text-[11px] font-mono">{formatDate(p.captured_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
