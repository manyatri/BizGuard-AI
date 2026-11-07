'use client';

import { useCart } from '@/lib/cart-context';
import { ShoppingBag, X, Check } from 'lucide-react';

export default function ToastNotification() {
  const { toast, dismissToast, setIsBagOpen } = useCart();

  if (!toast) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 animate-[slideUp_0.35s_cubic-bezier(0.16,1,0.3,1)]">
      <div className="flex items-center gap-3.5 p-3.5 rounded-2xl bg-[#FCFBF8] border border-[#E9D8B5] shadow-[0_8px_30px_rgba(56,54,56,0.12)] max-w-md backdrop-blur-md">
        {toast.image ? (
          <div className="w-11 h-11 rounded-xl overflow-hidden bg-[#FAF5EF] border border-[#E7E8EB] shrink-0 p-1">
            <img src={toast.image} alt="" className="w-full h-full object-contain" />
          </div>
        ) : (
          <div className="w-10 h-10 rounded-xl bg-[#F8E5E9] border border-[#D9A9B5] flex items-center justify-center shrink-0">
            <Check className="w-5 h-5 text-[#9D435F]" />
          </div>
        )}

        <div className="min-w-0 pr-2">
          <div className="flex items-center gap-1.5">
            <span className="text-[11px] font-bold tracking-wider text-[#8A7338] uppercase">
              {toast.title}
            </span>
          </div>
          <div className="text-xs font-semibold text-[#383638] truncate mt-0.5">
            {toast.message}
          </div>
        </div>

        <button
          onClick={() => {
            dismissToast();
            setIsBagOpen(true);
          }}
          className="px-3 py-1.5 rounded-lg text-xs font-bold bg-[#383638] text-white hover:bg-black transition-colors shrink-0 shadow-xs"
        >
          View Bag
        </button>

        <button
          onClick={dismissToast}
          className="text-[#8C95A0] hover:text-[#383638] p-1 transition-colors"
          aria-label="Dismiss notification"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
