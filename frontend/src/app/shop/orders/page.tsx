'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useShoppingStore } from '@/stores/useShoppingStore';
import { useAuthStore } from '@/stores/useAuthStore';
import type { Order } from '@/api/shopping';

const statusMap: Record<string, { label: string; color: string; bg: string }> = {
  pending: { label: '待付款', color: 'text-amber-600', bg: 'bg-amber-50' },
  paid: { label: '待发货', color: 'text-blue-600', bg: 'bg-blue-50' },
  shipped: { label: '待收货', color: 'text-sky-600', bg: 'bg-sky-50' },
  delivered: { label: '已签收', color: 'text-emerald-600', bg: 'bg-emerald-50' },
  completed: { label: '已完成', color: 'text-green-600', bg: 'bg-green-50' },
  cancelled: { label: '已取消', color: 'text-neutral-400', bg: 'bg-neutral-100' },
  refunding: { label: '退款中', color: 'text-orange-600', bg: 'bg-orange-50' },
  refunded: { label: '已退款', color: 'text-neutral-500', bg: 'bg-neutral-100' },
};

const tabs = [
  { value: '', label: '全部' },
  { value: 'pending', label: '待付款' },
  { value: 'paid', label: '待发货' },
  { value: 'shipped', label: '待收货' },
  { value: 'completed', label: '已完成' },
];

export default function OrdersPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const {
    orders, totalOrders, ordersLoading, orderStatus,
    fetchOrders, payOrder, cancelOrder, confirmOrder, setOrderStatus,
  } = useShoppingStore();

  const [payingOrderId, setPayingOrderId] = useState<string | null>(null);

  useEffect(() => {
    if (user?.user_id) fetchOrders(user.user_id);
  }, [user?.user_id, fetchOrders]);

  useEffect(() => {
    if (user?.user_id) fetchOrders(user.user_id);
  }, [orderStatus, user?.user_id, fetchOrders]);

  const handlePay = useCallback(async (orderId: string) => {
    setPayingOrderId(orderId);
    try {
      await payOrder(orderId, 'wechat');
      if (user?.user_id) fetchOrders(user.user_id);
    } catch { /* */ }
    finally { setPayingOrderId(null); }
  }, [payOrder, fetchOrders, user?.user_id]);

  const handleCancel = useCallback(async (orderId: string) => {
    try {
      await cancelOrder(orderId, '不想要了');
      if (user?.user_id) fetchOrders(user.user_id);
    } catch { /* */ }
  }, [cancelOrder, fetchOrders, user?.user_id]);

  const handleConfirm = useCallback(async (orderId: string) => {
    try {
      await confirmOrder(orderId);
      if (user?.user_id) fetchOrders(user.user_id);
    } catch { /* */ }
  }, [confirmOrder, fetchOrders, user?.user_id]);

  return (
    <div className="min-h-screen bg-neutral-50">
      <header className="sticky top-0 z-40 border-b border-neutral-100 bg-white/80 backdrop-blur-xl">
        <div className="flex items-center gap-3 px-4 py-3">
          <button onClick={() => router.back()} className="rounded-full p-2 hover:bg-neutral-100">
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h1 className="flex-1 text-base font-semibold text-neutral-900">我的订单</h1>
        </div>
        <div className="flex border-b border-neutral-100">
          {tabs.map(tab => (
            <button
              key={tab.value}
              onClick={() => setOrderStatus(tab.value)}
              className={`flex-1 py-2.5 text-sm font-medium transition-colors ${
                orderStatus === tab.value
                  ? 'border-b-2 border-primary-500 text-primary-600'
                  : 'text-neutral-500 hover:text-neutral-700'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </header>

      {ordersLoading ? (
        <div className="space-y-3 p-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="animate-pulse rounded-2xl bg-white p-5">
              <div className="h-4 w-1/3 rounded bg-neutral-200" />
              <div className="mt-4 h-16 rounded bg-neutral-200" />
              <div className="mt-3 h-4 w-1/4 rounded bg-neutral-200" />
            </div>
          ))}
        </div>
      ) : orders.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-32 text-center">
          <span className="text-7xl">📋</span>
          <p className="mt-6 text-lg font-semibold text-neutral-900">暂无订单</p>
          <p className="mt-2 text-sm text-neutral-500">去商城选购心仪商品吧</p>
          <Link href="/shop" className="mt-6 rounded-xl bg-primary-500 px-8 py-3 text-sm font-bold text-white hover:bg-primary-600">
            去逛逛
          </Link>
        </div>
      ) : (
        <div className="space-y-3 p-4">
          {orders.map(order => {
            const statusInfo = statusMap[order.status] || { label: order.status, color: 'text-neutral-500', bg: 'bg-neutral-100' };
            return (
              <div key={order.order_id} className="overflow-hidden rounded-2xl bg-white shadow-sm">
                <div className="flex items-center justify-between border-b border-neutral-50 px-5 py-3">
                  <span className="text-xs text-neutral-400">订单号：{order.order_no}</span>
                  <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusInfo.color} ${statusInfo.bg}`}>
                    {statusInfo.label}
                  </span>
                </div>

                <div className="px-5 py-3">
                  {order.items.map(item => (
                    <div key={item.order_item_id} className="flex items-center gap-3 py-2">
                      <div className="h-16 w-16 flex-shrink-0 overflow-hidden rounded-lg bg-neutral-100">
                        {item.product_image_url ? (
                          <img src={item.product_image_url} alt="" className="h-full w-full object-cover" />
                        ) : (
                          <span className="flex h-full items-center justify-center text-2xl">📦</span>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="truncate text-sm font-medium text-neutral-900">{item.product_name}</p>
                        <p className="text-xs text-neutral-400">x{item.quantity}</p>
                      </div>
                      <span className="text-sm font-semibold text-neutral-900">¥{item.subtotal.toFixed(2)}</span>
                    </div>
                  ))}
                </div>

                <div className="flex items-center justify-between border-t border-neutral-50 px-5 py-3">
                  <span className="text-sm text-neutral-500">
                    共{order.items.reduce((s, i) => s + i.quantity, 0)}件商品，实付
                    <span className="ml-1 font-bold text-red-500">¥{order.pay_amount.toFixed(2)}</span>
                  </span>
                  <div className="flex gap-2">
                    {order.status === 'pending' && (
                      <>
                        <button
                          onClick={() => handleCancel(order.order_id)}
                          className="rounded-lg border border-neutral-200 px-4 py-1.5 text-xs font-medium text-neutral-600 hover:bg-neutral-50"
                        >
                          取消
                        </button>
                        <button
                          onClick={() => handlePay(order.order_id)}
                          disabled={payingOrderId === order.order_id}
                          className="rounded-lg bg-primary-500 px-4 py-1.5 text-xs font-bold text-white hover:bg-primary-600 disabled:opacity-50"
                        >
                          {payingOrderId === order.order_id ? '支付中...' : '立即支付'}
                        </button>
                      </>
                    )}
                    {order.status === 'shipped' && (
                      <button
                        onClick={() => handleConfirm(order.order_id)}
                        className="rounded-lg bg-primary-500 px-4 py-1.5 text-xs font-bold text-white hover:bg-primary-600"
                      >
                        确认收货
                      </button>
                    )}
                    {order.status === 'completed' && !order.is_reviewed && (
                      <Link
                        href={`/shop/reviews/new?order_id=${order.order_id}`}
                        className="rounded-lg bg-amber-400 px-4 py-1.5 text-xs font-bold text-neutral-900 hover:bg-amber-500"
                      >
                        去评价
                      </Link>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      <div className="h-20 md:h-0" />
    </div>
  );
}
