'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Shield, ShoppingBag, ArrowLeft } from 'lucide-react';
import { useCart } from '@/lib/cart-context';

interface CartItem {
  id: string;
  name: string;
  price: number;
  size: string;
  quantity: number;
  image: string;
}

const LOOKS = [
  {
    num: '01',
    name: 'The City Edit',
    src: 'https://reel-ref-try-the-look.vercel.app/assets/model-1-640.webp',
    items: [
      { id: 'item-1', name: 'Air Jordan 12 Retro', vendor: 'Nikey | Password: 1', price: 149.00, img: 'https://reel-ref-try-the-look.vercel.app/assets/source-tatum-5-orbit-copy.webp', sizes: ['40', '41', '42', '43', '44', '45', '46'] },
      { id: 'item-2', name: 'Tshirt', vendor: 'Nike', price: 199.00, img: 'https://reel-ref-try-the-look.vercel.app/assets/source-tshirt.webp', sizes: ['S', 'L', 'M', 'XL'] },
      { id: 'item-3', name: 'Sweatshirt', vendor: 'Nike', price: 199.00, img: 'https://reel-ref-try-the-look.vercel.app/assets/source-sweatshirt.webp', sizes: ['S', 'L', 'M', 'XL'] },
    ]
  },
  {
    num: '02',
    name: 'Gallery Opening',
    src: 'https://reel-ref-try-the-look.vercel.app/assets/model-5-640.webp',
    items: [
      { id: 'item-4', name: 'Tatum 5 Orbit', vendor: 'Nikey | Password: 1', price: 149.00, img: 'https://reel-ref-try-the-look.vercel.app/assets/source-tatum-5-orbit.webp', sizes: ['40', '41', '42', '43', '44', '45', '46'] },
      { id: 'item-5', name: 'Hoodie Black', vendor: 'Nike', price: 199.00, tag: 'New', img: 'https://reel-ref-try-the-look.vercel.app/assets/source-hoodie-black.webp', sizes: ['S', 'L', 'M', 'XL'] },
      { id: 'item-6', name: 'Tshirt', vendor: 'Nike', price: 199.00, img: 'https://reel-ref-try-the-look.vercel.app/assets/source-tshirt.webp', sizes: ['S', 'L', 'M', 'XL'] },
    ]
  },
  {
    num: '03',
    name: 'Gallery Opening',
    src: 'https://reel-ref-try-the-look.vercel.app/assets/model-4-640.webp',
    items: [
      { id: 'item-7', name: 'Sweatshirt Plus', vendor: 'Nike', price: 199.00, img: 'https://reel-ref-try-the-look.vercel.app/assets/source-sweatshirt-plus.webp', sizes: ['S', 'L', 'M', 'XL'] },
      { id: 'item-8', name: 'Tatum 5 Orbit', vendor: 'Nikey | Password: 1', price: 149.00, tag: 'New', img: 'https://reel-ref-try-the-look.vercel.app/assets/source-tatum-5-orbit.webp', sizes: ['40', '41', '42', '43', '44', '45', '46'] },
      { id: 'item-9', name: 'Tshirt', vendor: 'Nike', price: 199.00, img: 'https://reel-ref-try-the-look.vercel.app/assets/source-tshirt.webp', sizes: ['S', 'L', 'M', 'XL'] },
    ]
  },
  {
    num: '04',
    name: 'Studio Day',
    src: 'https://reel-ref-try-the-look.vercel.app/assets/model-6-640.webp',
    items: [
      { id: 'item-10', name: 'Hoodie Black', vendor: 'Nike', price: 199.00, img: 'https://reel-ref-try-the-look.vercel.app/assets/source-hoodie-black.webp', sizes: ['S', 'L', 'M', 'XL'] },
      { id: 'item-11', name: 'Air Jordan 12 Retro', vendor: 'Nikey | Password: 1', price: 149.00, img: 'https://reel-ref-try-the-look.vercel.app/assets/source-tatum-5-orbit-copy.webp', sizes: ['40', '41', '42', '43', '44', '45', '46'] },
      { id: 'item-12', name: 'Tshirt', vendor: 'Nike', price: 199.00, img: 'https://reel-ref-try-the-look.vercel.app/assets/source-tshirt.webp', sizes: ['S', 'L', 'M', 'XL'] },
    ]
  },
  {
    num: '05',
    name: 'Studio Day',
    src: 'https://reel-ref-try-the-look.vercel.app/assets/model-3-640.webp',
    items: [
      { id: 'item-13', name: 'Sweatshirt', vendor: 'Nike', price: 199.00, img: 'https://reel-ref-try-the-look.vercel.app/assets/source-sweatshirt.webp', sizes: ['S', 'L', 'M', 'XL'] },
      { id: 'item-14', name: 'Tatum 5 Orbit', vendor: 'Nikey | Password: 1', price: 149.00, img: 'https://reel-ref-try-the-look.vercel.app/assets/source-tatum-5-orbit.webp', sizes: ['40', '41', '42', '43', '44', '45', '46'] },
      { id: 'item-15', name: 'Tshirt', vendor: 'Nike', price: 199.00, img: 'https://reel-ref-try-the-look.vercel.app/assets/source-tshirt.webp', sizes: ['S', 'L', 'M', 'XL'] },
    ]
  },
  {
    num: '06',
    name: 'Studio Day',
    src: 'https://reel-ref-try-the-look.vercel.app/assets/model-2-640.webp',
    items: [
      { id: 'item-16', name: 'Hoodie', vendor: 'Nike', price: 199.00, img: 'https://reel-ref-try-the-look.vercel.app/assets/source-hoodie.webp', sizes: ['S', 'L', 'M', 'XL'] },
      { id: 'item-17', name: 'Luka 5', vendor: 'Nikey | Password: 1', price: 149.00, img: 'https://reel-ref-try-the-look.vercel.app/assets/source-air-jordan-12-retro-copy.webp', sizes: ['40', '41', '42', '43', '44', '45', '46'] },
      { id: 'item-18', name: 'Tshirt', vendor: 'Nike', price: 199.00, img: 'https://reel-ref-try-the-look.vercel.app/assets/source-tshirt.webp', sizes: ['S', 'L', 'M', 'XL'] },
    ]
  }
];

