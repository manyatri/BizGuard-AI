'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api-client';
import { formatDate, getStatusColor } from '@/lib/utils';
import { RefreshCw, AlertTriangle, Boxes } from 'lucide-react';

export default function InventoryPage() {
  const [data, setData] = useState<any>(null);
  const [tab, setTab] = useState<'all' | 'low' | 'out'>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [adjusting, setAdjusting] = useState<string | null>(null);
  const [adjDelta, setAdjDelta] = useState('');
  const [adjReason, setAdjReason] = useState('');
  const [adjError, setAdjError] = useState('');

  const fetchData = async () => {
    setLoading(true); setError(null);
    try {
      const d = await api.getInventory();
      setData(d);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchData(); }, []);

  const items: any[] = data?.inventory || [];
  const filtered = tab === 'low' ? items.filter((i: any) => i.health_status === 'LOW_STOCK')
    : tab === 'out' ? items.filter((i: any) => i.health_status === 'OUT_OF_STOCK')
    : items;

  const handleAdjust = async (variantId: string) => {
    const delta = parseInt(adjDelta);
    if (isNaN(delta)) { setAdjError('Enter a valid number'); return; }
    if (!adjReason.trim()) { setAdjError('Reason is required'); return; }
    try {
      await api.adjustInventory(variantId, { quantity_delta: delta, reason: adjReason });
      setAdjusting(null); setAdjDelta(''); setAdjReason(''); setAdjError('');
      await fetchData();
    } catch (e: any) { setAdjError(e.message); }
  };

  const summary = data?.summary || {};

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-[#E5E7EB]">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl lg:text-2xl font-bold tracking-tight text-[#16191F]">Inventory Matrix</h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider bg-[#FAF5E8] text-[#8A7338] border border-[#E8DCB8]">
              Stock Telemetry
            </span>
          </div>
          <p className="text-xs text-[#64748B] mt-1">
            Real-time multi-variant size & color inventory reservations, bin locations, and stock allocation health.
          </p>
        </div>
        <button
          onClick={fetchData}
          className="flex items-center gap-1.5 px-3 py-1.5 border border-[#E5E7EB] bg-white text-[#4B5563] rounded-lg text-xs font-semibold hover:border-[#C5A55A] hover:text-[#16191F] shadow-xs transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Refresh
        </button>
      </div>

      {loading && <p className="text-xs text-[#8C95A0]">Loading inventory matrix...</p>}
      {error && <p className="text-xs text-[#9F1239]">{error} <button onClick={fetchData} className="underline ml-2">Retry</button></p>}

      {!loading && !error && (
        <>
          {/* Summary cards */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-white rounded-2xl border border-[#E5E7EB] p-4 shadow-xs">
              <div className="text-[11px] text-[#065F46] font-semibold uppercase tracking-wider">Healthy Variants</div>
              <div className="text-2xl font-bold text-[#065F46] mt-1">{summary.healthy ?? 0}</div>
            </div>
            <div className="bg-[#FEFCE8] rounded-2xl border border-[#FEF08A] p-4 shadow-xs">
              <div className="flex items-center gap-1.5 text-[11px] text-[#854D0E] font-semibold uppercase tracking-wider">
                <AlertTriangle className="w-3.5 h-3.5" /> Low Stock Warning
              </div>
              <div className="text-2xl font-bold text-[#854D0E] mt-1">{summary.low_stock ?? 0}</div>
            </div>
            <div className="bg-[#FFF1F2] rounded-2xl border border-[#FECDD3] p-4 shadow-xs">
              <div className="text-[11px] text-[#9F1239] font-semibold uppercase tracking-wider">Depleted / Out of Stock</div>
              <div className="text-2xl font-bold text-[#9F1239] mt-1">{summary.out_of_stock ?? 0}</div>
            </div>
          </div>

          {/* Filter tabs */}
          <div className="flex gap-2 mb-4">
            {(['all', 'low', 'out'] as const).map(t => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  tab === t
                    ? 'bg-[#16191F] text-white shadow-xs'
                    : 'bg-white border border-[#E5E7EB] text-[#4B5563] hover:text-[#16191F]'
                }`}
              >
                {t === 'all' ? `All Variants (${items.length})` : t === 'low' ? `Low Stock (${summary.low_stock ?? 0})` : `Out of Stock (${summary.out_of_stock ?? 0})`}
              </button>
            ))}
          </div>

          {/* Table */}
          <div className="bg-white rounded-2xl border border-[#E5E7EB] overflow-hidden shadow-xs">
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="text-left text-[#64748B] border-b border-[#E5E7EB] bg-[#FAF9F6] uppercase tracking-wider text-[11px]">
                    {['Variant SKU', 'Garment Name', 'Size', 'Color', 'On Hand', 'Reserved', 'Available', 'Health Status', 'Bin Location', 'Stock Adjustment'].map(h =>
                      <th key={h} className="px-4 py-3 font-semibold">{h}</th>)}
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F3F4F6]">
                  {filtered.length === 0 && (
                    <tr><td colSpan={10} className="px-6 py-10 text-center text-[#8C95A0]">No inventory records found</td></tr>
                  )}
                  {filtered.map((inv: any) => (
                    <tr key={inv.variant_id} className={`hover:bg-[#FDFCF7] transition-colors ${
                      inv.health_status === 'OUT_OF_STOCK' ? 'bg-[#FFF1F2]/40' : inv.health_status === 'LOW_STOCK' ? 'bg-[#FEFCE8]/40' : ''
                    }`}>
                      <td className="px-4 py-3.5 font-mono text-xs text-[#16191F] font-medium">{inv.sku}</td>
                      <td className="px-4 py-3.5 text-[#374151] font-medium max-w-[170px] truncate">{inv.product_title}</td>
                      <td className="px-4 py-3.5">
                        <span className="bg-[#FAF9F6] border border-[#E5E7EB] px-2 py-0.5 rounded text-[11px] font-semibold text-[#16191F]">
                          {inv.size}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 text-[#64748B]">{inv.color}</td>
                      <td className="px-4 py-3.5 font-semibold text-[#16191F]">{inv.quantity_on_hand}</td>
                      <td className="px-4 py-3.5 text-[#1E40AF] font-bold">{inv.quantity_reserved}</td>
                      <td className="px-4 py-3.5 font-bold text-[#16191F]">{inv.quantity_available}</td>
                      <td className="px-4 py-3.5">
                        <span className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-semibold border ${getStatusColor(inv.health_status)}`}>
                          {inv.health_status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 text-[#8C95A0] font-mono text-xs">{inv.warehouse_bin || '—'}</td>
                      <td className="px-4 py-3.5">
                        <button
                          onClick={() => { setAdjusting(inv.variant_id); setAdjDelta(''); setAdjReason(''); setAdjError(''); }}
                          className="text-xs font-semibold text-[#832B45] hover:underline"
                        >
                          Adjust
                        </button>
                      </td>
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
