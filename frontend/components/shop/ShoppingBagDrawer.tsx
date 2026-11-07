'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useCart } from '@/lib/cart-context';
import { formatCurrency } from '@/lib/utils';
import { api } from '@/lib/api-client';
import EmptyState from '@/components/ui/EmptyState';
import FashionLoader from '@/components/ui/FashionLoader';
import {
  X, Trash2, Plus, Minus, ArrowRight, ShieldCheck, CheckCircle2,
  Sparkles, CreditCard, Truck, Tag, Lock, ArrowLeft
} from 'lucide-react';

export default function ShoppingBagDrawer() {
  const {
    items,
    removeFromCart,
    updateQuantity,
    clearCart,
    subtotal,
    discount,
    deliveryCharge,
    finalTotal,
    isBagOpen,
    setIsBagOpen,
    isCheckoutOpen,
    setIsCheckoutOpen,
  } = useCart();

  // Checkout state
  const [step, setStep] = useState<'bag' | 'checkout' | 'success'>('bag');
  const [name, setName] = useState('Priya Sharma');
  const [email, setEmail] = useState('priya.sharma@example.com');
  const [phone, setPhone] = useState('+91 98765 43210');
  const [address, setAddress] = useState('Flat 402, Lotus Grandeur, Indiranagar');
  const [city, setCity] = useState('Bengaluru');
  const [state, setState] = useState('Karnataka');
  const [pincode, setPincode] = useState('560038');
  const [paymentMethod, setPaymentMethod] = useState<'UPI' | 'CARD' | 'NET_BANKING'>('UPI');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [createdOrder, setCreatedOrder] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isBagOpen && !isCheckoutOpen) return null;

  const handleClose = () => {
    setIsBagOpen(false);
    setIsCheckoutOpen(false);
    if (step === 'success') {
      setStep('bag');
    }
  };

  const handleProceedToCheckout = () => {
    setStep('checkout');
    setIsBagOpen(false);
    setIsCheckoutOpen(true);
  };

  const handlePlaceOrder = async () => {
    if (!name.trim() || !email.trim()) {
      setErrorMsg('Please provide your name and email for the invoice.');
      return;
    }
    setIsSubmitting(true);
    setErrorMsg(null);

    try {
      // Map cart items to backend format
      const orderPayload = {
        customer_name: name,
        customer_email: email,
        customer_phone: phone,
        shipping_address: {
          line1: address,
          city,
          state,
          pincode,
          country: 'India',
        },
        items: items.map(item => ({
          variant_id: item.id.includes('-') ? undefined : item.id, // if real UUID
          sku: item.sku || `SKU-${item.name.substring(0, 3).toUpperCase()}-${item.size}`,
          ordered_size: item.size,
          ordered_color: item.color,
          quantity: item.quantity,
          unit_price: item.price,
        })),
        payment: {
          payment_gateway: paymentMethod === 'UPI' ? 'UPI_RAZORPAY' : paymentMethod === 'CARD' ? 'STRIPE_LUXURY' : 'NET_BANKING',
          amount: finalTotal,
        },
      };

      const res = await api.createOrder(orderPayload);
      setCreatedOrder(res);
      clearCart();
      setStep('success');
    } catch (e: any) {
      setErrorMsg(e.message || 'Error processing luxury checkout.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Backdrop */}
      <div
        onClick={handleClose}
        className="fixed inset-0 bg-[#16191F]/40 backdrop-blur-xs transition-opacity duration-300"
      />

      {/* Slide-over panel */}
      <div className="relative z-10 w-full max-w-md lg:max-w-lg bg-[#FAF5EF] h-full shadow-2xl flex flex-col border-l border-[#E7E8EB] overflow-hidden animate-[slideLeft_0.35s_cubic-bezier(0.16,1,0.3,1)]">
        {/* Drawer Header */}
        <div className="p-5 border-b border-[#E7E8EB] bg-[#FCFBF8] flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#F8E5E9] border border-[#D9A9B5] flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-[#9D435F]" />
            </div>
            <div>
              <h2 className="text-sm font-bold tracking-tight text-[#383638] uppercase font-mono">
                {step === 'bag' ? 'Maison Vell Styling Bag' : step === 'checkout' ? 'Curated Checkout' : 'Order Authorized'}
              </h2>
              <p className="text-[10px] text-[#8C95A0]">
                {step === 'bag'
                  ? `${items.reduce((a, b) => a + b.quantity, 0)} Luxury Garment(s)`
                  : step === 'checkout'
                  ? 'Autonomous Order Verification'
                  : 'Fulfillment Sequence Initiated'}
              </p>
            </div>
          </div>

          <button
            onClick={handleClose}
            className="w-8 h-8 rounded-lg border border-[#E7E8EB] flex items-center justify-center text-[#8C95A0] hover:text-[#383638] hover:bg-[#FAF5EF] transition-colors"
            aria-label="Close"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* ===================== STEP 1: SHOPPING BAG ===================== */}
        {step === 'bag' && (
          <>
            {items.length === 0 ? (
              <div className="flex-1 p-6 flex flex-col items-center justify-center">
                <EmptyState
                  type="empty-bag"
                  title="Your Styling Bag Is Empty"
                  description="Curate hand-picked luxury garments, bespoke dresses, and signature silk trenchcoats from our lookbook."
                  actionText="Explore Runway Collection"
                  onAction={handleClose}
                  className="bg-transparent border-0 shadow-none"
                />
              </div>
            ) : (
              <div className="flex-1 overflow-y-auto p-5 space-y-4">
                {/* Free shipping progress perk */}
                <div className="p-3 rounded-xl bg-[#E8EFE5] border border-[#8BA888]/40 text-[#245229] text-xs flex items-center gap-2">
                  <Truck className="w-4 h-4 text-[#059669] shrink-0" />
                  <span className="text-[11px] font-medium">
                    {subtotal >= 3000
                      ? '✓ Boutique Privilege Applied: ₹500 VIP discount unlocked!'
                      : `Add ₹${3000 - subtotal} more to unlock ₹500 VIP Boutique credit!`}
                  </span>
                </div>

                {/* Items List */}
                <div className="space-y-3">
                  {items.map(item => (
                    <div
                      key={`${item.id}-${item.size}-${item.color}`}
                      className="group p-3.5 rounded-2xl bg-[#FCFBF8] border border-[#E7E8EB] shadow-[0_2px_8px_rgba(56,54,56,0.03)] hover:border-[#E9D8B5] transition-all flex gap-3.5"
                    >
                      {/* Thumbnail with pastel backdrop */}
                      <div className="w-20 h-24 rounded-xl bg-[#FAF5EF] border border-[#E7E8EB] overflow-hidden shrink-0 flex items-center justify-center p-1.5 group-hover:scale-102 transition-transform">
                        <img
                          src={item.image}
                          alt={item.name}
                          className="w-full h-full object-contain"
                        />
                      </div>

                      {/* Info & Controls */}
                      <div className="flex-1 flex flex-col justify-between min-w-0">
                        <div>
                          <div className="flex justify-between items-start gap-2">
                            <h3 className="font-semibold text-xs text-[#383638] truncate">
                              {item.name}
                            </h3>
                            <button
                              onClick={() => removeFromCart(item.id)}
                              className="text-[#8C95A0] hover:text-[#9D435F] p-0.5 transition-colors"
                              title="Remove item"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                          <p className="text-[10px] text-[#8C95A0] mt-0.5">{item.category || 'Luxury Pret'}</p>

                          {/* Selected Variant Badges */}
                          <div className="flex items-center gap-1.5 mt-1.5">
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#F8E5E9] text-[#9D435F] border border-[#D9A9B5]/40">
                              Size {item.size}
                            </span>
                            <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#E4EFF8] text-[#1E40AF] border border-[#9BB7D4]/40">
                              {item.color}
                            </span>
                          </div>
                        </div>

                        {/* Price & Quantity Selector */}
                        <div className="flex justify-between items-center mt-2.5 pt-2 border-t border-[#F8F5EF]">
                          <span className="font-bold text-xs text-[#383638]">
                            {formatCurrency(item.price * item.quantity)}
                          </span>

                          <div className="flex items-center gap-1 bg-[#FAF5EF] border border-[#E7E8EB] rounded-lg p-0.5">
                            <button
                              onClick={() => updateQuantity(item.id, -1)}
                              className="w-5 h-5 flex items-center justify-center rounded text-[#383638] hover:bg-white transition-colors"
                              aria-label="Decrease quantity"
                            >
                              <Minus className="w-3 h-3" />
                            </button>
                            <span className="w-5 text-center text-xs font-bold text-[#383638]">
                              {item.quantity}
                            </span>
                            <button
                              onClick={() => updateQuantity(item.id, 1)}
                              className="w-5 h-5 flex items-center justify-center rounded text-[#383638] hover:bg-white transition-colors"
                              aria-label="Increase quantity"
                            >
                              <Plus className="w-3 h-3" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Bag Summary Footer */}
            {items.length > 0 && (
              <div className="p-5 border-t border-[#E7E8EB] bg-[#FCFBF8] space-y-3">
                <div className="space-y-1.5 text-xs text-[#71717A]">
                  <div className="flex justify-between">
                    <span>Subtotal</span>
                    <span className="text-[#383638] font-semibold">{formatCurrency(subtotal)}</span>
                  </div>
                  {discount > 0 && (
                    <div className="flex justify-between text-[#065F46]">
                      <span className="flex items-center gap-1">
                        <Tag className="w-3.5 h-3.5 text-[#059669]" /> VIP Privilege Discount
                      </span>
                      <span className="font-semibold">- {formatCurrency(discount)}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span>Complimentary Insured Courier</span>
                    <span className="text-[#059669] font-semibold">
                      {deliveryCharge === 0 ? 'FREE' : formatCurrency(deliveryCharge)}
                    </span>
                  </div>
                  <div className="pt-2 border-t border-[#E7E8EB] flex justify-between text-sm font-bold text-[#383638]">
                    <span>Total Estimated</span>
                    <span className="text-base text-[#383638]">{formatCurrency(finalTotal)}</span>
                  </div>
                </div>

                <button
                  onClick={handleProceedToCheckout}
                  className="w-full py-3 rounded-xl bg-[#383638] text-white font-semibold text-xs uppercase tracking-wider hover:bg-black transition-all shadow-md flex items-center justify-center gap-2"
                >
                  <span>Proceed to Checkout</span>
                  <ArrowRight className="w-4 h-4 text-[#C5A55A]" />
                </button>
              </div>
            )}
          </>
        )}

        {/* ===================== STEP 2: CHECKOUT ===================== */}
        {step === 'checkout' && (
          <div className="flex-1 flex flex-col justify-between overflow-y-auto">
            <div className="p-5 space-y-4">
              <button
                onClick={() => setStep('bag')}
                className="flex items-center gap-1.5 text-xs font-semibold text-[#8C95A0] hover:text-[#383638] transition-colors mb-2"
              >
                <ArrowLeft className="w-3.5 h-3.5" /> Return to Styling Bag
              </button>

              {errorMsg && (
                <div className="p-3 rounded-xl bg-[#F8E5E9] border border-[#D9A9B5] text-[#9D435F] text-xs">
                  {errorMsg}
                </div>
              )}

              {/* Delivery Address Card */}
              <div className="p-4 rounded-2xl bg-[#FCFBF8] border border-[#E7E8EB] shadow-xs space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-[#383638] flex items-center gap-1.5">
                  <Truck className="w-3.5 h-3.5 text-[#C5A55A]" />
                  Delivery & Contact Information
                </h3>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="col-span-2">
                    <label className="text-[10px] text-[#8C95A0] block mb-0.5">Full Name</label>
                    <input
                      value={name}
                      onChange={e => setName(e.target.value)}
                      className="w-full px-3 py-1.5 rounded-lg border border-[#E7E8EB] bg-[#FAF5EF] text-[#383638] font-medium focus:ring-1 focus:ring-[#C5A55A] focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] text-[#8C95A0] block mb-0.5">Email (for invoice)</label>
                    <input
                      value={email}
                      onChange={e => setEmail(e.target.value)}
                      className="w-full px-3 py-1.5 rounded-lg border border-[#E7E8EB] bg-[#FAF5EF] text-[#383638] font-medium focus:ring-1 focus:ring-[#C5A55A] focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] text-[#8C95A0] block mb-0.5">Phone Number</label>
                    <input
                      value={phone}
                      onChange={e => setPhone(e.target.value)}
                      className="w-full px-3 py-1.5 rounded-lg border border-[#E7E8EB] bg-[#FAF5EF] text-[#383638] font-medium focus:ring-1 focus:ring-[#C5A55A] focus:outline-none"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="text-[10px] text-[#8C95A0] block mb-0.5">Boutique Delivery Address</label>
                    <input
                      value={address}
                      onChange={e => setAddress(e.target.value)}
                      className="w-full px-3 py-1.5 rounded-lg border border-[#E7E8EB] bg-[#FAF5EF] text-[#383638] font-medium focus:ring-1 focus:ring-[#C5A55A] focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] text-[#8C95A0] block mb-0.5">City</label>
                    <input
                      value={city}
                      onChange={e => setCity(e.target.value)}
                      className="w-full px-3 py-1.5 rounded-lg border border-[#E7E8EB] bg-[#FAF5EF] text-[#383638] font-medium focus:ring-1 focus:ring-[#C5A55A] focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] text-[#8C95A0] block mb-0.5">Pincode</label>
                    <input
                      value={pincode}
                      onChange={e => setPincode(e.target.value)}
                      className="w-full px-3 py-1.5 rounded-lg border border-[#E7E8EB] bg-[#FAF5EF] text-[#383638] font-medium focus:ring-1 focus:ring-[#C5A55A] focus:outline-none"
                    />
                  </div>
                </div>
              </div>

              {/* Payment Method Selector */}
              <div className="p-4 rounded-2xl bg-[#FCFBF8] border border-[#E7E8EB] shadow-xs space-y-2.5">
                <h3 className="text-xs font-bold uppercase tracking-wider text-[#383638] flex items-center gap-1.5">
                  <CreditCard className="w-3.5 h-3.5 text-[#C5A55A]" />
                  Payment Instrument
                </h3>
                <div className="space-y-2 text-xs">
                  {[
                    { id: 'UPI', label: 'Instant UPI (Google Pay, PhonePe, Paytm)', desc: 'Zero gateway surcharge' },
                    { id: 'CARD', label: 'Luxury Credit / Debit Card', desc: 'Encrypted via Stripe Elements' },
                    { id: 'NET_BANKING', label: 'Net Banking & Wire Transfer', desc: 'Instant merchant verification' },
                  ].map(m => (
                    <label
                      key={m.id}
                      onClick={() => setPaymentMethod(m.id as any)}
                      className={`flex items-center justify-between p-3 rounded-xl border cursor-pointer transition-all ${
                        paymentMethod === m.id
                          ? 'bg-[#FAF5EF] border-[#C5A55A] shadow-xs'
                          : 'border-[#E7E8EB] hover:bg-[#FCFBF8]'
                      }`}
                    >
                      <div className="flex items-center gap-2.5">
                        <input
                          type="radio"
                          name="payment"
                          checked={paymentMethod === m.id}
                          onChange={() => {}}
                          className="accent-[#C5A55A]"
                        />
                        <div>
                          <div className="font-semibold text-[#383638]">{m.label}</div>
                          <div className="text-[10px] text-[#8C95A0]">{m.desc}</div>
                        </div>
                      </div>
                      <span className="text-[10px] font-bold text-[#8A7338]">Safe ✓</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            {/* Authorize & Place Order Footer */}
            <div className="p-5 border-t border-[#E7E8EB] bg-[#FCFBF8] space-y-3">
              <div className="flex justify-between items-center text-xs text-[#71717A]">
                <span>Total Chargeable:</span>
                <span className="text-base font-bold text-[#383638]">{formatCurrency(finalTotal)}</span>
              </div>

              <button
                onClick={handlePlaceOrder}
                disabled={isSubmitting}
                className="w-full py-3 rounded-xl bg-[#383638] text-white font-semibold text-xs uppercase tracking-wider hover:bg-black transition-all shadow-md flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {isSubmitting ? (
                  <>
                    <FashionLoader size="small" messageIndex={1} />
                  </>
                ) : (
                  <>
                    <Lock className="w-3.5 h-3.5 text-[#C5A55A]" />
                    <span>Authorize & Confirm Order</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* ===================== STEP 3: ORDER CONFIRMED ===================== */}
        {step === 'success' && (
          <div className="flex-1 p-6 flex flex-col items-center justify-center text-center space-y-5 overflow-y-auto">
            <div className="w-16 h-16 rounded-full bg-[#E8EFE5] border border-[#8BA888] flex items-center justify-center shadow-sm">
              <CheckCircle2 className="w-9 h-9 text-[#059669]" />
            </div>

            <div>
              <span className="text-[10px] font-bold tracking-widest text-[#8A7338] uppercase">
                Order Confirmed
              </span>
              <h2 className="text-xl font-bold text-[#383638] mt-1">
                Thank you, {name}!
              </h2>
              <p className="text-xs text-[#71717A] mt-1 max-w-xs mx-auto">
                Your order is now being registered in BizGuard AI&apos;s real-time transactional state machine.
              </p>
            </div>

            {createdOrder && (
              <div className="w-full p-4 rounded-2xl bg-[#FCFBF8] border border-[#E7E8EB] text-left text-xs space-y-2 font-mono">
                <div className="flex justify-between">
                  <span className="text-[#8C95A0]">Order Reference:</span>
                  <span className="font-bold text-[#383638]">{createdOrder.order_number}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#8C95A0]">Status:</span>
                  <span className="text-[#059669] font-bold">{createdOrder.status}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#8C95A0]">Authorized Total:</span>
                  <span className="font-bold text-[#383638]">{formatCurrency(createdOrder.total_amount)}</span>
                </div>
              </div>
            )}

            <div className="w-full space-y-2">
              <Link
                href="/workflows"
                onClick={handleClose}
                className="w-full py-2.5 rounded-xl bg-[#383638] text-white text-xs font-semibold hover:bg-black transition-colors block text-center"
              >
                Track in Workflow Monitor →
              </Link>
              <button
                onClick={handleClose}
                className="w-full py-2.5 rounded-xl border border-[#E7E8EB] text-[#383638] text-xs font-semibold hover:bg-[#FAF5EF] transition-colors"
              >
                Continue Boutique Browsing
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
