'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowRight, RefreshCw, ShoppingBag } from 'lucide-react';

export type EmptyStateType =
  | 'no-products'
  | 'no-incidents'
  | 'no-approvals'
  | 'no-workflows'
  | 'no-orders'
  | 'empty-bag';

interface EmptyStateProps {
  type: EmptyStateType;
  title?: string;
  description?: string;
  actionText?: string;
  actionHref?: string;
  onAction?: () => void;
  className?: string;
}

export function EditorialFashionRackIllustration() {
  return (
    <svg viewBox="0 0 160 120" className="w-40 h-28 mx-auto mb-3" fill="none">
      {/* Designer Studio Garment Rack */}
      <line x1="20" y1="110" x2="140" y2="110" stroke="#E7E8EB" strokeWidth="2.5" strokeLinecap="round" />
      <line x1="35" y1="110" x2="35" y2="25" stroke="#D9CEB8" strokeWidth="2" />
      <line x1="125" y1="110" x2="125" y2="25" stroke="#D9CEB8" strokeWidth="2" />
      <line x1="28" y1="25" x2="132" y2="25" stroke="#C5A55A" strokeWidth="2.5" strokeLinecap="round" />
      {/* Floating empty rose-gold hangers */}
      <path d="M60 25 C60 18 68 18 68 25 L80 34 L56 34 Z" stroke="#D9A9B5" strokeWidth="1.5" fill="#F8E5E9" />
      <path d="M92 25 C92 18 100 18 100 25 L112 34 L88 34 Z" stroke="#9BB7D4" strokeWidth="1.5" fill="#E4EFF8" />
      {/* Floor wheels */}
      <circle cx="35" cy="112" r="3" fill="#383638" />
      <circle cx="125" cy="112" r="3" fill="#383638" />
      {/* Gentle floating atelier sparkle */}
      <path d="M80 55 L82 60 L87 62 L82 64 L80 69 L78 64 L73 62 L78 60 Z" fill="#E9D8B5" />
    </svg>
  );
}

export function EditorialMannequinIllustration() {
  return (
    <svg viewBox="0 0 160 120" className="w-40 h-28 mx-auto mb-3" fill="none">
      {/* Soft circular pastel aura */}
      <circle cx="80" cy="60" r="46" fill="#E8EFE5" fillOpacity="0.45" />
      {/* Classical dressmaker dress-form mannequin */}
      <path
        d="M72 32 C74 38 72 48 68 54 C66 58 66 65 70 70 L90 70 C94 65 94 58 92 54 C88 48 86 38 88 32 C84 34 76 34 72 32 Z"
        fill="#FCFBF8"
        stroke="#8BA888"
        strokeWidth="1.5"
      />
      {/* Stand and tripod base */}
      <line x1="80" y1="70" x2="80" y2="108" stroke="#383638" strokeWidth="2" />
      <path d="M66 112 L80 108 L94 112" stroke="#383638" strokeWidth="2" strokeLinecap="round" />
      <circle cx="80" cy="27" r="3.5" fill="#C5A55A" />
      {/* Green laurels / peaceful check badge */}
      <path d="M54 50 C54 62 62 72 74 74" stroke="#8BA888" strokeWidth="1.5" strokeDasharray="2 3" />
      <path d="M106 50 C106 62 98 72 86 74" stroke="#8BA888" strokeWidth="1.5" strokeDasharray="2 3" />
      <circle cx="80" cy="50" r="7" fill="#E8EFE5" stroke="#059669" strokeWidth="1.2" />
      <path d="M77 50 L79 52 L83 48" stroke="#059669" strokeWidth="1.4" strokeLinecap="round" />
    </svg>
  );
}

export function EditorialApprovalSealIllustration() {
  return (
    <svg viewBox="0 0 160 120" className="w-40 h-28 mx-auto mb-3" fill="none">
      {/* Soft warm ivory aura */}
      <circle cx="80" cy="56" r="44" fill="#FAF5EF" />
      {/* Quality ribbon rosette */}
      <path d="M66 68 L60 102 L72 96 L80 102 L78 72" fill="#F8E5E9" stroke="#D9A9B5" strokeWidth="1.2" />
      <path d="M94 68 L100 102 L88 96 L80 102 L82 72" fill="#E4EFF8" stroke="#9BB7D4" strokeWidth="1.2" />
      {/* Gold Medallion */}
      <circle cx="80" cy="52" r="24" fill="#FCFBF8" stroke="#C5A55A" strokeWidth="2" />
      <circle cx="80" cy="52" r="20" stroke="#E9D8B5" strokeWidth="1" strokeDasharray="3 2" />
      {/* Elegant quill */}
      <path d="M72 54 L88 38 C90 36 93 39 91 41 L76 56 L71 58 Z" fill="#E9D8B5" stroke="#C5A55A" strokeWidth="1" />
    </svg>
  );
}

