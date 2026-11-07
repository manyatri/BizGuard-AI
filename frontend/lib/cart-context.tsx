'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

export interface CartItem {
  id: string; // Unique cart item key: variantId or itemId
  productId?: string;
  name: string;
  category?: string;
  price: number;
  originalPrice?: number;
  size: string;
  color: string;
  quantity: number;
  image: string;
  sku?: string;
}

interface ToastInfo {
  id: string;
  title: string;
  message: string;
  image?: string;
}

interface CartContextType {
  items: CartItem[];
  addToCart: (item: Omit<CartItem, 'quantity'> & { quantity?: number }) => void;
  removeFromCart: (id: string) => void;
  updateQuantity: (id: string, delta: number) => void;
  clearCart: () => void;
  totalItems: number;
  subtotal: number;
  discount: number;
  deliveryCharge: number;
  finalTotal: number;
  isBagOpen: boolean;
  setIsBagOpen: (open: boolean) => void;
  isCheckoutOpen: boolean;
  setIsCheckoutOpen: (open: boolean) => void;
  toast: ToastInfo | null;
  dismissToast: () => void;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

const STORAGE_KEY = 'bizguard_luxury_cart_v1';

export function CartProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = useState<CartItem[]>([]);
  const [isBagOpen, setIsBagOpen] = useState(false);
  const [isCheckoutOpen, setIsCheckoutOpen] = useState(false);
  const [toast, setToast] = useState<ToastInfo | null>(null);

  // Initialize from localStorage on client
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        setItems(JSON.parse(saved));
      }
    } catch {}
  }, []);

  // Sync to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
    } catch {}
  }, [items]);

  const showToast = (title: string, message: string, image?: string) => {
    const id = Math.random().toString(36).substring(7);
    setToast({ id, title, message, image });
    setTimeout(() => {
      setToast(curr => (curr?.id === id ? null : curr));
    }, 3800);
  };

  const addToCart = (newItem: Omit<CartItem, 'quantity'> & { quantity?: number }) => {
    const qty = newItem.quantity || 1;
    const itemKey = `${newItem.id}-${newItem.size}-${newItem.color}`;

    setItems(prev => {
      const existingIdx = prev.findIndex(
        i => i.id === newItem.id && i.size === newItem.size && i.color === newItem.color
      );
      if (existingIdx >= 0) {
        const updated = [...prev];
        updated[existingIdx] = {
          ...updated[existingIdx],
          quantity: updated[existingIdx].quantity + qty,
        };
        return updated;
      }
      return [...prev, { ...newItem, id: newItem.id, quantity: qty }];
    });

    showToast(
      'Added to Styling Bag',
      `${newItem.name} (Size ${newItem.size} · ${newItem.color})`,
      newItem.image
    );
  };

  const removeFromCart = (id: string) => {
    setItems(prev => prev.filter(i => i.id !== id));
  };

  const updateQuantity = (id: string, delta: number) => {
    setItems(prev =>
      prev
        .map(i => {
          if (i.id === id) {
            const nextQty = i.quantity + delta;
            return nextQty > 0 ? { ...i, quantity: nextQty } : null;
          }
          return i;
        })
        .filter(Boolean) as CartItem[]
    );
  };

  const clearCart = () => {
    setItems([]);
  };

  const totalItems = items.reduce((acc, i) => acc + i.quantity, 0);
  const subtotal = items.reduce((acc, i) => acc + i.price * i.quantity, 0);
  // Tiered boutique offer: ₹500 discount for orders above ₹3,000
  const discount = subtotal > 3000 ? 500 : 0;
  // Free delivery for orders above ₹1,500
  const deliveryCharge = subtotal > 1500 || subtotal === 0 ? 0 : 150;
  const finalTotal = Math.max(0, subtotal - discount + deliveryCharge);

  return (
    <CartContext.Provider
      value={{
        items,
        addToCart,
        removeFromCart,
        updateQuantity,
        clearCart,
        totalItems,
        subtotal,
        discount,
        deliveryCharge,
        finalTotal,
        isBagOpen,
        setIsBagOpen,
        isCheckoutOpen,
        setIsCheckoutOpen,
        toast,
        dismissToast: () => setToast(null),
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
}
