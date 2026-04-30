'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { useShoppingStore } from '@/stores/useShoppingStore';
import { useAuthStore } from '@/stores/useAuthStore';
import OptimizedImage from '@/components/OptimizedImage';
import type { Product, Review } from '@/api/shopping';

const categoryIconMap: Record<string, string> = {
  food: '🍖', medicine: '💊', toy: '🎾', nest: '🏠',
  hygiene: '🧴', accessory: '🎀', clothing: '👕',
};

const categoryNameMap: Record<string, string> = {
  food: '宠物粮食', medicine: '医药保健', toy: '趣味玩具', nest: '温馨小窝',
  hygiene: '清洁护理', accessory: '时尚配件', clothing: '萌宠服饰',
};

function StarRating({ rating, size = 'md' }: { rating: number; size?: 'sm' | 'md' | 'lg' }) {
  const sizeClass = size === 'sm' ? 'h-3.5 w-3.5' : size === 'lg' ? 'h-6 w-6' : 'h-4 w-4';
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map(star => (
        <svg key={star} className={`${sizeClass} ${star <= Math.floor(rating) ? 'text-amber-400' : star <= rating ? 'text-amber-300' : 'text-neutral-200'}`} fill="currentColor" viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
      ))}
    </div>
  );
}

function ReviewCard({ review }: { review: Review }) {
  return (
    <div className="border-b border-neutral-100 py-4 last:border-0">
      <div className="flex items-start gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-primary-100 to-primary-200 text-sm font-bold text-primary-700">
          {review.is_anonymous ? '匿' : (review.user_nickname || '用')[0]}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-neutral-900">
              {review.is_anonymous ? '匿名用户' : review.user_nickname || '用户'}
            </span>
            <span className="text-xs text-neutral-400">{review.created_at?.slice(0, 10)}</span>
          </div>
          <div className="mt-1">
            <StarRating rating={review.rating} size="sm" />
          </div>
          {review.tags.length > 0 && (
            <div className="mt-1.5 flex flex-wrap gap-1">
              {review.tags.map(tag => (
                <span key={tag} className="rounded-full bg-primary-50 px-2 py-0.5 text-xs text-primary-600">{tag}</span>
              ))}
            </div>
          )}
          {review.content && (
            <p className="mt-2 text-sm leading-relaxed text-neutral-700">{review.content}</p>
          )}
          {review.image_urls.length > 0 && (
            <div className="mt-2 flex gap-2">
              {review.image_urls.slice(0, 3).map((url, i) => (
                <div key={i} className="h-20 w-20 overflow-hidden rounded-lg bg-neutral-100">
                  <OptimizedImage src={url} alt="" fill sizes="80px" className="object-cover" />
                </div>
              ))}
            </div>
          )}
          {review.reply_content && (
            <div className="mt-2 rounded-lg bg-neutral-50 p-3">
              <p className="text-xs font-medium text-neutral-500">商家回复：</p>
              <p className="mt-1 text-sm text-neutral-700">{review.reply_content}</p>
            </div>
          )}
          <div className="mt-2 flex items-center gap-4">
            <button className="flex items-center gap-1 text-xs text-neutral-400 hover:text-primary-500">
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
              </svg>
              {review.like_count}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ProductDetailPage() {
  const params = useParams();
  const router = useRouter();
  const productId = params.id as string;
  const { user } = useAuthStore();
  const { fetchProduct, fetchProductReviews, addToCart, reviewData } = useShoppingStore();

  const [product, setProduct] = useState<Product | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);
  const [addingToCart, setAddingToCart] = useState(false);
  const [activeTab, setActiveTab] = useState<'detail' | 'reviews'>('detail');

  useEffect(() => {
    async function load() {
      setLoading(true);
      const p = await fetchProduct(productId);
      if (p) setProduct(p);
      setLoading(false);
    }
    if (productId) load();
  }, [productId, fetchProduct]);

  useEffect(() => {
    if (productId) fetchProductReviews(productId);
  }, [productId, fetchProductReviews]);

  const handleAddToCart = useCallback(async () => {
    if (!user?.user_id || !product) return;
    setAddingToCart(true);
    try {
      await addToCart(user.user_id, product.product_id, quantity);
      router.push('/shop/cart');
    } catch { /* */ }
    finally { setAddingToCart(false); }
  }, [user?.user_id, product, quantity, addToCart, router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-white">
        <div className="animate-pulse">
          <div className="aspect-square bg-neutral-200" />
          <div className="p-6 space-y-4">
            <div className="h-6 w-3/4 rounded bg-neutral-200" />
            <div className="h-4 w-1/2 rounded bg-neutral-200" />
            <div className="h-8 w-1/3 rounded bg-neutral-200" />
          </div>
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-white">
        <span className="text-6xl">😢</span>
        <p className="mt-4 text-lg font-semibold text-neutral-900">商品不存在</p>
        <Link href="/shop" className="mt-4 text-sm text-primary-600 hover:underline">返回商城</Link>
      </div>
    );
  }

  const discount = product.original_price ? Math.round((1 - product.price / product.original_price) * 100) : 0;

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header */}
      <header className="sticky top-0 z-40 border-b border-neutral-100 bg-white/80 backdrop-blur-xl">
        <div className="flex items-center gap-3 px-4 py-3">
          <button onClick={() => router.back()} className="rounded-full p-2 hover:bg-neutral-100">
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h1 className="flex-1 truncate text-base font-semibold text-neutral-900">商品详情</h1>
          <Link href="/shop/cart" className="rounded-full p-2 hover:bg-neutral-100">
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
          </Link>
        </div>
      </header>

      {/* Product Image */}
      <div className="relative aspect-square bg-white">
        <OptimizedImage
          src={product.image_url || ''}
          alt={product.name}
          fill
          sizes="100vw"
          quality={90}
          priority
          fallback={
            <span className="flex h-full items-center justify-center text-8xl">
              {categoryIconMap[product.category] || '📦'}
            </span>
          }
          className="object-cover"
        />
        {discount > 0 && (
          <div className="absolute top-4 left-4 rounded-xl bg-red-500 px-3 py-1.5 text-sm font-bold text-white shadow-lg">
            -{discount}%
          </div>
        )}
      </div>

      {/* Product Info */}
      <div className="bg-white px-5 py-5">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1">
            <div className="flex items-center gap-2">
              {product.is_tcm_product && (
                <span className="rounded-md bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-700">中药</span>
              )}
              <span className="rounded-md bg-primary-100 px-2 py-0.5 text-xs font-medium text-primary-700">
                {categoryNameMap[product.category] || product.category}
              </span>
            </div>
            <h1 className="mt-2 text-xl font-bold text-neutral-900">{product.name}</h1>
            {product.brand && (
              <p className="mt-1 text-sm text-neutral-500">品牌：{product.brand}</p>
            )}
          </div>
        </div>

        <div className="mt-4 flex items-baseline gap-3">
          <span className="text-3xl font-bold text-red-500">¥{product.price.toFixed(2)}</span>
          {product.original_price && product.original_price > product.price && (
            <span className="text-base text-neutral-400 line-through">¥{product.original_price.toFixed(2)}</span>
          )}
        </div>

        <div className="mt-4 flex items-center gap-4 text-sm text-neutral-500">
          <div className="flex items-center gap-1">
            <StarRating rating={product.rating} size="sm" />
            <span className="ml-1 font-medium text-amber-500">{product.rating.toFixed(1)}</span>
          </div>
          <span>{product.review_count}条评价</span>
          <span>已售{product.sales_count}</span>
          {product.stock > 0 && product.stock <= 10 && (
            <span className="text-amber-500 font-medium">仅剩{product.stock}件</span>
          )}
        </div>

        {product.merchant_name && (
          <div className="mt-4 flex items-center gap-2 rounded-xl bg-neutral-50 p-3">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-100 text-sm">🏪</span>
            <div>
              <p className="text-sm font-medium text-neutral-900">{product.merchant_name}</p>
              <p className="text-xs text-neutral-400">官方认证商家</p>
            </div>
          </div>
        )}
      </div>

      {/* Quantity Selector */}
      <div className="mt-2 bg-white px-5 py-4">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-neutral-700">购买数量</span>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setQuantity(Math.max(1, quantity - 1))}
              className="flex h-8 w-8 items-center justify-center rounded-lg border border-neutral-200 text-neutral-600 hover:bg-neutral-50"
            >
              -
            </button>
            <span className="w-8 text-center text-sm font-semibold">{quantity}</span>
            <button
              onClick={() => setQuantity(Math.min(product.stock || 99, quantity + 1))}
              className="flex h-8 w-8 items-center justify-center rounded-lg border border-neutral-200 text-neutral-600 hover:bg-neutral-50"
            >
              +
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="mt-2 bg-white">
        <div className="flex border-b border-neutral-100">
          {(['detail', 'reviews'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex-1 py-3.5 text-sm font-medium transition-colors ${
                activeTab === tab
                  ? 'border-b-2 border-primary-500 text-primary-600'
                  : 'text-neutral-500 hover:text-neutral-700'
              }`}
            >
              {tab === 'detail' ? '商品详情' : `评价 (${product.review_count})`}
            </button>
          ))}
        </div>

        <div className="px-5 py-4">
          {activeTab === 'detail' ? (
            <div className="space-y-4">
              {product.description && (
                <div>
                  <h3 className="text-sm font-semibold text-neutral-900">商品描述</h3>
                  <p className="mt-2 text-sm leading-relaxed text-neutral-600">{product.description}</p>
                </div>
              )}
              {product.suitable_for && product.suitable_for.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-neutral-900">适用对象</h3>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {product.suitable_for.map(s => (
                      <span key={s} className="rounded-full bg-primary-50 px-3 py-1 text-xs text-primary-600">{s}</span>
                    ))}
                  </div>
                </div>
              )}
              {product.is_tcm_product && product.tcm_properties && (
                <div>
                  <h3 className="text-sm font-semibold text-neutral-900">中药属性</h3>
                  <div className="mt-2 rounded-xl bg-emerald-50 p-4">
                    {Object.entries(product.tcm_properties).map(([key, value]) => (
                      <div key={key} className="flex items-center gap-2 py-1">
                        <span className="text-xs font-medium text-emerald-700">{key}：</span>
                        <span className="text-xs text-emerald-600">{String(value)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {product.tags.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-neutral-900">标签</h3>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {product.tags.map(tag => (
                      <span key={tag} className="rounded-full bg-neutral-100 px-3 py-1 text-xs text-neutral-600">{tag}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div>
              {reviewData?.rating_stats && (
                <div className="mb-4 rounded-xl bg-amber-50 p-4">
                  <div className="flex items-center gap-4">
                    <div className="text-center">
                      <p className="text-3xl font-bold text-amber-600">{reviewData.rating_stats.avg_rating}</p>
                      <StarRating rating={reviewData.rating_stats.avg_rating} size="sm" />
                      <p className="mt-1 text-xs text-neutral-500">{reviewData.rating_stats.total_count}条评价</p>
                    </div>
                    <div className="flex-1 space-y-1">
                      {Object.entries(reviewData.rating_stats.distribution || {}).reverse().map(([star, count]) => (
                        <div key={star} className="flex items-center gap-2">
                          <span className="w-4 text-xs text-neutral-500">{star}星</span>
                          <div className="flex-1 h-2 rounded-full bg-neutral-200">
                            <div
                              className="h-full rounded-full bg-amber-400"
                              style={{ width: `${reviewData.rating_stats.total_count ? (count / reviewData.rating_stats.total_count) * 100 : 0}%` }}
                            />
                          </div>
                          <span className="w-8 text-right text-xs text-neutral-400">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
              {reviewData?.reviews.length ? (
                reviewData.reviews.map(review => <ReviewCard key={review.review_id} review={review} />)
              ) : (
                <div className="py-10 text-center">
                  <span className="text-4xl">📝</span>
                  <p className="mt-2 text-sm text-neutral-500">暂无评价</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Bottom Action Bar */}
      <div className="fixed bottom-0 left-0 right-0 z-40 border-t border-neutral-100 bg-white px-5 py-3 md:bottom-auto md:sticky">
        <div className="flex items-center gap-3">
          <Link
            href="/shop"
            className="flex flex-col items-center gap-0.5 px-3 text-neutral-500 hover:text-primary-600"
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            <span className="text-xs">首页</span>
          </Link>
          <button
            onClick={handleAddToCart}
            disabled={product.stock_status === 'out_of_stock' || addingToCart}
            className="flex-1 rounded-xl bg-amber-400 py-3.5 text-sm font-bold text-neutral-900 transition-all hover:bg-amber-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {addingToCart ? '添加中...' : product.stock_status === 'out_of_stock' ? '暂时缺货' : '加入购物车'}
          </button>
          <button
            onClick={handleAddToCart}
            disabled={product.stock_status === 'out_of_stock' || addingToCart}
            className="flex-1 rounded-xl bg-primary-500 py-3.5 text-sm font-bold text-white transition-all hover:bg-primary-600 disabled:cursor-not-allowed disabled:opacity-50"
          >
            立即购买
          </button>
        </div>
      </div>

      <div className="h-24 md:h-0" />
    </div>
  );
}
