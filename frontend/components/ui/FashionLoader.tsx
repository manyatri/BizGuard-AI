'use client';

import { useState, useEffect } from 'react';
import { Shield } from 'lucide-react';

const MESSAGES = [
  'Preparing your store...',
  'Synchronizing your business operations...',
  'Getting your AI operations team ready...',
];

// Elegant SVG editorial vector garments
export function KurtiIcon({ className = 'w-6 h-6' }: { className?: string }) {
  return (
    <svg viewBox="0 0 40 40" className={className} fill="none" stroke="currentColor">
      {/* Kurti silhouette with mandarin collar & side slits */}
      <path
        d="M14 6 L20 10 L26 6 L33 13 L29 17 L27 15 L28 34 L23 34 L23 26 L17 26 L17 34 L12 34 L13 15 L11 17 L7 13 Z"
        fill="#F8E5E9"
        stroke="#D9A9B5"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      {/* Embroidery placket detail */}
      <path d="M20 10 L20 20" stroke="#C5A55A" strokeWidth="1.2" strokeLinecap="round" />
      <circle cx="20" cy="13" r="0.75" fill="#C5A55A" />
      <circle cx="20" cy="16" r="0.75" fill="#C5A55A" />
      <circle cx="20" cy="19" r="0.75" fill="#C5A55A" />
    </svg>
  );
}

