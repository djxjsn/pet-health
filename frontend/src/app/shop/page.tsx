'use client';

import { useState, useCallback, useEffect } from 'react';
import Link from 'next/link';
import { useShoppingStore } from '@/stores/useShoppingStore';
import { useAuthStore } from '@/stores/useAuthStore';
import OptimizedImage from '@/components/OptimizedImage';
import type { Product } from '@/api/shopping';

const categories = [
  { id: '', name: '全部', icon: '🏪', gradient: 'from-primary-400 to-primary-600' },
  { id: 'food', name: '宠物粮食', icon: '🍖', gradient: 'from-amber-400 to-orange-500' },
  { id: 'medicine', name: '医药保健', icon: '💊', gradient: 'from-emerald-400 to-green-600' },
  { id: 'toy', name: '趣味玩具', icon: '🎾', gradient: 'from-sky-400 to-blue-500' },
  { id: 'nest', name: '温馨小窝', icon: '🏠', gradient: 'from-violet-400 to-purple-600' },
  { id: 'hygiene', name: '清洁护理', icon: '🧴', gradient: 'from-pink-400 to-rose-500' },
  { id: 'accessory', name: '时尚配件', icon: '🎀', gradient: 'from-teal-400 to-cyan-500' },
  { id: 'clothing', name: '萌宠服饰', icon: '👕', gradient: 'from-indigo-400 to-blue-600' },
];

const categoryIconMap: Record<string, string> = {
  food: '🍖',
  medicine: '💊',
  toy: '🎾',
  nest: '🏠',
  hygiene: '🧴',
  accessory: '🎀',
  clothing: '👕',
};

function formatPrice(price: number): string {
  return price.toFixed(2);
}

