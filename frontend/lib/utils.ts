import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number | string | null | undefined): string {
  if (amount === null || amount === undefined) return '—';
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(Number(amount));
}

export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata', dateStyle: 'medium', timeStyle: 'short' });
}

export function getStatusColor(status: string): string {
  const map: Record<string, string> = {
    // Orders
    PENDING: 'bg-[#FFFBEB] text-[#92400E] border-[#FDE68A]',
    PAYMENT_CAPTURED: 'bg-[#EFF6FF] text-[#1E40AF] border-[#BFDBFE]',
    INVENTORY_ALLOCATED: 'bg-[#FAF5FF] text-[#6B21A8] border-[#E9D5FF]',
    INVOICED: 'bg-[#FDF2F4] text-[#9D435F] border-[#FBCFE8]',
    SHIPPED: 'bg-[#ECFEFF] text-[#155E75] border-[#A5F3FC]',
    DELIVERED: 'bg-[#ECFDF5] text-[#065F46] border-[#A7F3D0]',
    STALLED_INCONSISTENT: 'bg-[#FFF1F2] text-[#9F1239] border-[#FECDD3]',
    CANCELLED: 'bg-[#F3F4F6] text-[#4B5563] border-[#E5E7EB]',
    // Incidents
    DETECTED: 'bg-[#FFF1F2] text-[#9F1239] border-[#FECDD3]',
    INVESTIGATING: 'bg-[#FFF7ED] text-[#9A3412] border-[#FED7AA]',
    PROPOSAL_READY: 'bg-[#EFF6FF] text-[#1E40AF] border-[#BFDBFE]',
    AWAITING_APPROVAL: 'bg-[#FEFCE8] text-[#854D0E] border-[#FEF08A]',
    EXECUTING_FIX: 'bg-[#FAF5FF] text-[#6B21A8] border-[#E9D5FF]',
    VERIFIED_RESOLVED: 'bg-[#ECFDF5] text-[#065F46] border-[#A7F3D0]',
    CLOSED: 'bg-[#F3F4F6] text-[#4B5563] border-[#E5E7EB]',
    // Workflows
    RUNNING: 'bg-[#EFF6FF] text-[#1E40AF] border-[#BFDBFE]',
    COMPLETED: 'bg-[#ECFDF5] text-[#065F46] border-[#A7F3D0]',
    FAILED: 'bg-[#FFF1F2] text-[#9F1239] border-[#FECDD3]',
    STALLED_INCONSISTENT_WF: 'bg-[#FFF1F2] text-[#9F1239] border-[#FECDD3]',
    COMPENSATED: 'bg-[#FDF2F4] text-[#9D435F] border-[#FBCFE8]',
    // Proposals
    DRAFTED: 'bg-[#F3F4F6] text-[#4B5563] border-[#E5E7EB]',
    READY_FOR_REVIEW: 'bg-[#FEFCE8] text-[#854D0E] border-[#FEF08A]',
    APPROVED: 'bg-[#ECFDF5] text-[#065F46] border-[#A7F3D0]',
    REJECTED: 'bg-[#FFF1F2] text-[#9F1239] border-[#FECDD3]',
    EXECUTED: 'bg-[#FAF5FF] text-[#6B21A8] border-[#E9D5FF]',
    // Inventory
    HEALTHY: 'bg-[#ECFDF5] text-[#065F46] border-[#A7F3D0]',
    LOW_STOCK: 'bg-[#FFFBEB] text-[#92400E] border-[#FDE68A]',
    OUT_OF_STOCK: 'bg-[#FFF1F2] text-[#9F1239] border-[#FECDD3]',
    // Payments
    CAPTURED: 'bg-[#ECFDF5] text-[#065F46] border-[#A7F3D0]',
    INITIATED: 'bg-[#EFF6FF] text-[#1E40AF] border-[#BFDBFE]',
    REFUNDED: 'bg-[#FDF2F4] text-[#9D435F] border-[#FBCFE8]',
    // Shipment
    MANIFESTED: 'bg-[#EFF6FF] text-[#1E40AF] border-[#BFDBFE]',
    PICKED_UP: 'bg-[#FAF5FF] text-[#6B21A8] border-[#E9D5FF]',
    IN_TRANSIT: 'bg-[#ECFEFF] text-[#155E75] border-[#A5F3FC]',
    ON_HOLD: 'bg-[#FFFBEB] text-[#92400E] border-[#FDE68A]',
    // Returns
    REQUESTED: 'bg-[#FFFBEB] text-[#92400E] border-[#FDE68A]',
    RESTOCKED: 'bg-[#ECFDF5] text-[#065F46] border-[#A7F3D0]',
    // Generic
    SUCCESS: 'bg-[#ECFDF5] text-[#065F46] border-[#A7F3D0]',
    ERROR: 'bg-[#FFF1F2] text-[#9F1239] border-[#FECDD3]',
    INVARIANT_BREACH: 'bg-[#FFE4E6] text-[#881337] border-[#FDA4AF]',
  };
  return map[status] || 'bg-[#F3F4F6] text-[#4B5563] border-[#E5E7EB]';
}

export function getSeverityColor(severity: string): string {
  const map: Record<string, string> = {
    CRITICAL: 'bg-[#BE123C] text-white',
    HIGH: 'bg-[#EA580C] text-white',
    MEDIUM: 'bg-[#CA8A04] text-white',
    LOW: 'bg-[#2563EB] text-white',
  };
  return map[severity] || 'bg-[#4B5563] text-white';
}
