'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useShoppingStore } from '@/stores/useShoppingStore';
import { useAuthStore } from '@/stores/useAuthStore';
import { shoppingApi } from '@/api/shopping';
import type { Merchant, Product } from '@/api/shopping';

const merchantTypes = [
  { value: 'tcm', label: '中药专营', icon: '🌿' },
  { value: 'pet_food', label: '宠物粮食', icon: '🍖' },
  { value: 'pet_medicine', label: '宠物医药', icon: '💊' },
  { value: 'pet_toy', label: '宠物玩具', icon: '🎾' },
  { value: 'pet_house', label: '宠物窝舍', icon: '🏠' },
  { value: 'general', label: '综合商家', icon: '🏪' },
];

export default function MerchantPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [merchant, setMerchant] = useState<Merchant | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [showRegister, setShowRegister] = useState(false);
  const [showAddProduct, setShowAddProduct] = useState(false);
  const [registerForm, setRegisterForm] = useState({
    merchant_name: '',
    merchant_type: 'general',
    description: '',
    contact_phone: '',
    contact_email: '',
    address: '',
  });
  const [productForm, setProductForm] = useState({
    name: '',
    category: 'food',
    price: 0,
    original_price: 0,
    description: '',
    stock: 0,
    is_tcm_product: false,
    tags: '',
  });

  useEffect(() => {
    async function load() {
      if (!user?.user_id) return;
      setLoading(true);
      try {
        const m = await shoppingApi.getMyMerchant(user.user_id);
        setMerchant(m);
        if (m) {
          const result = await shoppingApi.getProducts({ merchant_id: m.merchant_id, page: 1, page_size: 50 });
          setProducts(result.products);
        }
      } catch { /* not a merchant yet */ }
      setLoading(false);
    }
    load();
  }, [user?.user_id]);

  const handleRegister = useCallback(async () => {
    if (!user?.user_id) return;
    try {
      const m = await shoppingApi.createMerchant(user.user_id, {
        ...registerForm,
        tags: [],
      });
      setMerchant(m);
      setShowRegister(false);
    } catch { /* */ }
  }, [user?.user_id, registerForm]);

  const handleAddProduct = useCallback(async () => {
    if (!merchant) return;
    try {
      const p = await shoppingApi.createProduct(merchant.merchant_id, {
        ...productForm,
        original_price: productForm.original_price || undefined,
        tags: productForm.tags ? productForm.tags.split(',').map(t => t.trim()) : [],
        image_urls: [],
      });
      setProducts(prev => [p, ...prev]);
      setShowAddProduct(false);
      setProductForm({ name: '', category: 'food', price: 0, original_price: 0, description: '', stock: 0, is_tcm_product: false, tags: '' });
    } catch { /* */ }
  }, [merchant, productForm]);

  const handleDeleteProduct = useCallback(async (productId: string) => {
    try {
      await shoppingApi.deleteProduct(productId);
      setProducts(prev => prev.filter(p => p.product_id !== productId));
    } catch { /* */ }
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-neutral-50">
        <div className="animate-pulse p-6 space-y-4">
          <div className="h-8 w-1/3 rounded bg-neutral-200" />
          <div className="h-32 rounded-2xl bg-neutral-200" />
          <div className="h-64 rounded-2xl bg-neutral-200" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-50">
      <header className="sticky top-0 z-40 border-b border-neutral-100 bg-white/80 backdrop-blur-xl">
        <div className="flex items-center gap-3 px-4 py-3">
          <button onClick={() => router.back()} className="rounded-full p-2 hover:bg-neutral-100">
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h1 className="flex-1 text-base font-semibold text-neutral-900">商家管理</h1>
        </div>
      </header>

      <div className="p-4 space-y-4">
        {!merchant && !showRegister ? (
          <div className="flex flex-col items-center justify-center rounded-3xl bg-white py-20 text-center shadow-sm">
            <span className="text-7xl">🏪</span>
            <p className="mt-6 text-lg font-semibold text-neutral-900">成为商家</p>
            <p className="mt-2 text-sm text-neutral-500">入驻平台，开始销售宠物用品和中药产品</p>
            <button
              onClick={() => setShowRegister(true)}
              className="mt-6 rounded-xl bg-primary-500 px-8 py-3 text-sm font-bold text-white hover:bg-primary-600"
            >
              立即入驻
            </button>
          </div>
        ) : showRegister ? (
          <div className="rounded-2xl bg-white p-5 shadow-sm space-y-4">
            <h2 className="text-lg font-bold text-neutral-900">商家入驻申请</h2>
            <input
              type="text" placeholder="商家名称" value={registerForm.merchant_name}
              onChange={e => setRegisterForm(prev => ({ ...prev, merchant_name: e.target.value }))}
              className="w-full rounded-xl border border-neutral-200 px-4 py-3 text-sm focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-100"
            />
            <div>
              <label className="mb-2 block text-sm font-medium text-neutral-700">商家类型</label>
              <div className="grid grid-cols-3 gap-2">
                {merchantTypes.map(t => (
                  <button
                    key={t.value}
                    onClick={() => setRegisterForm(prev => ({ ...prev, merchant_type: t.value }))}
                    className={`rounded-xl border-2 p-3 text-center transition-colors ${
                      registerForm.merchant_type === t.value
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-neutral-200 hover:border-neutral-300'
                    }`}
                  >
                    <span className="text-2xl">{t.icon}</span>
                    <p className="mt-1 text-xs font-medium">{t.label}</p>
                  </button>
                ))}
              </div>
            </div>
            <textarea
              placeholder="商家简介" value={registerForm.description}
              onChange={e => setRegisterForm(prev => ({ ...prev, description: e.target.value }))}
              rows={3}
              className="w-full resize-none rounded-xl border border-neutral-200 px-4 py-3 text-sm focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-100"
            />
            <input
              type="tel" placeholder="联系电话" value={registerForm.contact_phone}
              onChange={e => setRegisterForm(prev => ({ ...prev, contact_phone: e.target.value }))}
              className="w-full rounded-xl border border-neutral-200 px-4 py-3 text-sm focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-100"
            />
            <input
              type="email" placeholder="联系邮箱" value={registerForm.contact_email}
              onChange={e => setRegisterForm(prev => ({ ...prev, contact_email: e.target.value }))}
              className="w-full rounded-xl border border-neutral-200 px-4 py-3 text-sm focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-100"
            />
            <input
              type="text" placeholder="详细地址" value={registerForm.address}
              onChange={e => setRegisterForm(prev => ({ ...prev, address: e.target.value }))}
              className="w-full rounded-xl border border-neutral-200 px-4 py-3 text-sm focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-100"
            />
            <div className="flex gap-3">
              <button onClick={() => setShowRegister(false)} className="flex-1 rounded-xl border border-neutral-200 py-3 text-sm font-medium text-neutral-700 hover:bg-neutral-50">取消</button>
              <button onClick={handleRegister} disabled={!registerForm.merchant_name} className="flex-1 rounded-xl bg-primary-500 py-3 text-sm font-bold text-white hover:bg-primary-600 disabled:opacity-50">提交申请</button>
            </div>
          </div>
        ) : (
          <>
            {/* Merchant Info Card */}
            <div className="rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 p-5 text-white shadow-lg">
              <div className="flex items-center gap-4">
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-white/20 text-3xl backdrop-blur-sm">
                  🏪
                </div>
                <div className="flex-1">
                  <h2 className="text-lg font-bold">{merchant.merchant_name}</h2>
                  <p className="mt-0.5 text-sm text-white/80">
                    {merchantTypes.find(t => t.value === merchant.merchant_type)?.icon}{' '}
                    {merchantTypes.find(t => t.value === merchant.merchant_type)?.label || merchant.merchant_type}
                  </p>
                  <div className="mt-2 flex items-center gap-3 text-xs text-white/70">
                    <span>⭐ {merchant.rating.toFixed(1)}</span>
                    <span>📦 {merchant.total_sales}销量</span>
                    <span>📋 {merchant.product_count}商品</span>
                  </div>
                </div>
                <span className={`rounded-full px-3 py-1 text-xs font-semibold ${
                  merchant.status === 'active' ? 'bg-emerald-400/20 text-emerald-200' :
                  merchant.status === 'pending' ? 'bg-amber-400/20 text-amber-200' :
                  'bg-red-400/20 text-red-200'
                }`}>
                  {merchant.status === 'active' ? '营业中' : merchant.status === 'pending' ? '审核中' : merchant.status}
                </span>
              </div>
            </div>

            {/* Product Management */}
            <div className="rounded-2xl bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-base font-bold text-neutral-900">商品管理</h3>
                <button
                  onClick={() => setShowAddProduct(true)}
                  disabled={merchant.status !== 'active'}
                  className="rounded-xl bg-primary-500 px-4 py-2 text-xs font-bold text-white hover:bg-primary-600 disabled:opacity-50"
                >
                  + 上架商品
                </button>
              </div>

              {showAddProduct && (
                <div className="mb-4 rounded-xl border border-primary-100 bg-primary-50/50 p-4 space-y-3">
                  <h4 className="text-sm font-semibold text-primary-700">上架新商品</h4>
                  <input
                    type="text" placeholder="商品名称" value={productForm.name}
                    onChange={e => setProductForm(prev => ({ ...prev, name: e.target.value }))}
                    className="w-full rounded-lg border border-neutral-200 bg-white px-3 py-2.5 text-sm focus:border-primary-400 focus:outline-none"
                  />
                  <div className="grid grid-cols-2 gap-3">
                    <select
                      value={productForm.category}
                      onChange={e => setProductForm(prev => ({ ...prev, category: e.target.value }))}
                      className="rounded-lg border border-neutral-200 bg-white px-3 py-2.5 text-sm focus:border-primary-400 focus:outline-none"
                    >
                      <option value="food">宠物粮食</option>
                      <option value="medicine">医药保健</option>
                      <option value="toy">趣味玩具</option>
                      <option value="nest">温馨小窝</option>
                      <option value="hygiene">清洁护理</option>
                      <option value="accessory">时尚配件</option>
                      <option value="clothing">萌宠服饰</option>
                    </select>
                    <input
                      type="number" placeholder="库存数量" value={productForm.stock || ''}
                      onChange={e => setProductForm(prev => ({ ...prev, stock: parseInt(e.target.value) || 0 }))}
                      className="rounded-lg border border-neutral-200 bg-white px-3 py-2.5 text-sm focus:border-primary-400 focus:outline-none"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <input
                      type="number" placeholder="售价" value={productForm.price || ''}
                      onChange={e => setProductForm(prev => ({ ...prev, price: parseFloat(e.target.value) || 0 }))}
                      className="rounded-lg border border-neutral-200 bg-white px-3 py-2.5 text-sm focus:border-primary-400 focus:outline-none"
                    />
                    <input
                      type="number" placeholder="原价（选填）" value={productForm.original_price || ''}
                      onChange={e => setProductForm(prev => ({ ...prev, original_price: parseFloat(e.target.value) || 0 }))}
                      className="rounded-lg border border-neutral-200 bg-white px-3 py-2.5 text-sm focus:border-primary-400 focus:outline-none"
                    />
                  </div>
                  <textarea
                    placeholder="商品描述" value={productForm.description}
                    onChange={e => setProductForm(prev => ({ ...prev, description: e.target.value }))}
                    rows={2}
                    className="w-full resize-none rounded-lg border border-neutral-200 bg-white px-3 py-2.5 text-sm focus:border-primary-400 focus:outline-none"
                  />
                  <input
                    type="text" placeholder="标签（逗号分隔）" value={productForm.tags}
                    onChange={e => setProductForm(prev => ({ ...prev, tags: e.target.value }))}
                    className="w-full rounded-lg border border-neutral-200 bg-white px-3 py-2.5 text-sm focus:border-primary-400 focus:outline-none"
                  />
                  {merchant.merchant_type === 'tcm' && (
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox" checked={productForm.is_tcm_product}
                        onChange={e => setProductForm(prev => ({ ...prev, is_tcm_product: e.target.checked }))}
                        className="h-4 w-4 rounded border-neutral-300 text-emerald-500 focus:ring-emerald-500"
                      />
                      <span className="text-sm text-neutral-700">标记为中药产品</span>
                    </label>
                  )}
                  <div className="flex gap-2">
                    <button onClick={() => setShowAddProduct(false)} className="flex-1 rounded-lg border border-neutral-200 py-2 text-xs font-medium text-neutral-600 hover:bg-neutral-50">取消</button>
                    <button onClick={handleAddProduct} disabled={!productForm.name || productForm.price <= 0} className="flex-1 rounded-lg bg-primary-500 py-2 text-xs font-bold text-white hover:bg-primary-600 disabled:opacity-50">上架</button>
                  </div>
                </div>
              )}

              {products.length === 0 ? (
                <div className="py-10 text-center">
                  <span className="text-4xl">📦</span>
                  <p className="mt-2 text-sm text-neutral-500">暂无商品，点击上方按钮上架</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {products.map(product => (
                    <div key={product.product_id} className="flex items-center gap-3 rounded-xl border border-neutral-100 p-3">
                      <div className="h-14 w-14 flex-shrink-0 overflow-hidden rounded-lg bg-neutral-100">
                        {product.image_url ? (
                          <img src={product.image_url} alt="" className="h-full w-full object-cover" />
                        ) : (
                          <span className="flex h-full items-center justify-center text-2xl">📦</span>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="truncate text-sm font-medium text-neutral-900">{product.name}</p>
                        <div className="mt-1 flex items-center gap-2 text-xs text-neutral-400">
                          <span>¥{product.price.toFixed(2)}</span>
                          <span>库存{product.stock}</span>
                          <span>已售{product.sales_count}</span>
                        </div>
                      </div>
                      <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                        product.status === 'on_sale' ? 'bg-emerald-50 text-emerald-600' : 'bg-neutral-100 text-neutral-400'
                      }`}>
                        {product.status === 'on_sale' ? '在售' : '下架'}
                      </span>
                      <button
                        onClick={() => handleDeleteProduct(product.product_id)}
                        className="p-1 text-neutral-300 hover:text-red-500"
                      >
                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