export default function TryTheLookRunway() {
  const [activeIdx, setActiveIdx] = useState(0);
  const [selectedSizes, setSelectedSizes] = useState<Record<string, string>>({});
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);

  const { addToCart, setIsBagOpen, totalItems } = useCart();

  const curLook = LOOKS[activeIdx];

  useEffect(() => {
    if (!isAutoPlaying) return;
    const timer = setInterval(() => {
      setActiveIdx(prev => (prev + 1) % LOOKS.length);
    }, 5000);
    return () => clearInterval(timer);
  }, [isAutoPlaying]);

  const handleSelectSize = (itemId: string, size: string) => {
    setSelectedSizes(prev => ({ ...prev, [itemId]: size }));
  };

  const handleAddToCart = (item: any) => {
    const size = selectedSizes[item.id] || item.sizes[0];
    addToCart({
      id: `${item.id}-${size}`,
      name: item.name,
      price: item.price,
      size,
      color: 'Streetwear Edition',
      image: item.img,
    });
  };

  const handleAddFullLook = () => {
    curLook.items.forEach(item => {
      const size = selectedSizes[item.id] || item.sizes[0];
      addToCart({
        id: `${item.id}-${size}`,
        name: item.name,
        price: item.price,
        size,
        color: 'Streetwear Edition',
        image: item.img,
      });
    });
  };

  return (
    <div className="min-h-screen bg-white text-[#151413] flex flex-col font-sans select-none overflow-x-hidden">
      {/* Toast */}
      {toastMsg && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-[#151413] text-white px-5 py-3 rounded-none text-xs z-50 shadow-2xl transition-all">
          {toastMsg}
        </div>
      )}

      {/* Header */}
      <header className="h-[88px] px-10 flex items-center gap-8 border-b border-[#e4e4e4] bg-white relative z-50">
        <Link href="/" className="inline-flex items-center gap-2 mr-auto" aria-label="Runway home">
          <ArrowLeft className="w-4 h-4 text-gray-500 hover:text-black mr-2" />
          <img
            src="https://reel-ref-try-the-look.vercel.app/assets/nike-logo.svg"
            alt="Nike"
            width={68}
            height={24}
            className="w-[68px] h-[24px] object-contain"
          />
        </Link>

        <nav className="hidden md:flex gap-7 text-sm font-semibold tracking-tight text-[#151413]">
          <Link href="/" className="py-3 hover:underline underline-offset-4">Maison Vell</Link>
          <a href="#" className="py-3 underline underline-offset-4 font-bold" aria-current="page">Runway</a>
          <Link href="/operations" className="py-3 hover:underline underline-offset-4 text-rose-700 flex items-center gap-1.5 font-bold">
            <Shield className="w-3.5 h-3.5" />
            BizGuard AI Console
          </Link>
        </nav>

        <button
          onClick={() => setIsBagOpen(true)}
          className="flex items-center gap-2 p-2 hover:bg-gray-100 rounded-lg text-sm font-medium"
        >
          <ShoppingBag className="w-5 h-5 text-[#9D435F]" />
          <span className="text-xs bg-[#9D435F] text-white px-1.5 py-0.5 rounded-full font-mono">{totalItems}</span>
        </button>
      </header>

      {/* Main Runway Area */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-[1fr_380px] min-h-[calc(100vh-88px)]">
        {/* Stage */}
        <div className="relative bg-gradient-to-b from-white to-[#f5f7fa] flex flex-col justify-between p-8 lg:p-14 overflow-hidden border-r border-[#c8c8c8]">
          {/* Header intro */}
          <div>
            <h1 className="text-4xl md:text-5xl font-normal tracking-tight text-[#151413]">Try the Look.</h1>
            <p className="text-xs text-[#66625c] mt-2 max-w-md leading-relaxed">
              Six looks, styled head to toe. Tap a piece to explore size variants and complete the outfit.
            </p>
          </div>

          {/* Model Display in 3D Depth */}
          <div className="relative flex-1 flex items-center justify-center my-6">
            <div className="relative w-full max-w-md h-[460px] flex items-center justify-center">
              {LOOKS.map((look, i) => {
                const diff = (i - activeIdx + LOOKS.length) % LOOKS.length;
                const isCenter = diff === 0;
                const isLeft = diff === LOOKS.length - 1;
                const isRight = diff === 1;

                if (!isCenter && !isLeft && !isRight) return null;

                const translateX = isCenter ? '0%' : isLeft ? '-70%' : '70%';
                const scale = isCenter ? 'scale(1)' : 'scale(0.8)';
                const blur = isCenter ? 'blur(0px)' : 'blur(4px)';
                const opacity = isCenter ? '1' : '0.45';
                const zIndex = isCenter ? 20 : 10;

                return (
                  <div
                    key={look.num}
                    onClick={() => { setActiveIdx(i); setIsAutoPlaying(false); }}
                    className="absolute inset-0 flex flex-col items-center justify-end transition-all duration-700 ease-out cursor-pointer"
                    style={{
                      transform: `translateX(${translateX}) ${scale}`,
                      filter: blur,
                      opacity,
                      zIndex
                    }}
                  >
                    <img
                      src={look.src}
                      alt={look.name}
                      className="h-[430px] object-contain drop-shadow-2xl"
                    />
                    <div className="w-3/4 h-4 bg-radial-gradient from-black/20 to-transparent blur-md rounded-full mt-1"></div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Controls: Ticks + Prev/Next */}
          <div className="flex items-center justify-between gap-4 pt-6 border-t border-gray-200">
            <button
              onClick={() => { setActiveIdx(prev => (prev - 1 + LOOKS.length) % LOOKS.length); setIsAutoPlaying(false); }}
              className="p-3 border border-black/20 hover:border-black rounded-none text-xs uppercase tracking-wider font-semibold"
            >
              ← Prev
            </button>

            <div className="flex items-center gap-2 flex-1 max-w-md justify-center">
              {LOOKS.map((l, i) => (
                <button
                  key={l.num}
                  onClick={() => { setActiveIdx(i); setIsAutoPlaying(false); }}
                  className={`h-1.5 transition-all rounded-full ${i === activeIdx ? 'w-12 bg-black' : 'w-4 bg-black/20 hover:bg-black/50'}`}
                />
              ))}
            </div>

            <button
              onClick={() => { setActiveIdx(prev => (prev + 1) % LOOKS.length); setIsAutoPlaying(false); }}
              className="p-3 border border-black/20 hover:border-black rounded-none text-xs uppercase tracking-wider font-semibold"
            >
              Next →
            </button>
          </div>
        </div>

        {/* Product Panel: In this look */}
        <aside className="bg-white flex flex-col justify-between p-8 overflow-y-auto">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-[#c8c8c8] mb-6">
              <h2 className="text-lg font-normal tracking-tight">In this look</h2>
              <span className="text-[10px] tracking-widest uppercase text-[#66625c] font-mono">
                Look {curLook.num} • 3 PIECES
              </span>
            </div>

            <div className="space-y-6">
              {curLook.items.map((item, idx) => {
                const selectedSize = selectedSizes[item.id] || item.sizes[0];
                return (
                  <div key={item.id} className="border-b border-gray-100 pb-5">
                    <div className="flex gap-4 items-center">
                      <div className="relative w-20 h-24 bg-gray-50 flex items-center justify-center p-2 flex-shrink-0">
                        {item.tag && (
                          <span className="absolute top-1 left-1 bg-black text-white text-[9px] px-1.5 py-0.5 uppercase tracking-widest font-semibold">
                            {item.tag}
                          </span>
                        )}
                        <img src={item.img} alt={item.name} className="max-h-full max-w-full object-contain" />
                      </div>

                      <div className="flex-1 min-w-0">
                        <p className="text-[10px] tracking-widest uppercase text-gray-400 truncate">{item.vendor}</p>
                        <h3 className="text-sm font-medium text-[#151413] mt-0.5">{item.name}</h3>
                        <p className="text-xs font-semibold text-gray-700 mt-1">${item.price.toFixed(2)}</p>

                        {/* Size picker */}
                        <div className="flex flex-wrap gap-1.5 mt-2">
                          {item.sizes.map(sz => (
                            <button
                              key={sz}
                              onClick={() => handleSelectSize(item.id, sz)}
                              className={`text-[10px] px-2 py-0.5 border ${selectedSize === sz ? 'bg-black text-white border-black' : 'border-gray-200 text-gray-700 hover:border-black'}`}
                            >
                              {sz}
                            </button>
                          ))}
                        </div>
                      </div>

                      <button
                        onClick={() => handleAddToCart(item)}
                        className="p-2 border border-gray-300 hover:border-black text-sm font-medium"
                        aria-label={`Add ${item.name}`}
                      >
                        +
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Bundle checkout CTA */}
          <div className="pt-6 border-t border-[#c8c8c8] mt-8">
            <div className="flex justify-between items-baseline mb-3">
              <div>
                <p className="text-xs font-medium">Complete the look</p>
                <p className="text-[11px] text-[#66625c]">Bundle all 3 and save 10%</p>
              </div>
              <div className="flex items-baseline gap-2">
                <s className="text-xs text-gray-400">$547.00</s>
                <strong className="text-base font-semibold text-[#151413]">$492.30</strong>
              </div>
            </div>

            <button
              onClick={handleAddFullLook}
              className="w-full py-4 bg-[#151413] hover:bg-black text-white text-xs font-semibold uppercase tracking-wider transition-colors"
            >
              Add full look to bag
            </button>
          </div>
        </aside>
      </div>

      {/* Bag Dialog */}
      {isBagOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white max-w-lg w-full p-8 border border-gray-300 relative shadow-2xl">
            <div className="flex justify-between items-center mb-4 pb-2 border-b">
              <h3 className="text-xl font-normal">Your styling bag ({cart.length})</h3>
              <button onClick={() => setIsBagOpen(false)} className="text-2xl font-light hover:text-rose-600">×</button>
            </div>

            {cart.length === 0 ? (
              <p className="text-xs text-gray-500 py-8 text-center">Your styling bag is empty.</p>
            ) : (
              <div className="max-h-72 overflow-y-auto divide-y divide-gray-100 mb-6">
                {cart.map((item, idx) => (
                  <div key={idx} className="py-3 flex items-center justify-between text-xs">
                    <div className="flex items-center gap-3">
                      <img src={item.image} alt={item.name} className="w-10 h-10 object-contain" />
                      <div>
                        <p className="font-semibold">{item.name}</p>
                        <p className="text-gray-400 text-[10px]">Size {item.size} • ${item.price.toFixed(2)}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setCart(prev => prev.filter((_, i) => i !== idx))}
                      className="text-gray-400 hover:text-black font-semibold text-sm"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}

            <div className="pt-4 border-t flex justify-between items-center text-sm font-semibold mb-6">
              <span>Total Estimated</span>
              <span>${cart.reduce((acc, c) => acc + c.price, 0).toFixed(2)}</span>
            </div>

            <button
              onClick={() => {
                alert('Saved outfit shortlist. In full production, this syncs directly with Shopify Cart API.');
                setIsBagOpen(false);
              }}
              className="w-full py-3 bg-[#151413] text-white text-xs font-semibold uppercase tracking-wider hover:bg-black"
            >
              Confirm Styling Bag
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
