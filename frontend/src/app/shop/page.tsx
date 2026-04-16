'use client';

import { useState, useCallback, useEffect } from 'react';
import OptimizedImage from '@/components/OptimizedImage';

interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  originalPrice?: number;
  image: string;
  category: string;
  rating: number;
  reviewCount: number;
  tags: string[];
  inStock: boolean;
}

const categories = [
  { id: 'all', name: '全部' },
  { id: 'food', name: '食品' },
  { id: 'medicine', name: '药品' },
  { id: 'toy', name: '玩具' },
  { id: 'care', name: '护理用品' },
];

const mockProducts: Product[] = [
  {
    id: 'prod-001',
    name: '皇家猫粮 成猫专用',
    description: '营养均衡配方，适合成年猫咪日常喂养。富含优质蛋白和必需脂肪酸。',
    price: 299,
    originalPrice: 359,
    image: '/images/products/cat-food.jpg',
    category: 'food',
    rating: 4.8,
    reviewCount: 1256,
    tags: ['热销', '官方认证'],
    inStock: true,
  },
  {
    id: 'prod-002',
    name: '宠物驱虫滴剂 犬猫通用',
    description: '广谱驱虫，有效预防跳蚤、蜱虫、线虫等寄生虫感染。',
    price: 89,
    image: '/images/products/dewormer.jpg',
    category: 'medicine',
    rating: 4.9,
    reviewCount: 3421,
    tags: ['必备'],
    inStock: true,
  },
  {
    id: 'prod-003',
    name: '智能互动玩具球',
    description: '自动滚动、发光发声，激发宠物运动天性，减少分离焦虑。',
    price: 159,
    originalPrice: 199,
    image: '/images/products/toy-ball.jpg',
    category: 'toy',
    rating: 4.5,
    reviewCount: 567,
    tags: ['新品', '智能'],
    inStock: true,
  },
  {
    id: 'prod-004',
    name: '天然沐浴露 无泪配方',
    description: '温和清洁，不刺激眼睛。含芦荟精华，滋润毛发。',
    price: 68,
    image: '/images/products/shampoo.jpg',
    category: 'care',
    rating: 4.6,
    reviewCount: 892,
    tags: ['天然成分'],
    inStock: true,
  },
  {
    id: 'prod-005',
    name: '关节保健软骨素',
    description: '适合老年犬猫，支持关节健康，缓解关节炎症状。',
    price: 128,
    image: '/images/products/joint-care.jpg',
    category: 'medicine',
    rating: 4.7,
    reviewCount: 2134,
    tags: ['老年宠适用'],
    inStock: false,
  },
  {
    id: 'prod-006',
    name: '猫抓板 剑麻材质',
    description: '保护家具，满足猫咪磨爪需求。可立式/卧式两用。',
    price: 99,
    originalPrice: 139,
    image: '/images/products/scratch-post.jpg',
    category: 'care',
    rating: 4.4,
    reviewCount: 445,
    tags: ['热销'],
    inStock: true,
  },
];

