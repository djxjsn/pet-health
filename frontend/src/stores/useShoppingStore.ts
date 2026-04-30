'use client';

import { create } from 'zustand';
import { shoppingApi, Product, CartData, Order, ReviewListResult, HotSearchItem, CategoryStats } from '@/api/shopping';

interface ShoppingState {
  products: Product[];
  totalProducts: number;
  currentPage: number;
  pageSize: number;
  isLoading: boolean;
  searchQuery: string;
  selectedCategory: string;
  sortBy: string;
  hotSearches: HotSearchItem[];
  categoryStats: CategoryStats | null;
  cart: CartData | null;
  cartLoading: boolean;
  orders: Order[];
  totalOrders: number;
  orderPage: number;
  orderStatus: string;
  ordersLoading: boolean;
  reviewData: ReviewListResult | null;
  reviewsLoading: boolean;

  fetchProducts: (params?: Record<string, unknown>) => Promise<void>;
  fetchProduct: (productId: string) => Promise<Product | null>;
  fetchHotSearches: () => Promise<void>;
  fetchCategoryStats: () => Promise<void>;
  setSearchQuery: (query: string) => void;
  setSelectedCategory: (category: string) => void;
  setSortBy: (sort: string) => void;
  setPage: (page: number) => void;

  fetchCart: (userId: string) => Promise<void>;
  addToCart: (userId: string, productId: string, quantity?: number) => Promise<void>;
  updateCartItem: (userId: string, cartItemId: string, data: { quantity?: number; selected?: boolean }) => Promise<void>;
  removeCartItem: (userId: string, cartItemId: string) => Promise<void>;
  updateCartSelection: (userId: string, selected: boolean, itemIds?: string[]) => Promise<void>;
  clearCart: (userId: string) => Promise<void>;

  createOrder: (userId: string, data: Record<string, unknown>) => Promise<Order | null>;
  fetchOrders: (userId: string, params?: Record<string, unknown>) => Promise<void>;
  fetchOrder: (orderId: string) => Promise<Order | null>;
  payOrder: (orderId: string, paymentMethod: string) => Promise<void>;
  cancelOrder: (orderId: string, cancelReason?: string) => Promise<void>;
  confirmOrder: (orderId: string) => Promise<void>;
  setOrderStatus: (status: string) => void;

  fetchProductReviews: (productId: string, params?: Record<string, unknown>) => Promise<void>;
  createReview: (userId: string, data: Record<string, unknown>) => Promise<void>;
  likeReview: (reviewId: string) => Promise<void>;
}

export const useShoppingStore = create<ShoppingState>()((set, get) => ({
  products: [],
  totalProducts: 0,
  currentPage: 1,
  pageSize: 20,
  isLoading: false,
  searchQuery: '',
  selectedCategory: '',
  sortBy: 'popular',
  hotSearches: [],
  categoryStats: null,
  cart: null,
  cartLoading: false,
  orders: [],
  totalOrders: 0,
  orderPage: 1,
  orderStatus: '',
  ordersLoading: false,
  reviewData: null,
  reviewsLoading: false,

  fetchProducts: async (params) => {
    set({ isLoading: true });
    try {
      const state = get();
      const sortMap: Record<string, { sort_by: string; sort_order: number }> = {
        popular: { sort_by: 'sales_count', sort_order: -1 },
        'price-asc': { sort_by: 'price', sort_order: 1 },
        'price-desc': { sort_by: 'price', sort_order: -1 },
        newest: { sort_by: 'created_at', sort_order: -1 },
        rating: { sort_by: 'rating', sort_order: -1 },
      };
      const sort = sortMap[state.sortBy] || sortMap.popular;
      const result = await shoppingApi.getProducts({
        query: state.searchQuery || undefined,
        category: state.selectedCategory || undefined,
        page: state.currentPage,
        page_size: state.pageSize,
        ...sort,
        ...params,
      });
      set({
        products: result.products,
        totalProducts: result.total,
        isLoading: false,
      });
    } catch {
      set({ isLoading: false });
    }
  },

  fetchProduct: async (productId) => {
    try {
      return await shoppingApi.getProduct(productId);
    } catch {
      return null;
    }
  },

  fetchHotSearches: async () => {
    try {
      const result = await shoppingApi.getHotSearch();
      set({ hotSearches: result.keywords });
    } catch { /* ignore */ }
  },

  fetchCategoryStats: async () => {
    try {
      const stats = await shoppingApi.getCategoryStats();
      set({ categoryStats: stats });
    } catch { /* ignore */ }
  },

  setSearchQuery: (query) => {
    set({ searchQuery: query, currentPage: 1 });
  },

  setSelectedCategory: (category) => {
    set({ selectedCategory: category, currentPage: 1 });
  },

  setSortBy: (sort) => {
    set({ sortBy: sort, currentPage: 1 });
  },

  setPage: (page) => {
    set({ currentPage: page });
  },

  fetchCart: async (userId) => {
    set({ cartLoading: true });
    try {
      const cart = await shoppingApi.getCart(userId);
      set({ cart, cartLoading: false });
    } catch {
      set({ cartLoading: false });
    }
  },

  addToCart: async (userId, productId, quantity = 1) => {
    await shoppingApi.addToCart(userId, productId, quantity);
    await get().fetchCart(userId);
  },

  updateCartItem: async (userId, cartItemId, data) => {
    await shoppingApi.updateCartItem(userId, cartItemId, data);
    await get().fetchCart(userId);
  },

  removeCartItem: async (userId, cartItemId) => {
    await shoppingApi.removeCartItem(userId, cartItemId);
    await get().fetchCart(userId);
  },

  updateCartSelection: async (userId, selected, itemIds) => {
    await shoppingApi.updateCartSelection(userId, selected, itemIds);
    await get().fetchCart(userId);
  },

  clearCart: async (userId) => {
    await shoppingApi.clearCart(userId);
    await get().fetchCart(userId);
  },

  createOrder: async (userId, data) => {
    const order = await shoppingApi.createOrder(userId, data);
    await get().fetchCart(userId);
    return order;
  },

  fetchOrders: async (userId, params) => {
    set({ ordersLoading: true });
    try {
      const state = get();
      const result = await shoppingApi.getOrders(userId, {
        status: state.orderStatus || undefined,
        page: state.orderPage,
        page_size: 20,
        ...params,
      });
      set({
        orders: result.orders,
        totalOrders: result.total,
        ordersLoading: false,
      });
    } catch {
      set({ ordersLoading: false });
    }
  },

  fetchOrder: async (orderId) => {
    try {
      return await shoppingApi.getOrder(orderId);
    } catch {
      return null;
    }
  },

  payOrder: async (orderId, paymentMethod) => {
    await shoppingApi.payOrder(orderId, paymentMethod);
  },

  cancelOrder: async (orderId, cancelReason) => {
    await shoppingApi.cancelOrder(orderId, cancelReason);
  },

  confirmOrder: async (orderId) => {
    await shoppingApi.confirmOrder(orderId);
  },

  setOrderStatus: (status) => {
    set({ orderStatus: status, orderPage: 1 });
  },

  fetchProductReviews: async (productId, params) => {
    set({ reviewsLoading: true });
    try {
      const result = await shoppingApi.getProductReviews(productId, {
        page: 1,
        page_size: 20,
        ...params,
      });
      set({ reviewData: result, reviewsLoading: false });
    } catch {
      set({ reviewsLoading: false });
    }
  },

  createReview: async (userId, data) => {
    await shoppingApi.createReview(userId, data);
  },

  likeReview: async (reviewId) => {
    await shoppingApi.likeReview(reviewId);
  },
}));
