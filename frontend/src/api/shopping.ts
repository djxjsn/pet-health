'use client';

import { apiClient } from './client';

export interface Product {
  _id: string;
  product_id: string;
  name: string;
  brand?: string;
  category: string;
  subcategory?: string;
  price: number;
  original_price?: number;
  currency: string;
  image_url?: string;
  image_urls: string[];
  description?: string;
  ingredients?: Record<string, unknown>[];
  nutrition_info?: Record<string, unknown>;
  suitable_for?: string[];
  tags: string[];
  rating: number;
  review_count: number;
  sales_count: number;
  stock: number;
  stock_status: string;
  merchant_id?: string;
  merchant_name?: string;
  is_tcm_product: boolean;
  tcm_properties?: Record<string, unknown>;
  specifications?: Record<string, unknown>[];
  status: string;
  created_at?: string;
  updated_at?: string;
}

export interface ProductListResult {
  products: Product[];
  total: number;
  page: number;
  page_size: number;
}

export interface CartItem {
  cart_item_id: string;
  user_id: string;
  product_id: string;
  product_name: string;
  product_image_url?: string;
  price: number;
  quantity: number;
  merchant_id?: string;
  merchant_name?: string;
  selected: boolean;
  stock?: number;
  stock_status?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CartData {
  items: CartItem[];
  total_count: number;
  selected_count: number;
  total_amount: number;
  selected_amount: number;
}

export interface OrderItem {
  order_item_id: string;
  product_id: string;
  product_name: string;
  product_image_url?: string;
  product_category?: string;
  price: number;
  quantity: number;
  subtotal: number;
  merchant_id?: string;
}

export interface Order {
  order_id: string;
  user_id: string;
  order_no: string;
  items: OrderItem[];
  total_amount: number;
  discount_amount: number;
  freight_amount: number;
  pay_amount: number;
  status: string;
  payment_method?: string;
  payment_time?: string;
  shipping_name?: string;
  shipping_phone?: string;
  shipping_address?: string;
  shipping_province?: string;
  shipping_city?: string;
  shipping_district?: string;
  express_company?: string;
  express_no?: string;
  shipped_time?: string;
  delivered_time?: string;
  completed_time?: string;
  cancelled_time?: string;
  cancel_reason?: string;
  remark?: string;
  is_reviewed: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface OrderListResult {
  orders: Order[];
  total: number;
  page: number;
  page_size: number;
}

export interface Review {
  review_id: string;
  user_id: string;
  user_nickname?: string;
  user_avatar_url?: string;
  order_id: string;
  order_item_id: string;
  product_id: string;
  product_name: string;
  merchant_id?: string;
  rating: number;
  content?: string;
  image_urls: string[];
  reply_content?: string;
  replied_at?: string;
  is_anonymous: boolean;
  like_count: number;
  status: string;
  tags: string[];
  pet_info?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
}

export interface ReviewListResult {
  reviews: Review[];
  total: number;
  page: number;
  page_size: number;
  rating_stats?: {
    avg_rating: number;
    total_count: number;
    distribution: Record<string, number>;
  };
}

export interface Merchant {
  merchant_id: string;
  user_id: string;
  merchant_name: string;
  merchant_type: string;
  logo_url?: string;
  cover_image_url?: string;
  description?: string;
  contact_phone?: string;
  contact_email?: string;
  address?: string;
  province?: string;
  city?: string;
  district?: string;
  business_license?: string;
  status: string;
  rating: number;
  review_count: number;
  total_sales: number;
  product_count: number;
  tags: string[];
  is_verified: boolean;
  tcm_certification?: Record<string, unknown>;
  shipping_policy?: Record<string, unknown>;
  return_policy?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
}

export interface MerchantListResult {
  merchants: Merchant[];
  total: number;
  page: number;
  page_size: number;
}

export interface HotSearchItem {
  keyword: string;
  score: number;
}

export interface CategoryStats {
  total_products: number;
  by_category: Record<string, number>;
}

export const shoppingApi = {
  getProducts: async (params?: {
    query?: string;
    category?: string;
    price_min?: number;
    price_max?: number;
    merchant_id?: string;
    is_tcm?: boolean;
    sort_by?: string;
    sort_order?: number;
    page?: number;
    page_size?: number;
  }): Promise<ProductListResult> => {
    return apiClient.get('/ecommerce/products', params as Record<string, string | number | boolean>);
  },

  getProduct: async (productId: string): Promise<Product> => {
    return apiClient.get(`/ecommerce/products/${productId}`);
  },

  getHotSearch: async (limit: number = 10): Promise<{ keywords: HotSearchItem[] }> => {
    return apiClient.get('/ecommerce/hot-search', { limit });
  },

  getCategoryStats: async (): Promise<CategoryStats> => {
    return apiClient.get('/ecommerce/categories');
  },

  addToCart: async (userId: string, productId: string, quantity: number = 1): Promise<CartItem> => {
    return apiClient.post(`/ecommerce/cart/add?user_id=${userId}`, { product_id: productId, quantity });
  },

  getCart: async (userId: string): Promise<CartData> => {
    return apiClient.get('/ecommerce/cart', { user_id: userId });
  },

  updateCartItem: async (userId: string, cartItemId: string, data: { quantity?: number; selected?: boolean }): Promise<CartItem> => {
    return apiClient.put(`/ecommerce/cart/${cartItemId}?user_id=${userId}`, data);
  },

  removeCartItem: async (userId: string, cartItemId: string): Promise<void> => {
    await apiClient.delete(`/ecommerce/cart/${cartItemId}?user_id=${userId}`);
  },

  updateCartSelection: async (userId: string, selected: boolean, itemIds?: string[]): Promise<void> => {
    await apiClient.put(`/ecommerce/cart/select?user_id=${userId}`, { selected, item_ids: itemIds });
  },

  clearCart: async (userId: string): Promise<void> => {
    await apiClient.delete(`/ecommerce/cart/clear?user_id=${userId}`);
  },

  createOrder: async (userId: string, data: {
    shipping_name: string;
    shipping_phone: string;
    shipping_address: string;
    shipping_province?: string;
    shipping_city?: string;
    shipping_district?: string;
    remark?: string;
    cart_item_ids?: string[];
  }): Promise<Order> => {
    return apiClient.post(`/ecommerce/orders?user_id=${userId}`, data);
  },

  getOrders: async (userId: string, params?: { status?: string; page?: number; page_size?: number }): Promise<OrderListResult> => {
    return apiClient.get('/ecommerce/orders', { user_id: userId, ...params });
  },

  getOrder: async (orderId: string): Promise<Order> => {
    return apiClient.get(`/ecommerce/orders/${orderId}`);
  },

  payOrder: async (orderId: string, paymentMethod: string): Promise<void> => {
    await apiClient.post(`/ecommerce/orders/${orderId}/pay`, { payment_method: paymentMethod });
  },

  cancelOrder: async (orderId: string, cancelReason?: string): Promise<void> => {
    await apiClient.post(`/ecommerce/orders/${orderId}/cancel`, { cancel_reason: cancelReason });
  },

  confirmOrder: async (orderId: string): Promise<void> => {
    await apiClient.post(`/ecommerce/orders/${orderId}/confirm`);
  },

  getProductReviews: async (productId: string, params?: { page?: number; page_size?: number; sort_by?: string }): Promise<ReviewListResult> => {
    return apiClient.get(`/ecommerce/reviews/product/${productId}`, params);
  },

  createReview: async (userId: string, data: {
    order_id: string;
    order_item_id: string;
    product_id: string;
    rating: number;
    content?: string;
    image_urls?: string[];
    is_anonymous?: boolean;
    tags?: string[];
    pet_info?: Record<string, unknown>;
  }): Promise<Review> => {
    return apiClient.post(`/ecommerce/reviews?user_id=${userId}`, data);
  },

  likeReview: async (reviewId: string): Promise<void> => {
    await apiClient.post(`/ecommerce/reviews/${reviewId}/like`);
  },

  getMerchants: async (params?: { status?: string; merchant_type?: string; page?: number; page_size?: number }): Promise<MerchantListResult> => {
    return apiClient.get('/ecommerce/merchants', params);
  },

  getMerchant: async (merchantId: string): Promise<Merchant> => {
    return apiClient.get(`/ecommerce/merchants/${merchantId}`);
  },

  getMyMerchant: async (userId: string): Promise<Merchant> => {
    return apiClient.get(`/ecommerce/merchants/me/${userId}`);
  },

  createMerchant: async (userId: string, data: Record<string, unknown>): Promise<Merchant> => {
    return apiClient.post(`/ecommerce/merchants?user_id=${userId}`, data);
  },

  updateMerchant: async (merchantId: string, data: Record<string, unknown>): Promise<Merchant> => {
    return apiClient.put(`/ecommerce/merchants/${merchantId}`, data);
  },

  createProduct: async (merchantId: string, data: Record<string, unknown>): Promise<Product> => {
    return apiClient.post(`/ecommerce/products?merchant_id=${merchantId}`, data);
  },

  updateProduct: async (productId: string, data: Record<string, unknown>): Promise<Product> => {
    return apiClient.put(`/ecommerce/products/${productId}`, data);
  },

  deleteProduct: async (productId: string): Promise<void> => {
    await apiClient.delete(`/ecommerce/products/${productId}`);
  },

  shipOrder: async (orderId: string, expressCompany: string, expressNo: string): Promise<void> => {
    await apiClient.post(`/ecommerce/orders/${orderId}/ship`, { express_company: expressCompany, express_no: expressNo });
  },

  replyReview: async (reviewId: string, merchantId: string, replyContent: string): Promise<void> => {
    await apiClient.post(`/ecommerce/reviews/${reviewId}/reply?merchant_id=${merchantId}`, { reply_content: replyContent });
  },
};