export default function ShopPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sortBy, setSortBy] = useState<'popular' | 'price-asc' | 'price-desc'>('popular');
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const loadProducts = async () => {
      setIsLoading(true);
      await new Promise(resolve => setTimeout(resolve, 300));
      setProducts(mockProducts);
      setIsLoading(false);
    };
    
    loadProducts();
  }, []);

  const filteredProducts = products
    .filter(p => selectedCategory === 'all' || p.category === selectedCategory)
    .filter(p => 
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.description.toLowerCase().includes(searchQuery.toLowerCase())
    )
    .sort((a, b) => {
      switch (sortBy) {
        case 'price-asc':
          return a.price - b.price;
        case 'price-desc':
          return b.price - a.price;
        default:
          return b.reviewCount - a.reviewCount;
      }
    });

  const handleAddToCart = useCallback((product: Product) => {
    alert(`已添加「${product.name}」到购物车`);
  }, []);

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center gap-0.5">
        {[1, 2, 3, 4, 5].map(star => (
          <svg
            key={star}
            className={`h-4 w-4 ${star <= Math.floor(rating) ? 'text-secondary-500' : 'text-neutral-200'}`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        ))}
        <span className="ml-1 text-xs text-neutral-500">{rating}</span>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-neutral-50">
      <header className="sticky top-0 z-40 border-b bg-white px-4 py-3 md:hidden">
        <h1 className="text-lg font-semibold text-neutral-900">智能商城</h1>
      </header>

      <div className="mx-auto max-w-7xl px-4 py-6">
        <div className="mb-6">
          <div className="relative">
            <svg
              className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-neutral-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="搜索商品..."
              className="w-full rounded-lg border border-neutral-200 bg-white py-2.5 pl-10 pr-4 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-200"
            />
          </div>
        </div>

        <div className="mb-6 overflow-x-auto">
          <div className="flex gap-2 pb-2">
            {categories.map(cat => (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`
                  flex-shrink-0 rounded-full px-4 py-2 text-sm font-medium transition-colors
                  ${selectedCategory === cat.id
                    ? 'bg-primary-600 text-white'
                    : 'bg-white text-neutral-700 hover:bg-neutral-100'
                  }
                `}
              >
                {cat.name}
              </button>
            ))}
          </div>
        </div>

        <div className="mb-6 flex items-center justify-between">
          <p className="text-sm text-neutral-500">
            共 {filteredProducts.length} 件商品
          </p>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
            className="rounded-lg border border-neutral-200 bg-white px-3 py-1.5 text-sm focus:border-primary-500 focus:outline-none"
          >
            <option value="popular">最热门</option>
            <option value="price-asc">价格从低到高</option>
            <option value="price-desc">价格从高到低</option>
          </select>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="animate-pulse rounded-lg bg-white p-4">
                <div className="mb-3 aspect-square rounded bg-neutral-200" />
                <div className="h-4 rounded bg-neutral-200" />
                <div className="mt-2 h-3 w-3/4 rounded bg-neutral-200" />
              </div>
            ))}
          </div>
        ) : filteredProducts.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-lg bg-white py-16 text-center">
            <svg className="mb-4 h-16 w-16 text-neutral-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
            <p className="font-medium text-neutral-900">暂无商品</p>
            <p className="mt-1 text-sm text-neutral-500">换个关键词试试吧</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
            {filteredProducts.map(product => (
              <div
                key={product.id}
                className="group overflow-hidden rounded-lg border bg-white transition-all hover:shadow-lg hover:-translate-y-0.5"
              >
                <div className="relative aspect-square bg-neutral-100">
                  <OptimizedImage
                    src={product.image}
                    alt={product.name}
                    fill
                    sizes="(max-width: 640px) 50vw, (max-width: 768px) 33vw, 25vw"
                    quality={80}
                    priority={filteredProducts.indexOf(product) < 4}
                    fallback={
                      <span className="flex h-full items-center justify-center text-4xl">
                        {product.category === 'food' && '🍖'}
                        {product.category === 'medicine' && '💊'}
                        {product.category === 'toy' && '🎾'}
                        {product.category === 'care' && '🧴'}
                      </span>
                    }
                    className="rounded-t-lg object-cover"
                  />
                  
                  {product.tags.length > 0 && (
                    <div className="absolute top-2 left-2 flex flex-wrap gap-1">
                      {product.tags.map(tag => (
                        <span
                          key={tag}
                          className="rounded-full bg-primary-100 px-2 py-0.5 text-xs font-medium text-primary-700"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}

                  {!product.inStock && (
                    <div className="absolute inset-0 flex items-center justify-center bg-black/40">
                      <span className="rounded-md bg-black/70 px-3 py-1 text-sm font-medium text-white">
                        暂缺货
                      </span>
                    </div>
                  )}
                </div>

                <div className="p-3">
                  <h3 className="truncate font-medium text-sm text-neutral-900 group-hover:text-primary-600">
                    {product.name}
                  </h3>
                  
                  <p className="mt-1 line-clamp-2 text-xs text-neutral-500">
                    {product.description}
                  </p>

                  <div className="mt-2">
                    {renderStars(product.rating)}
                  </div>

                  <div className="mt-3 flex items-end justify-between">
                    <div>
                      <span className="text-lg font-bold text-red-500">
                        ¥{product.price}
                      </span>
                      {product.originalPrice && (
                        <span className="ml-1.5 text-xs text-neutral-400 line-through">
                          ¥{product.originalPrice}
                        </span>
                      )}
                    </div>
                    
                    <button
                      onClick={() => handleAddToCart(product)}
                      disabled={!product.inStock}
                      className={`
                        rounded-lg px-3 py-1.5 text-sm font-medium transition-colors
                        ${product.inStock
                          ? 'bg-primary-600 text-white hover:bg-primary-700'
                          : 'cursor-not-allowed bg-neutral-100 text-neutral-400'
                        }
                      `}
                    >
                      {product.inStock ? '+ 购物车' : '缺货'}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="h-20 md:h-0" />
    </div>
  );
}
