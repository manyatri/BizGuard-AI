'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import { useCart } from '@/lib/cart-context';
import {
  Compass, LayoutDashboard, GitBranch, Bug, BrainCircuit,
  CheckSquare, BarChart3, Settings, Shield, ChevronLeft, ChevronRight,
  Package, Boxes, ShoppingCart, CreditCard, Sparkles, Menu, X, CircleDot,
  ShoppingBag
} from 'lucide-react';

export const PRIMARY_NAV = [
  { href: '/', label: 'Overview / Home', icon: Compass, exact: true },
  { href: '/operations', label: 'Business Operations', icon: LayoutDashboard },
  { href: '/workflows', label: 'Workflow Monitor', icon: GitBranch },
  { href: '/bugs', label: 'Bug Detection & Simulator', icon: Bug },
  { href: '/war-room', label: 'AI War Rooms', icon: BrainCircuit },
  { href: '/approvals', label: 'Approval Center', icon: CheckSquare },
  { href: '/analytics', label: 'Reliability Analytics', icon: BarChart3 },
  { href: '/settings', label: 'Settings & Integrations', icon: Settings },
];

export const COMMERCE_NAV = [
  { href: '/products', label: 'Product Catalog', icon: Package },
  { href: '/inventory', label: 'Inventory Matrix', icon: Boxes },
  { href: '/orders', label: 'Orders & Fulfillment', icon: ShoppingCart },
  { href: '/payments', label: 'Payments & Invoices', icon: CreditCard },
  { href: '/runway', label: 'Try The Look (Streetwear)', icon: Sparkles },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { totalItems, setIsBagOpen } = useCart();

  const isActive = (href: string, exact?: boolean) => {
    if (exact || href === '/') return pathname === '/';
    return pathname.startsWith(href);
  };

  return (
    <>
      {/* Mobile Toggle Button */}
      <div className="lg:hidden fixed top-3 left-3 z-50 flex items-center gap-2">
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="p-2 rounded-xl bg-white/95 backdrop-blur-md shadow-md border border-[#E7E8EB] text-[#383638] hover:bg-[#F8E5E9] transition-colors"
          aria-label="Toggle navigation"
        >
          {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5 text-[#C5A55A]" />}
        </button>

        {/* Mobile Bag Trigger */}
        <button
          onClick={() => setIsBagOpen(true)}
          className="p-2 rounded-xl bg-[#FCFBF8] border border-[#E7E8EB] shadow-md text-[#383638] flex items-center gap-1.5"
          aria-label="Open Shopping Bag"
        >
          <ShoppingBag className="w-4 h-4 text-[#9D435F]" />
          {totalItems > 0 && (
            <span className="w-4 h-4 rounded-full bg-[#9D435F] text-white text-[10px] font-bold flex items-center justify-center">
              {totalItems}
            </span>
          )}
        </button>
      </div>

      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div
          onClick={() => setMobileOpen(false)}
          className="lg:hidden fixed inset-0 bg-black/30 backdrop-blur-xs z-40 transition-opacity"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed lg:static top-0 bottom-0 left-0 z-40 flex flex-col bg-[#FCFBF8] border-r border-[#E7E8EB] shadow-[1px_0_12px_rgba(56,54,56,0.03)] transition-all duration-300 ease-in-out shrink-0 select-none ${
          collapsed ? 'w-[72px]' : 'w-64'
        } ${mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}
      >
        {/* Brand Header */}
        <div className="h-16 px-4 border-b border-[#E7E8EB] flex items-center justify-between bg-[#FAF5EF]">
          <Link
            href="/"
            className="flex items-center gap-3 overflow-hidden text-left"
            onClick={() => setMobileOpen(false)}
          >
            <div className="w-9 h-9 rounded-xl bg-[#FCFBF8] border border-[#E9D8B5] flex items-center justify-center shrink-0 shadow-xs">
              <Shield className="w-5 h-5 text-[#C5A55A]" />
            </div>
            {!collapsed && (
              <div className="min-w-0">
                <div className="font-bold text-sm tracking-[0.14em] text-[#383638] uppercase font-mono leading-none">
                  BizGuard
                </div>
                <div className="text-[10px] tracking-wider text-[#8A7338] font-medium uppercase mt-1 leading-none">
                  Reliability AI
                </div>
              </div>
            )}
          </Link>

          {/* Desktop Collapse Toggle */}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="hidden lg:flex w-6 h-6 rounded-md border border-[#E7E8EB] items-center justify-center text-[#8C95A0] hover:text-[#383638] hover:bg-[#FAF5EF] transition-colors"
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* Shopping Bag Fast Launcher */}
        <div className="px-3 pt-3">
          <button
            onClick={() => setIsBagOpen(true)}
            className={`w-full flex items-center justify-between px-3 py-2 rounded-xl bg-[#F8E5E9] border border-[#D9A9B5] text-[#9D435F] hover:bg-[#F4DDE4] transition-all shadow-xs group ${
              collapsed ? 'justify-center px-0' : ''
            }`}
            title="Open Styling Bag"
          >
            <div className="flex items-center gap-2.5">
              <ShoppingBag className="w-4 h-4 text-[#9D435F] group-hover:scale-110 transition-transform" />
              {!collapsed && (
                <span className="text-xs font-bold tracking-tight">Styling Bag</span>
              )}
            </div>
            {!collapsed ? (
              <span className="px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-[#9D435F] text-white">
                {totalItems}
              </span>
            ) : totalItems > 0 ? (
              <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-[#9D435F]" />
            ) : null}
          </button>
        </div>

        {/* System Status Pill */}
        {!collapsed && (
          <div className="mx-3 mt-2 px-3 py-1.5 rounded-xl bg-[#E8EFE5] border border-[#8BA888]/40 text-[#059669] flex items-center gap-2 text-[11px]">
            <CircleDot className="w-3.5 h-3.5 text-[#059669] animate-pulse shrink-0" />
            <span className="font-semibold truncate">Autonomous Engine: Active</span>
          </div>
        )}

        {/* Scrollable Navigation */}
        <div className="flex-1 py-3 px-2 space-y-5 overflow-y-auto overflow-x-hidden">
          {/* Primary Operations Section */}
          <div>
            {!collapsed && (
              <div className="px-3 mb-1.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-[#8C95A0]">
                Platform Control
              </div>
            )}
            <ul className="space-y-0.5">
              {PRIMARY_NAV.map(({ href, label, icon: Icon, exact }) => {
                const active = isActive(href, exact);
                return (
                  <li key={href}>
                    <Link
                      href={href}
                      onClick={() => setMobileOpen(false)}
                      title={collapsed ? label : undefined}
                      className={`group flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold transition-all ${
                        active
                          ? 'bg-[#F8E5E9] text-[#9D435F] border-l-3 border-[#C5A55A] shadow-xs'
                          : 'text-[#4B5563] hover:text-[#383638] hover:bg-[#FAF5EF]'
                      } ${collapsed ? 'justify-center px-0' : ''}`}
                    >
                      <Icon
                        className={`w-4 h-4 shrink-0 transition-colors ${
                          active ? 'text-[#C5A55A]' : 'text-[#8C95A0] group-hover:text-[#383638]'
                        }`}
                      />
                      {!collapsed && <span className="truncate">{label}</span>}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>

          {/* Commerce & Inventory Section */}
          <div className="pt-2 border-t border-[#E7E8EB]">
            {!collapsed && (
              <div className="px-3 mb-1.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-[#8C95A0]">
                Store & Inventory
              </div>
            )}
            <ul className="space-y-0.5">
              {COMMERCE_NAV.map(({ href, label, icon: Icon }) => {
                const active = isActive(href);
                return (
                  <li key={href}>
                    <Link
                      href={href}
                      onClick={() => setMobileOpen(false)}
                      title={collapsed ? label : undefined}
                      className={`group flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold transition-all ${
                        active
                          ? 'bg-[#E4EFF8] text-[#1E40AF] border-l-3 border-[#C5A55A] shadow-xs'
                          : 'text-[#4B5563] hover:text-[#383638] hover:bg-[#FAF5EF]'
                      } ${collapsed ? 'justify-center px-0' : ''}`}
                    >
                      <Icon
                        className={`w-4 h-4 shrink-0 transition-colors ${
                          active ? 'text-[#C5A55A]' : 'text-[#8C95A0] group-hover:text-[#383638]'
                        }`}
                      />
                      {!collapsed && <span className="truncate">{label}</span>}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>

        {/* Sidebar Footer */}
        <div className="p-3 border-t border-[#E7E8EB] bg-[#FAF5EF] text-[11px] text-[#8C95A0]">
          {!collapsed ? (
            <div className="flex items-center justify-between">
              <div>
                <div className="font-semibold text-[#383638]">Maison Vell x BizGuard</div>
                <div className="text-[10px] text-[#8C95A0]">Zero-Downtime E-Commerce</div>
              </div>
              <span className="px-1.5 py-0.5 rounded text-[9px] font-bold tracking-wider bg-[#E9D8B5] text-[#785E20] border border-[#C5A55A]/40">
                PROD
              </span>
            </div>
          ) : (
            <div className="text-center font-mono text-[9px] text-[#C5A55A]">v1.0</div>
          )}
        </div>
      </aside>
    </>
  );
}
