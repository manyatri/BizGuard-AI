'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api-client';
import { formatCurrency, formatDate, getStatusColor } from '@/lib/utils';
import FashionLoader from '@/components/ui/FashionLoader';
import EmptyState from '@/components/ui/EmptyState';
import { RefreshCw, ChevronDown, ChevronUp, ShoppingCart } from 'lucide-react';

const ORDER_STATUSES = ['', 'PENDING', 'PAYMENT_CAPTURED', 'INVENTORY_ALLOCATED', 'INVOICED', 'SHIPPED', 'DELIVERED', 'STALLED_INCONSISTENT', 'CANCELLED'];

export default function OrdersPage() {
  const [orders, setOrders] = useState<any[]>([]);
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);

  const fetchOrders = async () => {
    setLoading(true); setError(null);
    try {
      const d = await api.getOrders(status || undefined).catch(() => []);
      setOrders(Array.isArray(d) ? d : (d?.orders || []));
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchOrders(); }, [status]);

  if (loading) {
    return (
      <div className="p-8 max-w-7xl mx-auto flex items-center justify-center min-h-[500px]">
        <FashionLoader messageIndex={0} />
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-[#E7E8EB]">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl lg:text-2xl font-bold tracking-tight text-[#383638]">Order Management</h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-[#FAF5EF] text-[#8A7338] border border-[#E9D8B5]">
              Transactions
            </span>
          </div>
          <p className="text-xs text-[#71717A] mt-1">
            Customer order lifecycle, payment authorizations, item line-items, and fulfillment statuses.
          </p>
        </div>
        <div className="flex gap-2">
          <select
            value={status}
            onChange={e => setStatus(e.target.value)}
            className="border border-[#E7E8EB] rounded-xl px-3 py-1.5 text-xs text-[#383638] font-medium bg-[#FCFBF8] focus:ring-1 focus:ring-[#C5A55A] focus:outline-none"
          >
            {ORDER_STATUSES.map(s => <option key={s} value={s}>{s || 'All Statuses'}</option>)}
          </select>
          <button
            onClick={fetchOrders}
            className="flex items-center gap-1.5 px-3.5 py-2 border border-[#E7E8EB] bg-[#FCFBF8] text-[#383638] rounded-xl text-xs font-bold hover:border-[#C5A55A] shadow-xs transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {error && <p className="text-xs text-[#9D435F]">{error} <button onClick={fetchOrders} className="underline ml-2">Retry</button></p>}

      {!loading && !error && orders.length === 0 ? (
        <EmptyState
          type="no-orders"
          title="No Transactions Found"
          description="There are currently no customer orders matching your status filter. You can add items to your styling bag from the lookbook and test a simulated checkout."
          actionText="Browse Luxury Runway"
          actionHref="/products"
        />
      ) : (
        <div className="bg-[#FCFBF8] rounded-2xl border border-[#E7E8EB] overflow-hidden shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-left text-[#71717A] border-b border-[#E7E8EB] bg-[#FAF5EF] uppercase tracking-wider text-[11px]">
                  {['', 'Order #', 'Customer', 'Line Items', 'Total Value', 'Pipeline Status', 'Timestamp'].map(h =>
                    <th key={h} className="px-5 py-3 font-semibold">{h}</th>)}
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F3F4F6]">
                {orders.map((o: any) => (
                  <>
                    <tr
                      key={o.id}
                      className={`hover:bg-[#FAF5EF] cursor-pointer transition-colors ${
                        o.status === 'STALLED_INCONSISTENT' ? 'bg-[#F8E5E9]/50' : ''
                      }`}
                      onClick={() => setExpanded(expanded === o.id ? null : o.id)}
                    >
                      <td className="px-5 py-3.5 text-[#8C95A0]">
                        {expanded === o.id ? <ChevronUp className="w-4 h-4 text-[#C5A55A]" /> : <ChevronDown className="w-4 h-4" />}
                      </td>
                      <td className="px-5 py-3.5 font-mono font-bold text-[#383638] text-xs">{o.order_number}</td>
                      <td className="px-5 py-3.5">
                        <div className="text-[#383638] font-bold text-xs">{o.customer_name}</div>
                        <div className="text-[11px] text-[#8C95A0]">{o.customer_email}</div>
                      </td>
                      <td className="px-5 py-3.5 text-[#4B5563] font-medium">{o.items?.length ?? 0} item(s)</td>
                      <td className="px-5 py-3.5 font-bold text-[#383638]">{formatCurrency(o.total_amount)}</td>
                      <td className="px-5 py-3.5">
                        <span className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-semibold border ${getStatusColor(o.status)}`}>
                          {o.status}
                        </span>
                      </td>
                      <td className="px-5 py-3.5 text-[#8C95A0] text-[11px] font-mono">{formatDate(o.created_at)}</td>
                    </tr>
                    {expanded === o.id && (
                      <tr key={`${o.id}-detail`} className="bg-[#FAF5EF] border-b border-[#E7E8EB]">
                        <td colSpan={7} className="px-8 py-4">
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs">
                            {/* Items */}
                            <div>
                              <div className="text-[11px] font-bold text-[#383638] uppercase tracking-wider mb-2">Order Line Items</div>
                              {(o.items || []).map((item: any) => (
                                <div key={item.id} className="text-[#383638] mb-1.5 p-2.5 bg-[#FCFBF8] rounded-xl border border-[#E7E8EB]">
                                  <div className="font-semibold text-[#383638]">{item.product_title}</div>
                                  <div className="text-[11px] text-[#71717A] flex justify-between mt-0.5">
                                    <span>Size {item.ordered_size} · {item.ordered_color} · Qty {item.quantity}</span>
                                    <span className="font-bold text-[#383638]">{formatCurrency(item.subtotal)}</span>
                                  </div>
                                </div>
                              ))}
                            </div>
                            {/* Payment */}
                            <div>
                              <div className="text-[11px] font-bold text-[#383638] uppercase tracking-wider mb-2">Payment Details</div>
                              {(o.payments || []).map((p: any) => (
                                <div key={p.id} className="text-[#383638] p-2.5 bg-[#FCFBF8] rounded-xl border border-[#E7E8EB]">
                                  <div className="flex justify-between items-center">
                                    <span className="font-semibold text-[#383638]">{p.payment_gateway}</span>
                                    <span className={`inline-flex px-1.5 py-0.2 rounded text-[10px] font-semibold border ${getStatusColor(p.status)}`}>{p.status}</span>
                                  </div>
                                  <div className="text-[10px] text-[#8C95A0] font-mono mt-1">{p.transaction_reference}</div>
                                </div>
                              ))}
                            </div>
                            {/* Shipping */}
                            <div>
                              <div className="text-[11px] font-bold text-[#383638] uppercase tracking-wider mb-2">Shipping Destination</div>
                              {o.shipping_address ? (
                                <div className="text-[#383638] p-2.5 bg-[#FCFBF8] rounded-xl border border-[#E7E8EB] text-[11px] leading-relaxed">
                                  {o.shipping_address.line1 && <div>{o.shipping_address.line1}</div>}
                                  <div>{[o.shipping_address.city, o.shipping_address.state, o.shipping_address.pincode].filter(Boolean).join(', ')}</div>
                                  <div>{o.shipping_address.country}</div>
                                </div>
                              ) : (
                                <div className="text-[11px] text-[#8C95A0]">No shipping address recorded</div>
                              )}
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
