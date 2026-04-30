'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useShoppingStore } from '@/stores/useShoppingStore';
import { useAuthStore } from '@/stores/useAuthStore';

const ratingLabels = ['', '非常差', '差', '一般', '好', '非常好'];
const quickTags = ['好评', '物流快', '包装好', '质量好', '性价比高', '宠物喜欢', '效果明显', '会回购'];

export default function NewReviewPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const orderId = searchParams.get('order_id') || '';
  const { user } = useAuthStore();
  const { fetchOrder, createReview } = useShoppingStore();

  const [order, setOrder] = useState<Record<string, unknown> | null>(null);
  const [selectedItem, setSelectedItem] = useState<Record<string, unknown> | null>(null);
  const [rating, setRating] = useState(5);
  const [content, setContent] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (orderId) {
      fetchOrder(orderId).then(o => {
        if (o) {
          setOrder(o as unknown as Record<string, unknown>);
          const items = (o as Record<string, unknown>).items as Record<string, unknown>[];
          if (items && items.length > 0) setSelectedItem(items[0]);
        }
      });
    }
  }, [orderId, fetchOrder]);

  const toggleTag = useCallback((tag: string) => {
    setTags(prev => prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag]);
  }, []);

  const handleSubmit = useCallback(async () => {
    if (!user?.user_id || !selectedItem) return;
    setSubmitting(true);
    try {
      await createReview(user.user_id, {
        order_id: orderId,
        order_item_id: (selectedItem as Record<string, unknown>).order_item_id,
        product_id: (selectedItem as Record<string, unknown>).product_id,
        rating,
        content,
        tags,
        is_anonymous: isAnonymous,
      });
      router.back();
    } catch { /* */ }
    finally { setSubmitting(false); }
  }, [user?.user_id, selectedItem, orderId, rating, content, tags, isAnonymous, createReview, router]);

  const items = (order?.items || []) as Record<string, unknown>[];

  return (
    <div className="min-h-screen bg-neutral-50">
      <header className="sticky top-0 z-40 border-b border-neutral-100 bg-white/80 backdrop-blur-xl">
        <div className="flex items-center gap-3 px-4 py-3">
          <button onClick={() => router.back()} className="rounded-full p-2 hover:bg-neutral-100">
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h1 className="flex-1 text-base font-semibold text-neutral-900">发表评价</h1>
        </div>
      </header>

      <div className="p-4 space-y-4">
        {items.length > 1 && (
          <div className="rounded-2xl bg-white p-4 shadow-sm">
            <h3 className="mb-3 text-sm font-semibold text-neutral-700">选择商品</h3>
            <div className="flex gap-3 overflow-x-auto pb-2">
              {items.map((item) => (
                <button
                  key={String(item.order_item_id)}
                  onClick={() => setSelectedItem(item)}
                  className={`flex-shrink-0 rounded-xl border-2 p-2 transition-colors ${
                    selectedItem?.order_item_id === item.order_item_id
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-neutral-200'
                  }`}
                >
                  <p className="text-xs font-medium text-neutral-900 max-w-24 truncate">{String(item.product_name)}</p>
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="rounded-2xl bg-white p-5 shadow-sm">
          <h3 className="mb-4 text-sm font-semibold text-neutral-700">评分</h3>
          <div className="flex items-center gap-2">
            {[1, 2, 3, 4, 5].map(star => (
              <button key={star} onClick={() => setRating(star)} className="transition-transform hover:scale-110">
                <svg className={`h-10 w-10 ${star <= rating ? 'text-amber-400' : 'text-neutral-200'}`} fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              </button>
            ))}
            <span className="ml-2 text-sm font-medium text-amber-600">{ratingLabels[rating]}</span>
          </div>
        </div>

        <div className="rounded-2xl bg-white p-5 shadow-sm">
          <h3 className="mb-3 text-sm font-semibold text-neutral-700">快捷标签</h3>
          <div className="flex flex-wrap gap-2">
            {quickTags.map(tag => (
              <button
                key={tag}
                onClick={() => toggleTag(tag)}
                className={`rounded-full px-3 py-1.5 text-xs font-medium transition-colors ${
                  tags.includes(tag)
                    ? 'bg-primary-500 text-white'
                    : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
                }`}
              >
                {tag}
              </button>
            ))}
          </div>
        </div>

        <div className="rounded-2xl bg-white p-5 shadow-sm">
          <h3 className="mb-3 text-sm font-semibold text-neutral-700">评价内容</h3>
          <textarea
            value={content}
            onChange={e => setContent(e.target.value)}
            placeholder="分享你的使用体验，帮助其他宠物主人做出选择..."
            rows={4}
            maxLength={1000}
            className="w-full resize-none rounded-xl border border-neutral-200 px-4 py-3 text-sm focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-100"
          />
          <p className="mt-1 text-right text-xs text-neutral-400">{content.length}/1000</p>
        </div>

        <div className="rounded-2xl bg-white p-5 shadow-sm">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={isAnonymous}
              onChange={e => setIsAnonymous(e.target.checked)}
              className="h-4 w-4 rounded border-neutral-300 text-primary-500 focus:ring-primary-500"
            />
            <span className="text-sm text-neutral-700">匿名评价</span>
          </label>
        </div>

        <button
          onClick={handleSubmit}
          disabled={submitting || rating === 0}
          className="w-full rounded-xl bg-primary-500 py-3.5 text-sm font-bold text-white hover:bg-primary-600 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {submitting ? '提交中...' : '提交评价'}
        </button>
      </div>
    </div>
  );
}