export function DressIcon({ className = 'w-6 h-6' }: { className?: string }) {
  return (
    <svg viewBox="0 0 40 40" className={className} fill="none" stroke="currentColor">
      {/* Flowing A-line evening dress */}
      <path
        d="M16 6 C18 9 22 9 24 6 L27 12 C25 14 24 16 25 19 L32 35 L8 35 L15 19 C16 16 15 14 13 12 Z"
        fill="#E4EFF8"
        stroke="#9BB7D4"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      {/* Subtle waist sash */}
      <path d="M15 19 Q20 21 25 19" stroke="#E9D8B5" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}

export function ShirtIcon({ className = 'w-6 h-6' }: { className?: string }) {
  return (
    <svg viewBox="0 0 40 40" className={className} fill="none" stroke="currentColor">
      {/* Tailored button-up shirt */}
      <path
        d="M15 8 L20 11 L25 8 L32 14 L28 17 L27 15 L27 34 L13 34 L13 15 L12 17 L8 14 Z"
        fill="#E8EFE5"
        stroke="#8BA888"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      {/* Collar & Buttons */}
      <path d="M15 8 L20 12 L25 8" stroke="#383638" strokeWidth="1.2" />
      <line x1="20" y1="12" x2="20" y2="34" stroke="#383638" strokeWidth="1" strokeDasharray="1 3" />
    </svg>
  );
}

export function JeansIcon({ className = 'w-6 h-6' }: { className?: string }) {
  return (
    <svg viewBox="0 0 40 40" className={className} fill="none" stroke="currentColor">
      {/* Denim jeans with pocket curves */}
      <path
        d="M12 9 L28 9 L29 34 L22 34 L20 18 L18 34 L11 34 Z"
        fill="#E4EFF8"
        stroke="#5B7E9F"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      {/* Belt waistband & rivet */}
      <line x1="12" y1="12" x2="28" y2="12" stroke="#E9D8B5" strokeWidth="1.2" />
      <path d="M13 12 Q16 16 17 12" stroke="#5B7E9F" strokeWidth="1" />
      <path d="M27 12 Q24 16 23 12" stroke="#5B7E9F" strokeWidth="1" />
    </svg>
  );
}

export function TrousersIcon({ className = 'w-6 h-6' }: { className?: string }) {
  return (
    <svg viewBox="0 0 40 40" className={className} fill="none" stroke="currentColor">
      {/* Pleated wide-leg trousers */}
      <path
        d="M13 8 L27 8 L29 35 L22 35 L20 20 L18 35 L11 35 Z"
        fill="#FAF5EF"
        stroke="#B3A382"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      {/* Center pressed crease lines */}
      <line x1="15" y1="12" x2="15" y2="34" stroke="#D9CEB8" strokeWidth="1" strokeDasharray="3 2" />
      <line x1="25" y1="12" x2="25" y2="34" stroke="#D9CEB8" strokeWidth="1" strokeDasharray="3 2" />
    </svg>
  );
}

export default function FashionLoader({
  messageIndex,
  size = 'default',
  fullscreen = false,
}: {
  messageIndex?: number;
  size?: 'small' | 'default' | 'large';
  fullscreen?: boolean;
}) {
  const [currentIdx, setCurrentIdx] = useState(messageIndex ?? 0);

  useEffect(() => {
    if (messageIndex !== undefined) return;
    const interval = setInterval(() => {
      setCurrentIdx(prev => (prev + 1) % MESSAGES.length);
    }, 2800);
    return () => clearInterval(interval);
  }, [messageIndex]);

  const radius = size === 'small' ? 44 : size === 'large' ? 88 : 64;
  const containerSize = radius * 2 + 50;

  // 5 garments evenly distributed at 72 degrees each
  const garments = [
    { name: 'Kurti', component: KurtiIcon, angle: 0 },
    { name: 'Dress', component: DressIcon, angle: 72 },
    { name: 'Shirt', component: ShirtIcon, angle: 144 },
    { name: 'Jeans', component: JeansIcon, angle: 216 },
    { name: 'Trousers', component: TrousersIcon, angle: 288 },
  ];

  return (
    <div
      className={`flex flex-col items-center justify-center p-6 ${
        fullscreen ? 'fixed inset-0 z-50 bg-[#F8F5EF]/90 backdrop-blur-sm' : 'w-full'
      }`}
    >
      {/* Circular Rotating Orbit System */}
      <div
        className="relative flex items-center justify-center"
        style={{ width: `${containerSize}px`, height: `${containerSize}px` }}
      >
        {/* Outer subtle orbital track */}
        <div
          className="absolute rounded-full border border-dashed border-[#E9D8B5]/60 animate-[spin_24s_linear_infinite] motion-reduce:animate-none"
          style={{ width: `${radius * 2}px`, height: `${radius * 2}px` }}
        />

        {/* Inner glow halo */}
        <div
          className="absolute rounded-full bg-gradient-to-tr from-[#F8E5E9]/50 via-[#FCFBF8] to-[#E4EFF8]/50 blur-md pointer-events-none"
          style={{ width: `${radius * 1.4}px`, height: `${radius * 1.4}px` }}
        />

        {/* Rotating garments ring */}
        <div
          className="absolute inset-0 flex items-center justify-center animate-[spin_12s_linear_infinite] motion-reduce:animate-none"
        >
          {garments.map((g, idx) => {
            const rad = (g.angle * Math.PI) / 180;
            const x = Math.cos(rad) * radius;
            const y = Math.sin(rad) * radius;

            return (
              <div
                key={g.name}
                className="absolute flex items-center justify-center w-9 h-9 rounded-full bg-white/95 border border-[#E7E8EB] shadow-[0_2px_8px_rgba(56,54,56,0.06)] transform transition-transform"
                style={{
                  transform: `translate(${x}px, ${y}px)`,
                }}
              >
                {/* Counter-rotate icon so it stays upright while orbiting */}
                <div className="animate-[spin_12s_linear_infinite_reverse] motion-reduce:animate-none">
                  <g.component className="w-5 h-5 drop-shadow-xs" />
                </div>
              </div>
            );
          })}
        </div>

        {/* Central BizGuard Emblem */}
        <div className="relative z-10 flex flex-col items-center justify-center w-14 h-14 rounded-2xl bg-[#FCFBF8] border border-[#E9D8B5] shadow-[0_4px_16px_rgba(201,165,90,0.15)] group">
          <div className="w-7 h-7 rounded-lg bg-[#FAF5E8] flex items-center justify-center border border-[#E8DCB8]">
            <Shield className="w-4 h-4 text-[#C5A55A] animate-pulse" />
          </div>
          <span className="text-[8px] font-bold tracking-widest text-[#8A7338] uppercase mt-0.5 font-mono">
            BIZGUARD
          </span>
        </div>
      </div>

      {/* Dynamic Cycling Message */}
      <div className="mt-5 text-center min-h-[32px]">
        <p className="text-xs font-semibold tracking-wide text-[#383638] transition-opacity duration-300">
          {MESSAGES[currentIdx]}
        </p>
        <div className="flex items-center justify-center gap-1.5 mt-2">
          {MESSAGES.map((_, i) => (
            <span
              key={i}
              className={`h-1 rounded-full transition-all duration-300 ${
                i === currentIdx ? 'w-4 bg-[#C5A55A]' : 'w-1 bg-[#E7E8EB]'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
