'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api-client';
import { formatCurrency } from '@/lib/utils';
import { useCart } from '@/lib/cart-context';
import FashionLoader from '@/components/ui/FashionLoader';
import EmptyState from '@/components/ui/EmptyState';
import {
  Heart, ShoppingBag, Eye, RefreshCw, LayoutGrid, ListFilter,
  Check, Sparkles, X, Shield, ArrowRight
} from 'lucide-react';

const CATEGORY_PASTELS: Record<string, { bg: string; text: string; border: string }> = {
  'kurtis': { bg: '#F8E5E9', text: '#9D435F', border: '#D9A9B5' },
  'dresses': { bg: '#E4EFF8', text: '#1E40AF', border: '#9BB7D4' },
  'tops': { bg: '#E8EFE5', text: '#245229', border: '#8BA888' },
  'shirts': { bg: '#FAF5EF', text: '#8A7338', border: '#E9D8B5' },
  'jeans': { bg: '#E7E8EB', text: '#383638', border: '#C5A55A' },
};

export default function ProductsPage() {
  const [products, setProducts] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterCat, setFilterCat] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('grid');

  // Interactive UI states
  const [wishlist, setWishlist] = useState<Record<string, boolean>>({});
  const [selectedVariants, setSelectedVariants] = useState<Record<string, { size: string; color: string }>>({});
  const [quickViewProduct, setQuickViewProduct] = useState<any | null>(null);

  const { addToCart } = useCart();

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [p, c] = await Promise.all([
        api.getProducts().catch(() => []),
        api.getCategories().catch(() => []),
      ]);
      const prods = Array.isArray(p) ? p : (p?.products || []);
      setProducts(prods);
      setCategories(Array.isArray(c) ? c : (c?.categories || []));

      // Default select first available size for each product
      const defaults: Record<string, { size: string; color: string }> = {};
      prods.forEach((prod: any) => {
        const firstVariant = prod.variants?.[0];
        defaults[prod.id] = {
          size: firstVariant?.size || 'M',
          color: firstVariant?.color || 'Classic Black',
        };
      });
      setSelectedVariants(defaults);
    } catch (e: any) {
      setError(e.message || 'Error loading product catalogue.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const toggleWishlist = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setWishlist(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const selectVariantSize = (productId: string, size: string, color: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedVariants(prev => ({
      ...prev,
      [productId]: { size, color },
    }));
  };

  const handleAddProductToCart = (product: any, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    const sel = selectedVariants[product.id] || { size: 'M', color: 'Noir' };
    const matchedVariant = product.variants?.find((v: any) => v.size === sel.size) || product.variants?.[0];

    addToCart({
      id: matchedVariant?.id || product.id,
      productId: product.id,
      name: product.title,
      category: product.category?.name || product.category_name || 'Designer Wear',
      price: Number(product.base_price) + Number(matchedVariant?.price_adjustment || 0),
      size: sel.size,
      color: matchedVariant?.color || sel.color,
      image: product.image_url || 'https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20261102_042056_1a704ff7-b0e5-4a9f-bbda-62392b819fb6.png&w=1200&q=85',
      sku: matchedVariant?.sku || product.base_sku,
    });
  };

  const filtered = products.filter((p: any) => {
    const matchesCat = !filterCat || p.category_id === filterCat || p.category?.slug === filterCat;
    const matchesSearch = !searchQuery || p.title.toLowerCase().includes(searchQuery.toLowerCase()) || p.base_sku.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCat && matchesSearch;
  });

  if (loading) {
    return (
      <div className="p-8 max-w-7xl mx-auto flex items-center justify-center min-h-[500px]">
        <FashionLoader size="large" />
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Top Header & Search Controls */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-[#E7E8EB]">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl lg:text-2xl font-bold tracking-tight text-[#383638]">
              Maison Vell Catalog & Inventory
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-[#F8E5E9] text-[#9D435F] border border-[#D9A9B5]">
              {products.length} Designs
            </span>
          </div>
          <p className="text-xs text-[#71717A] mt-1">
            Browse our artisanal apparel collection with real-time SKU reservations and variant-level inventory.
          </p>
        </div>

        {/* View toggles & Filters */}
        <div className="flex items-center gap-2.5 flex-wrap w-full md:w-auto">
          <input
            type="text"
            placeholder="Search silhouettes, fabric, SKU..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="px-3 py-1.5 rounded-xl border border-[#E7E8EB] bg-[#FCFBF8] text-xs text-[#383638] placeholder-[#8C95A0] focus:ring-1 focus:ring-[#C5A55A] focus:outline-none w-full sm:w-48"
          />

          <select
            value={filterCat}
            onChange={e => setFilterCat(e.target.value)}
            className="px-3 py-1.5 rounded-xl border border-[#E7E8EB] bg-[#FCFBF8] text-xs text-[#383638] font-medium focus:ring-1 focus:ring-[#C5A55A] focus:outline-none"
          >
            <option value="">All Departments</option>
            {categories.map((c: any) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>

          {/* View switcher */}
          <div className="flex items-center p-1 rounded-xl bg-[#FAF5EF] border border-[#E7E8EB]">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-1.5 rounded-lg transition-all ${
                viewMode === 'grid' ? 'bg-[#FCFBF8] text-[#383638] shadow-xs' : 'text-[#8C95A0] hover:text-[#383638]'
              }`}
              title="Luxury Lookbook Grid"
            >
              <LayoutGrid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={`p-1.5 rounded-lg transition-all ${
                viewMode === 'table' ? 'bg-[#FCFBF8] text-[#383638] shadow-xs' : 'text-[#8C95A0] hover:text-[#383638]'
              }`}
              title="Master SKU Registry Table"
            >
              <ListFilter className="w-4 h-4" />
            </button>
          </div>

          <button
            onClick={fetchData}
            className="p-2 rounded-xl border border-[#E7E8EB] bg-[#FCFBF8] text-[#71717A] hover:text-[#383638] hover:border-[#C5A55A] transition-colors"
            title="Refresh Catalog"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 rounded-2xl bg-[#F8E5E9] border border-[#D9A9B5] text-[#9D435F] text-xs flex justify-between items-center">
          <span>{error}</span>
          <button onClick={fetchData} className="underline font-bold">Retry</button>
        </div>
      )}

      {/* Empty State */}
      {filtered.length === 0 && !loading && (
        <EmptyState
          type="no-products"
          title="No Garments Found"
          description="We couldn't find any clothing designs matching your current filter. Try selecting 'All Departments' or clear search."
          actionText="Clear Filter"
          onAction={() => { setFilterCat(''); setSearchQuery(''); }}
        />
      )}

      {/* ===================== VIEW 1: LUXURY EDITORIAL GRID ===================== */}
      {viewMode === 'grid' && filtered.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filtered.map((prod: any) => {
            const isWishlisted = !!wishlist[prod.id];
            const currentVariant = selectedVariants[prod.id] || { size: 'M', color: 'Classic' };
            const catSlug = (prod.category?.slug || prod.category_name || '').toLowerCase();
            const pastelStyle = CATEGORY_PASTELS[catSlug] || { bg: '#FAF5EF', text: '#8A7338', border: '#E9D8B5' };

            return (
              <div
                key={prod.id}
                onClick={() => setQuickViewProduct(prod)}
                className="group cursor-pointer rounded-2xl bg-[#FCFBF8] border border-[#E7E8EB] overflow-hidden shadow-[0_2px_12px_rgba(56,54,56,0.03)] hover:shadow-[0_8px_24px_rgba(201,165,90,0.12)] hover:border-[#C5A55A]/50 transition-all duration-300 flex flex-col justify-between"
              >
                {/* Product Image & Badges Container */}
                <div className="relative aspect-[3/4] w-full bg-gradient-to-b from-[#FAF5EF] to-[#FCFBF8] overflow-hidden p-4 flex items-center justify-center">
                  {/* Category Accent Badge */}
                  <span
                    className="absolute top-3 left-3 z-10 px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider shadow-xs border"
                    style={{
                      backgroundColor: pastelStyle.bg,
                      color: pastelStyle.text,
                      borderColor: pastelStyle.border,
                    }}
                  >
                    {prod.category?.name || prod.category_name || 'Atelier'}
                  </span>

                  {/* Wishlist Heart Button */}
                  <button
                    onClick={e => toggleWishlist(prod.id, e)}
                    className="absolute top-3 right-3 z-10 w-8 h-8 rounded-full bg-white/90 backdrop-blur-xs border border-[#E7E8EB] flex items-center justify-center text-[#8C95A0] hover:text-[#9D435F] transition-all shadow-xs"
                    aria-label="Save to wishlist"
                  >
                    <Heart
                      className={`w-4 h-4 transition-transform ${
                        isWishlisted ? 'fill-[#9D435F] text-[#9D435F] animate-heart-pop' : 'group-hover:scale-110'
                      }`}
                    />
                  </button>

                  {/* Product Photograph with zoom */}
                  <img
                    src={prod.image_url || 'https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20261102_042056_1a704ff7-b0e5-4a9f-bbda-62392b819fb6.png&w=1200&q=85'}
                    alt={prod.title}
                    className="w-full h-full object-contain transform group-hover:scale-106 transition-transform duration-500 ease-out"
                  />

                  {/* Quick View Hover Pill */}
                  <div className="absolute bottom-3 inset-x-4 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                    <button
                      onClick={e => {
                        e.stopPropagation();
                        setQuickViewProduct(prod);
                      }}
                      className="w-full py-2 rounded-xl bg-white/95 backdrop-blur-md border border-[#E9D8B5] text-[11px] font-bold text-[#383638] shadow-md hover:bg-[#FAF5EF] transition-colors flex items-center justify-center gap-1.5"
                    >
                      <Eye className="w-3.5 h-3.5 text-[#C5A55A]" /> Quick View Specifications
                    </button>
                  </div>
                </div>

                {/* Card Content & Variant Selectors */}
                <div className="p-4 flex-1 flex flex-col justify-between space-y-3 bg-[#FCFBF8]">
                  <div>
                    <div className="flex justify-between items-baseline gap-2">
                      <span className="text-[10px] font-mono text-[#8C95A0] tracking-wider uppercase">
                        {prod.base_sku}
                      </span>
                      <span className="text-[10px] font-semibold text-[#059669]">
                        In Stock ✓
                      </span>
                    </div>

                    <h3 className="font-bold text-xs text-[#383638] mt-1 group-hover:text-[#9D435F] transition-colors line-clamp-1">
                      {prod.title}
                    </h3>
                    <p className="text-[11px] text-[#71717A] mt-0.5 line-clamp-2 leading-relaxed">
                      {prod.description}
                    </p>
                  </div>

                  {/* Size Selectors with pastel borders */}
                  {prod.variants && prod.variants.length > 0 && (
                    <div className="pt-2 border-t border-[#F8F5EF]">
                      <div className="flex items-center justify-between mb-1.5 text-[10px] text-[#8C95A0]">
                        <span>Select Size:</span>
                        <span className="font-bold text-[#383638]">{currentVariant.size}</span>
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {prod.variants.map((v: any) => {
                          const isSelected = currentVariant.size === v.size;
                          return (
                            <button
                              key={v.id}
                              onClick={e => selectVariantSize(prod.id, v.size, v.color, e)}
                              className={`px-2 py-1 rounded-md text-[10px] font-bold transition-all ${
                                isSelected
                                  ? 'bg-[#F8E5E9] text-[#9D435F] border-2 border-[#C5A55A] shadow-xs'
                                  : 'bg-[#FAF5EF] text-[#4B5563] border border-[#E7E8EB] hover:border-[#D9A9B5]'
                              }`}
                            >
                              {v.size}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {/* Price & Add to Bag Button */}
                  <div className="pt-2 border-t border-[#E7E8EB] flex items-center justify-between">
                    <div>
                      <span className="text-xs font-bold text-[#383638]">
                        {formatCurrency(prod.base_price)}
                      </span>
                      <span className="text-[10px] text-[#8C95A0] block">
                        Complimentary Courier
                      </span>
                    </div>

                    <button
                      onClick={e => handleAddProductToCart(prod, e)}
                      className="px-3.5 py-2 rounded-xl bg-[#383638] text-white hover:bg-black text-[11px] font-bold transition-all shadow-xs flex items-center gap-1.5 group-hover:bg-[#C5A55A]"
                    >
                      <ShoppingBag className="w-3.5 h-3.5" />
                      <span>Add to Bag</span>
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ===================== VIEW 2: MASTER SKU TABLE ===================== */}
      {viewMode === 'table' && filtered.length > 0 && (
        <div className="bg-[#FCFBF8] rounded-2xl border border-[#E7E8EB] overflow-hidden shadow-xs">
          <div className="px-6 py-4 border-b border-[#E7E8EB] bg-[#FAF5EF] flex justify-between items-center">
            <h2 className="text-xs font-bold uppercase tracking-wider text-[#383638]">Master Garment Registry</h2>
            <span className="text-xs text-[#8C95A0] font-medium">{filtered.length} designs active</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-left text-[#71717A] border-b border-[#E7E8EB] bg-[#FAF5EF] uppercase tracking-wider text-[11px]">
                  {['Garment Description', 'Base SKU', 'Category', 'Base Price', 'Fabric Material', 'Action'].map(h => (
                    <th key={h} className="px-5 py-3 font-semibold">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F3F4F6]">
                {filtered.map((p: any) => (
                  <tr key={p.id} className="hover:bg-[#FAF5EF] transition-colors">
                    <td className="px-5 py-3.5">
                      <div className="font-semibold text-[#383638]">{p.title}</div>
                      <div className="text-[10px] text-[#8C95A0] truncate max-w-sm mt-0.5">{p.description}</div>
                    </td>
                    <td className="px-5 py-3.5 font-mono text-[11px] text-[#71717A]">{p.base_sku}</td>
                    <td className="px-5 py-3.5 text-[#383638] font-medium">{p.category?.name || p.category_name || 'Clothing'}</td>
                    <td className="px-5 py-3.5 font-bold text-[#383638]">{formatCurrency(p.base_price)}</td>
                    <td className="px-5 py-3.5 text-[#71717A]">{p.fabric || '100% Cotton'}</td>
                    <td className="px-5 py-3.5">
                      <button
                        onClick={() => handleAddProductToCart(p)}
                        className="px-3 py-1.5 rounded-lg bg-[#383638] text-white text-[11px] font-bold hover:bg-black transition-colors"
                      >
                        Add to Bag
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ===================== QUICK VIEW MODAL ===================== */}
      {quickViewProduct && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs">
          <div className="relative w-full max-w-2xl bg-[#FCFBF8] rounded-3xl border border-[#E9D8B5] p-6 lg:p-8 shadow-2xl overflow-hidden animate-[slideUp_0.3s_ease-out]">
            <button
              onClick={() => setQuickViewProduct(null)}
              className="absolute top-4 right-4 w-8 h-8 rounded-full border border-[#E7E8EB] flex items-center justify-center text-[#8C95A0] hover:text-[#383638] transition-colors"
            >
              <X className="w-4 h-4" />
            </button>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
              <div className="aspect-[3/4] rounded-2xl bg-[#FAF5EF] border border-[#E7E8EB] p-4 flex items-center justify-center overflow-hidden">
                <img
                  src={quickViewProduct.image_url || 'https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20261102_042056_1a704ff7-b0e5-4a9f-bbda-62392b819fb6.png&w=1200&q=85'}
                  alt={quickViewProduct.title}
                  className="w-full h-full object-contain"
                />
              </div>

              <div className="space-y-4">
                <div>
                  <span className="text-[10px] font-mono uppercase tracking-wider text-[#C5A55A]">
                    {quickViewProduct.base_sku}
                  </span>
                  <h2 className="text-lg font-bold text-[#383638] mt-0.5">
                    {quickViewProduct.title}
                  </h2>
                  <div className="text-base font-bold text-[#383638] mt-1">
                    {formatCurrency(quickViewProduct.base_price)}
                  </div>
                </div>

                <p className="text-xs text-[#71717A] leading-relaxed">
                  {quickViewProduct.description}
                </p>

                <div className="p-3 rounded-xl bg-[#FAF5EF] border border-[#E7E8EB] text-xs space-y-1">
                  <div className="flex justify-between">
                    <span className="text-[#8C95A0]">Fabric Composition:</span>
                    <span className="font-semibold text-[#383638]">{quickViewProduct.fabric || 'Mulberry Silk & Linen Blend'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[#8C95A0]">Care Guide:</span>
                    <span className="font-semibold text-[#383638]">Dry Clean Only</span>
                  </div>
                </div>

                <button
                  onClick={() => {
                    handleAddProductToCart(quickViewProduct);
                    setQuickViewProduct(null);
                  }}
                  className="w-full py-3 rounded-xl bg-[#383638] text-white hover:bg-black text-xs font-bold uppercase tracking-wider transition-all shadow-md flex items-center justify-center gap-2"
                >
                  <ShoppingBag className="w-4 h-4 text-[#C5A55A]" />
                  <span>Add to Styling Bag</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