export function EditorialWorkflowLoomIllustration() {
  return (
    <svg viewBox="0 0 160 120" className="w-40 h-28 mx-auto mb-3" fill="none">
      {/* Soft powder blue aura */}
      <circle cx="80" cy="58" r="44" fill="#E4EFF8" fillOpacity="0.5" />
      {/* Silk thread weaving / State machine nodes */}
      <line x1="30" y1="58" x2="130" y2="58" stroke="#E7E8EB" strokeWidth="2" strokeDasharray="4 4" />
      {/* Nodes */}
      <circle cx="45" cy="58" r="9" fill="#FCFBF8" stroke="#8BA888" strokeWidth="1.5" />
      <circle cx="45" cy="58" r="3" fill="#059669" />
      <circle cx="80" cy="58" r="11" fill="#FCFBF8" stroke="#C5A55A" strokeWidth="2" />
      <circle cx="80" cy="58" r="4" fill="#C5A55A" />
      <circle cx="115" cy="58" r="9" fill="#FCFBF8" stroke="#9BB7D4" strokeWidth="1.5" />
      <circle cx="115" cy="58" r="3" fill="#2563EB" />
      {/* Curved silk ribbon */}
      <path d="M45 58 Q80 28 115 58" stroke="#D9A9B5" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}

export function EditorialShoppingBoxIllustration() {
  return (
    <svg viewBox="0 0 160 120" className="w-40 h-28 mx-auto mb-3" fill="none">
      {/* Luxury ribboned boutique packaging box */}
      <rect x="44" y="44" width="72" height="58" rx="6" fill="#FCFBF8" stroke="#E7E8EB" strokeWidth="1.5" />
      <rect x="40" y="38" width="80" height="14" rx="3" fill="#F8E5E9" stroke="#D9A9B5" strokeWidth="1.2" />
      {/* Ribbon */}
      <line x1="80" y1="38" x2="80" y2="102" stroke="#C5A55A" strokeWidth="2" />
      {/* Bow */}
      <path d="M80 38 C72 26 62 34 76 38 Z" fill="#E9D8B5" stroke="#C5A55A" strokeWidth="1.2" />
      <path d="M80 38 C88 26 98 34 84 38 Z" fill="#E9D8B5" stroke="#C5A55A" strokeWidth="1.2" />
      <circle cx="80" cy="38" r="2.5" fill="#383638" />
    </svg>
  );
}

export function EditorialToteBagIllustration() {
  return (
    <svg viewBox="0 0 160 120" className="w-40 h-28 mx-auto mb-3" fill="none">
      {/* Chic luxury canvas tote bag */}
      <path
        d="M48 42 L112 42 L106 102 C106 105 103 108 99 108 L61 108 C57 108 54 105 54 102 Z"
        fill="#FCFBF8"
        stroke="#D9CEB8"
        strokeWidth="1.5"
      />
      {/* Twin leather handles */}
      <path d="M64 42 C64 20 74 18 80 18 C86 18 96 20 96 42" stroke="#C5A55A" strokeWidth="2" fill="none" strokeLinecap="round" />
      {/* Soft brand tag */}
      <rect x="74" y="62" width="12" height="18" rx="2" fill="#F8E5E9" stroke="#D9A9B5" strokeWidth="1" />
      <line x1="80" y1="52" x2="80" y2="62" stroke="#383638" strokeWidth="1" />
      {/* Decorative floral twig */}
      <path d="M100 48 Q114 36 122 42" stroke="#8BA888" strokeWidth="1.2" fill="none" />
      <ellipse cx="122" cy="42" rx="3" ry="2" fill="#E8EFE5" stroke="#8BA888" strokeWidth="1" />
    </svg>
  );
}

const DEFAULTS: Record<EmptyStateType, { title: string; desc: string; illustration: React.FC }> = {
  'no-products': {
    title: 'No Garments Found',
    desc: 'There are no clothing pieces matching your selected filter. Explore our new season collections or reset filters.',
    illustration: EditorialFashionRackIllustration,
  },
  'no-incidents': {
    title: 'All Invariants In Perfect Harmony',
    desc: 'Zero anomalies or state drift detected. All business logic, reservations, and transactional pipelines are healthy.',
    illustration: EditorialMannequinIllustration,
  },
  'no-approvals': {
    title: 'Approval Center Clear',
    desc: 'No proposals currently require supervisor signature. Autonomous pre-checks have verified all orders.',
    illustration: EditorialApprovalSealIllustration,
  },
  'no-workflows': {
    title: 'No Workflow Disruptions',
    desc: 'All state transitions and order fulfillments are completing without bottlenecks or invariant blocks.',
    illustration: EditorialWorkflowLoomIllustration,
  },
  'no-orders': {
    title: 'No Transactions Registered',
    desc: 'The transaction ledger is ready for new customer purchases. Test an order from the live boutique lookbook.',
    illustration: EditorialShoppingBoxIllustration,
  },
  'empty-bag': {
    title: 'Your Styling Bag Is Empty',
    desc: 'Discover tailored silhouettes, curated ensembles, and artisanal kurtis from the Maison Vell collection.',
    illustration: EditorialToteBagIllustration,
  },
};

export default function EmptyState({
  type,
  title,
  description,
  actionText,
  actionHref,
  onAction,
  className = '',
}: EmptyStateProps) {
  const config = DEFAULTS[type];
  const Illustration = config.illustration;

  return (
    <div
      className={`flex flex-col items-center justify-center p-8 lg:p-12 text-center rounded-2xl bg-[#FCFBF8] border border-[#E7E8EB] shadow-[0_2px_12px_rgba(56,54,56,0.02)] ${className}`}
    >
      <Illustration />
      <h3 className="text-base font-bold text-[#383638] tracking-tight mb-1.5">
        {title || config.title}
      </h3>
      <p className="text-xs text-[#71717A] max-w-md leading-relaxed mb-5">
        {description || config.desc}
      </p>

      {actionText && (
        <div>
          {actionHref ? (
            <Link
              href={actionHref}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-[#383638] text-white hover:bg-black transition-all shadow-xs"
            >
              <span>{actionText}</span>
              <ArrowRight className="w-3.5 h-3.5 text-[#C5A55A]" />
            </Link>
          ) : onAction ? (
            <button
              onClick={onAction}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-[#383638] text-white hover:bg-black transition-all shadow-xs"
            >
              <span>{actionText}</span>
              <ArrowRight className="w-3.5 h-3.5 text-[#C5A55A]" />
            </button>
          ) : null}
        </div>
      )}
    </div>
  );
}
