'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useShoppingStore } from '@/stores/useShoppingStore';
import { useAuthStore } from '@/stores/useAuthStore';
import OptimizedImage from '@/components/OptimizedImage';

const categoryIconMap: Record<string, string> = {
  food: '🍖', medicine: '💊', toy: '🎾', nest: '🏠',
  hygiene: '🧴', accessory: '🎀', clothing: '👕',
};

export default function CartPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const {
    cart, cartLoading, fetchCart, updateCartItem, removeCartItem,
    updateCartSelection, clearCart, createOrder,
  } = useShoppingStore();

  const [isCheckout, setIsCheckout] = useState(false);
  const [shippingInfo, setShippingInfo] = useState({
    shipping_name: '',
    shipping_phone: '',
    shipping_address: '',
    shipping_province: '',
    shipping_city: '',
    shipping_district: '',
    remark: '',
  });

  useEffect(() => {
    if (user?.user_id) fetchCart(user.user_id);
  }, [user?.user_id, fetchCart]);

  const handleQuantityChange = useCallback(async (cartItemId: string, newQty: number) => {
    if (!user?.user_id || newQty < 1) return;
    await updateCartItem(user.user_id, cartItemId, { quantity: newQty });
  }, [user?.user_id, updateCartItem]);

  const handleRemove = useCallback(async (cartItemId: string) => {
    if (!user?.user_id) return;
    await removeCartItem(user.user_id, cartItemId);
  }, [user?.user_id, removeCartItem]);

  const handleToggleSelect = useCallback(async (cartItemId: string, selected: boolean) => {
    if (!user?.user_id) return;
    await updateCartItem(user.user_id, cartItemId, { selected });
  }, [user?.user_id, updateCartItem]);

  const handleSelectAll = useCallback(async (selected: boolean) => {
    if (!user?.user_id) return;
    await updateCartSelection(user.user_id, selected);
  }, [user?.user_id, updateCartSelection]);

  const handleCheckout = useCallback(async () => {
    if (!user?.user_id || !cart) return;
    setIsCheckout(true);
  }, [user?.user_id, cart]);

  const handleSubmitOrder = useCallback(async () => {
    if (!user?.user_id) return;
    try {
      const order = await createOrder(user.user_id, shippingInfo);
      if (order) {
        router.push(`/shop/orders/${order.order_id}`);
      }
    } catch { /* */ }
  }, [user?.user_id, shippingInfo, createOrder, router]);

  const items = cart?.items || [];
  const allSelected = items.length > 0 && items.every(i => i.selected);
  const selectedItems = items.filter(i => i.selected);
  const selectedAmount = cart?.selected_amount || 0;

  return (
    <div className="min-h-screen bg-neutral-50">
      <header className="sticky top-0 z-40 border-b border-neutral-100 bg-white/80 backdrop-blur-xl">
        <div className="flex items-center gap-3 px-4 py-3">
          <button onClick={() => router.back()} className="rounded-full p-2 hover:bg-neutral-100">
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h1 className="flex-1 text-base font-semibold text-neutral-900">购物车</h1>
          {items.length > 0 && (
            <button
              onClick={() => user?.user_id && clearCart(user.user_id)}
              className="text-sm text-neutral-400 hover:text-red-500"
            >
              清空
            </button>
          )}
        </div>
      </header>

      {!isCheckout ? (
        <>
          {cartLoading ? (
            <div className="space-y-3 p-4">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="animate-pulse flex gap-4 rounded-2xl bg-white p-4">
                  <div className="h-24 w-24 rounded-xl bg-neutral-200" />
                  <div className="flex-1 space-y-2">
                    <div className="h-4 w-3/4 rounded bg-neutral-200" />
                    <div className="h-3 w-1/2 rounded bg-neutral-200" />
                    <div className="h-5 w-1/4 rounded bg-neutral-200" />
                  </div>
                </div>
              ))}
            </div>
          ) : items.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-32 text-center">
              <span className="text-7xl">🛒</span>
              <p className="mt-6 text-lg font-semibold text-neutral-900">购物车是空的</p>
              <p className="mt-2 text-sm text-neutral-500">去商城逛逛，给主子挑点好物吧</p>
              <Link
                href="/shop"
                className="mt-6 rounded-xl bg-primary-500 px-8 py-3 text-sm font-bold text-white hover:bg-primary-600"
              >
                去逛逛
              </Link>
            </div>
          ) : (
            <div className="space-y-3 p-4">
              {items.map(item => (
                <div key={item.cart_item_id} className="flex gap-4 rounded-2xl bg-white p-4 shadow-sm">
                  <button
                    onClick={() => handleToggleSelect(item.cart_item_id, !item.selected)}
                    className={`mt-8 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full border-2 transition-colors ${
                      item.selected ? 'border-primary-500 bg-primary-500' : 'border-neutral-300'
                    }`}
                  >
                    {item.selected && (
                      <svg className="h-3 w-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    )}
                  </button>

                  <div className="h-24 w-24 flex-shrink-0 overflow-hidden rounded-xl bg-neutral-100">
                    <OptimizedImage
                      src={item.product_image_url || ''}
                      alt={item.product_name}
                      fill
                      sizes="96px"
                      quality={80}
                      fallback={
                        <span className="flex h-full items-center justify-center text-3xl">📦</span>
                      }
                      className="object-cover"
                    />
                  </div>

                  <div className="flex-1 min-w-0">
                    <h3 className="truncate text-sm font-semibold text-neutral-900">{item.product_name}</h3>
                    {item.merchant_name && (
                      <p className="mt-0.5 truncate text-xs text-neutral-400">{item.merchant_name}</p>
                    )}
                    {item.stock_status === 'out_of_stock' && (
                      <span className="mt-1 inline-block rounded bg-red-50 px-2 py-0.5 text-xs text-red-500">已缺货</span>
                    )}
                    <div className="mt-2 flex items-center justify-between">
                      <span className="text-base font-bold text-red-500">¥{item.price.toFixed(2)}</span>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleQuantityChange(item.cart_item_id, item.quantity - 1)}
                          disabled={item.quantity <= 1}
                          className="flex h-7 w-7 items-center justify-center rounded-lg border border-neutral-200 text-neutral-500 hover:bg-neutral-50 disabled:opacity-30"
                        >
                          -
                        </button>
                        <span className="w-6 text-center text-sm font-medium">{item.quantity}</span>
                        <button
                          onClick={() => handleQuantityChange(item.cart_item_id, item.quantity + 1)}
                          className="flex h-7 w-7 items-center justify-center rounded-lg border border-neutral-200 text-neutral-500 hover:bg-neutral-50"
                        >
                          +
                        </button>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => handleRemove(item.cart_item_id)}
                    className="mt-1 self-start p-1 text-neutral-300 hover:text-red-500"
                  >
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Bottom Bar */}
          {items.length > 0 && (
            <div className="fixed bottom-0 left-0 right-0 z-40 border-t border-neutral-100 bg-white px-5 py-3">
              <div className="flex items-center justify-between">
                <button
                  onClick={() => handleSelectAll(!allSelected)}
                  className="flex items-center gap-2"
                >
                  <span className={`flex h-5 w-5 items-center justify-center rounded-full border-2 ${
                    allSelected ? 'border-primary-500 bg-primary-500' : 'border-neutral-300'
                  }`}>
                    {allSelected && (
                      <svg className="h-3 w-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    )}
                  </span>
                  <span className="text-sm text-neutral-600">全选</span>
                </button>

                <div className="flex items-center gap-4">
                  <div>
                    <span className="text-sm text-neutral-500">合计：</span>
                    <span className="text-xl font-bold text-red-500">¥{selectedAmount.toFixed(2)}</span>
                  </div>
                  <button
                    onClick={handleCheckout}
                    disabled={selectedItems.length === 0}
                    className="rounded-xl bg-primary-500 px-6 py-3 text-sm font-bold text-white transition-all hover:bg-primary-600 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    结算({selectedItems.length})
                  </button>
                </div>
              </div>
            </div>
          )}
        </>
      ) : (
        /* Checkout Form */
        <div className="p-4 space-y-4">
          <h2 className="text-lg font-bold text-neutral-900">确认订单</h2>

          <div className="rounded-2xl bg-white p-5 shadow-sm space-y-4">
            <h3 className="text-sm font-semibold text-neutral-700">收货信息</h3>
            <input
              type="text" placeholder="收货人姓名" value={shippingInfo.shipping_name}
              onChange={e => setShippingInfo(prev => ({ ...prev, shipping_name: e.target.value }))}
              className="w-full rounded-xl border border-neutral-200 px-4 py-3 text-sm focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-100"
            />
            <input
              type="tel" placeholder="联系电话" value={shippingInfo.shipping_phone}
              onChange={e => setShippingInfo(prev => ({ ...prev, shipping_phone: e.target.value }))}
              className="w-full rounded-xl border border-neutral-200 px-4 py-3 text-sm focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-100"
            />
            <input
              type="text" placeholder="详细地址" value={shippingInfo.shipping_address}
              onChange={e => setShippingInfo(prev => ({ ...prev, shipping_address: e.target.value }))}
              className="w-full rounded-xl border border-neutral-200 px-4 py-3 text-sm focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-100"
            />
            <input
              type="text" placeholder="订单备注（选填）" value={shippingInfo.remark}
              onChange={e => setShippingInfo(prev => ({ ...prev, remark: e.target.value }))}
              className="w-full rounded-xl border border-neutral-200 px-4 py-3 text-sm focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-100"
            />
          </div>

          <div className="rounded-2xl bg-white p-5 shadow-sm">
            <h3 className="mb-3 text-sm font-semibold text-neutral-700">商品清单</h3>
            {selectedItems.map(item => (
              <div key={item.cart_item_id} className="flex items-center gap-3 py-2">
                <div className="h-12 w-12 flex-shrink-0 overflow-hidden rounded-lg bg-neutral-100">
                  <OptimizedImage src={item.product_image_url || ''} alt="" fill sizes="48px" quality={70}
                    fallback={<span className="flex h-full items-center justify-center text-lg">📦</span>}
                    className="object-cover"
                  />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="truncate text-sm text-neutral-900">{item.product_name}</p>
                  <p className="text-xs text-neutral-400">x{item.quantity}</p>
                </div>
                <span className="text-sm font-semibold text-neutral-900">¥{(item.price * item.quantity).toFixed(2)}</span>
              </div>
            ))}
            <div className="mt-3 border-t border-neutral-100 pt-3">
              <div className="flex justify-between text-sm">
                <span className="text-neutral-500">商品小计</span>
                <span className="font-medium">¥{selectedAmount.toFixed(2)}</span>
              </div>
              <div className="mt-1 flex justify-between text-sm">
                <span className="text-neutral-500">运费</span>
                <span className="font-medium">{selectedAmount >= 99 ? '免运费' : '¥10.00'}</span>
              </div>
              <div className="mt-2 flex justify-between">
                <span className="font-semibold text-neutral-900">实付</span>
                <span className="text-xl font-bold text-red-500">¥{(selectedAmount + (selectedAmount >= 99 ? 0 : 10)).toFixed(2)}</span>
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => setIsCheckout(false)}
              className="flex-1 rounded-xl border border-neutral-200 py-3.5 text-sm font-medium text-neutral-700 hover:bg-neutral-50"
            >
              返回修改
            </button>
            <button
              onClick={handleSubmitOrder}
              disabled={!shippingInfo.shipping_name || !shippingInfo.shipping_phone || !shippingInfo.shipping_address}
              className="flex-1 rounded-xl bg-primary-500 py-3.5 text-sm font-bold text-white hover:bg-primary-600 disabled:cursor-not-allowed disabled:opacity-50"
            >
              提交订单
            </button>
          </div>
        </div>
      )}

      <div className="h-24 md:h-8" />
    </div>
  );
}