function ProductCard({ product, onAddToCart }: { product: Product; onAddToCart: (p: Product) => void }) {
  const discount = product.original_price ? Math.round((1 - product.price / product.original_price) * 100) : 0;

  return (
    <Link href={`/shop/${product.product_id}`} className="group block">
      <div className="overflow-hidden rounded-2xl border border-neutral-100 bg-white shadow-sm transition-all duration-300 hover:shadow-xl hover:-translate-y-1 hover:border-primary-100">
        <div className="relative aspect-square bg-gradient-to-br from-neutral-50 to-neutral-100 overflow-hidden">
          <OptimizedImage
            src={product.image_url || ''}
            alt={product.name}
            fill
            sizes="(max-width: 640px) 50vw, (max-width: 768px) 33vw, 25vw"
            quality={85}
            priority={false}
            fallback={
              <span className="flex h-full items-center justify-center text-5xl">
                {categoryIconMap[product.category] || '📦'}
              </span>
            }
            className="object-cover transition-transform duration-500 group-hover:scale-110"
          />

          {discount > 0 && (
            <div className="absolute top-2 left-2 flex items-center gap-1">
              <span className="rounded-lg bg-red-500 px-2 py-0.5 text-xs font-bold text-white shadow-sm">
                -{discount}%
              </span>
            </div>
          )}

          {product.is_tcm_product && (
            <span className="absolute top-2 right-2 rounded-lg bg-emerald-500 px-2 py-0.5 text-xs font-bold text-white shadow-sm">
              中药
            </span>
          )}

          {product.stock_status === 'out_of_stock' && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/40 backdrop-blur-[2px]">
              <span className="rounded-xl bg-black/70 px-4 py-1.5 text-sm font-semibold text-white">
                暂时缺货
              </span>
            </div>
          )}

          {product.stock_status === 'limited' && (
            <span className="absolute bottom-2 left-2 rounded-lg bg-amber-500/90 px-2 py-0.5 text-xs font-medium text-white">
              仅剩{product.stock}件
            </span>
          )}

          <button
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              if (product.stock_status !== 'out_of_stock') onAddToCart(product);
            }}
            disabled={product.stock_status === 'out_of_stock'}
            className={`
              absolute bottom-2 right-2 flex h-9 w-9 items-center justify-center rounded-full
              shadow-lg transition-all duration-200
              ${product.stock_status === 'out_of_stock'
                ? 'cursor-not-allowed bg-neutral-200 text-neutral-400'
                : 'bg-primary-500 text-white hover:bg-primary-600 hover:scale-110 active:scale-95'
              }
            `}
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          </button>
        </div>

        <div className="p-3.5">
          {product.merchant_name && (
            <p className="mb-1 truncate text-xs text-neutral-400">{product.merchant_name}</p>
          )}
          <h3 className="truncate text-sm font-semibold text-neutral-900 group-hover:text-primary-600 transition-colors">
            {product.name}
          </h3>

          <p className="mt-1 line-clamp-2 text-xs leading-relaxed text-neutral-500">
            {product.description}
          </p>

          <div className="mt-2 flex items-center gap-1.5">
            <div className="flex items-center">
              {[1, 2, 3, 4, 5].map(star => (
                <svg
                  key={star}
                  className={`h-3.5 w-3.5 ${star <= Math.floor(product.rating) ? 'text-amber-400' : 'text-neutral-200'}`}
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              ))}
            </div>
            <span className="text-xs text-neutral-400">
              {product.rating > 0 ? product.rating.toFixed(1) : '暂无评分'}
            </span>
            {product.review_count > 0 && (
              <span className="text-xs text-neutral-300">({product.review_count})</span>
            )}
          </div>

          <div className="mt-2.5 flex items-end justify-between">
            <div className="flex items-baseline gap-1.5">
              <span className="text-lg font-bold text-red-500">
                ¥{formatPrice(product.price)}
              </span>
              {product.original_price && product.original_price > product.price && (
                <span className="text-xs text-neutral-400 line-through">
                  ¥{formatPrice(product.original_price)}
                </span>
              )}
            </div>
            {product.sales_count > 0 && (
              <span className="text-xs text-neutral-400">已售{product.sales_count}</span>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}

export default function ShopPage() {
  const {
    products, isLoading, searchQuery, selectedCategory, sortBy,
    hotSearches, fetchProducts, fetchHotSearches,
    setSearchQuery, setSelectedCategory, setSortBy, addToCart,
  } = useShoppingStore();

  const { user } = useAuthStore();
  const [showHotSearch, setShowHotSearch] = useState(false);
  const [addingToCart, setAddingToCart] = useState<string | null>(null);

  useEffect(() => {
    fetchProducts();
    fetchHotSearches();
  }, [fetchProducts, fetchHotSearches]);

  useEffect(() => {
    fetchProducts();
  }, [selectedCategory, sortBy, fetchProducts]);

  const handleSearch = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    fetchProducts();
    setShowHotSearch(false);
  }, [fetchProducts]);

  const handleHotSearchClick = useCallback((keyword: string) => {
    setSearchQuery(keyword);
    setShowHotSearch(false);
    setTimeout(() => fetchProducts(), 0);
  }, [setSearchQuery, fetchProducts]);

  const handleAddToCart = useCallback(async (product: Product) => {
    if (!user?.user_id) return;
    setAddingToCart(product.product_id);
    try {
      await addToCart(user.user_id, product.product_id, 1);
    } catch {
      // error handled in store
    } finally {
      setAddingToCart(null);
    }
  }, [user?.user_id, addToCart]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-neutral-50 to-white">
      <header className="sticky top-0 z-40 border-b border-neutral-100 bg-white/80 backdrop-blur-xl md:hidden">
        <div className="flex items-center justify-between px-4 py-3">
          <h1 className="text-lg font-bold text-neutral-900">🐾 智能商城</h1>
          <Link href="/shop/cart" className="relative rounded-full p-2 text-neutral-600 hover:bg-neutral-100">
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
          </Link>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-4 py-6">
        {/* Search Bar */}
        <div className="mb-6">
          <form onSubmit={handleSearch} className="relative">
            <svg
              className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-neutral-400"
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => setShowHotSearch(true)}
              onBlur={() => setTimeout(() => setShowHotSearch(false), 200)}
              placeholder="搜索宠物粮食、药品、玩具..."
              className="w-full rounded-2xl border border-neutral-200 bg-white py-3.5 pl-12 pr-4 text-sm shadow-sm transition-all focus:border-primary-400 focus:outline-none focus:ring-4 focus:ring-primary-100"
            />
            {showHotSearch && hotSearches.length > 0 && (
              <div className="absolute left-0 right-0 top-full z-50 mt-2 rounded-2xl border border-neutral-100 bg-white p-4 shadow-xl">
                <p className="mb-2 text-xs font-semibold text-neutral-400">🔥 热门搜索</p>
                <div className="flex flex-wrap gap-2">
                  {hotSearches.map((item) => (
                    <button
                      key={item.keyword}
                      onClick={() => handleHotSearchClick(item.keyword)}
                      className="rounded-full bg-neutral-100 px-3 py-1.5 text-xs text-neutral-700 transition-colors hover:bg-primary-50 hover:text-primary-600"
                    >
                      {item.keyword}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </form>
        </div>

        {/* Category Navigation */}
        <div className="mb-8">
          <div className="grid grid-cols-4 gap-3 md:grid-cols-8">
            {categories.map(cat => (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`flex flex-col items-center gap-2 rounded-2xl p-3 transition-all duration-200 ${
                  selectedCategory === cat.id
                    ? 'bg-primary-50 shadow-sm ring-2 ring-primary-200'
                    : 'bg-white hover:bg-neutral-50'
                }`}
              >
                <span className={`flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br ${cat.gradient} text-xl shadow-sm`}>
                  {cat.icon}
                </span>
                <span className={`text-xs font-medium ${
                  selectedCategory === cat.id ? 'text-primary-700' : 'text-neutral-600'
                }`}>
                  {cat.name}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Sort & Count */}
        <div className="mb-6 flex items-center justify-between">
          <p className="text-sm font-medium text-neutral-500">
            共 <span className="text-neutral-900">{products.length}</span> 件商品
          </p>
          <div className="flex items-center gap-1 rounded-xl bg-neutral-100 p-1">
            {[
              { value: 'popular', label: '热门' },
              { value: 'newest', label: '最新' },
              { value: 'price-asc', label: '价格↑' },
              { value: 'price-desc', label: '价格↓' },
            ].map(opt => (
              <button
                key={opt.value}
                onClick={() => setSortBy(opt.value)}
                className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
                  sortBy === opt.value
                    ? 'bg-white text-primary-600 shadow-sm'
                    : 'text-neutral-500 hover:text-neutral-700'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Product Grid */}
        {isLoading ? (
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="animate-pulse rounded-2xl bg-white p-4">
                <div className="mb-3 aspect-square rounded-xl bg-neutral-200" />
                <div className="h-4 w-3/4 rounded bg-neutral-200" />
                <div className="mt-2 h-3 w-1/2 rounded bg-neutral-200" />
                <div className="mt-3 h-5 w-1/3 rounded bg-neutral-200" />
              </div>
            ))}
          </div>
        ) : products.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-3xl bg-white py-20 text-center shadow-sm">
            <span className="mb-4 text-6xl">🔍</span>
            <p className="text-lg font-semibold text-neutral-900">暂无商品</p>
            <p className="mt-1 text-sm text-neutral-500">换个关键词或分类试试吧</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
            {products.map(product => (
              <ProductCard
                key={product.product_id}
                product={product}
                onAddToCart={handleAddToCart}
              />
            ))}
          </div>
        )}

        {/* Desktop Cart FAB */}
        <Link
          href="/shop/cart"
          className="fixed bottom-24 right-6 z-30 hidden h-14 w-14 items-center justify-center rounded-full bg-primary-500 text-white shadow-lg shadow-primary-200 transition-all hover:bg-primary-600 hover:scale-110 hover:shadow-xl md:flex"
        >
          <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
          </svg>
        </Link>
      </div>

      <div className="h-20 md:h-0" />
    </div>
  );
}
