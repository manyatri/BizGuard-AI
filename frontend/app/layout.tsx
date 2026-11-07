import type { Metadata } from 'next';
import './globals.css';
import Sidebar from '@/components/layout/Sidebar';
import { CartProvider } from '@/lib/cart-context';
import ShoppingBagDrawer from '@/components/shop/ShoppingBagDrawer';
import ToastNotification from '@/components/ui/ToastNotification';

export const metadata: Metadata = {
  title: 'BizGuard AI — Autonomous E-Commerce Reliability & Recovery',
  description: 'Zero-Downtime Autonomous Business Reliability and Recovery Platform for Clothing E-Commerce',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <body className="font-sans antialiased h-full text-[#383638] bg-[#FAF5EF] selection:bg-[#F8E5E9] selection:text-[#9D435F]">
        <CartProvider>
          <div className="flex h-screen w-screen overflow-hidden bg-[#FAF5EF]">
            <Sidebar />
            <div className="flex-1 min-w-0 h-full overflow-hidden flex flex-col relative">
              {children}
            </div>
          </div>
          <ShoppingBagDrawer />
          <ToastNotification />
        </CartProvider>
      </body>
    </html>
  );
}
