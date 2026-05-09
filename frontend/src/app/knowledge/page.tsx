'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { encyclopediaApi, CATEGORY_CONFIG, SEVERITY_CONFIG, type BreedSummary, type HealthConditionSummary, type HealthCategoryGroup } from '@/api/encyclopedia';

const speciesList = [
  { id: 'cat', name: '🐱 猫咪', gradient: 'from-primary-400 to-primary-500', desc: '了解猫咪品种和健康知识' },
  { id: 'dog', name: '🐶 狗狗', gradient: 'from-accent-400 to-accent-500', desc: '了解狗狗品种和健康知识' },
];

const knowledgeModules = [
  {
    id: 'breeds',
    name: '品种百科',
    icon: '📚',
    description: '猫狗常见品种详细介绍，包括标准特征、性格特点和饲养要求',
    gradient: 'from-success-400 to-accent-500',
  },
  {
    id: 'health',
    name: '健康知识',
    icon: '🏥',
    description: '常见病症数据库，按症状分类，提供专业护理建议',
    gradient: 'from-secondary-400 to-primary-500',
  },
];

export default function KnowledgeHubPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<{ breeds: BreedSummary[]; conditions: HealthConditionSummary[] } | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [showSearch, setShowSearch] = useState(false);

  const handleSearch = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setIsSearching(true);
    try {
      const results = await encyclopediaApi.searchKnowledge(searchQuery);
      setSearchResults(results);
      setShowSearch(true);
    } catch {
      setSearchResults({ breeds: [], conditions: [] });
    } finally {
      setIsSearching(false);
    }
  }, [searchQuery]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-neutral-50 to-white">
      {/* Mobile header */}
      <header className="sticky top-0 z-40 border-b border-neutral-100 bg-white/80 backdrop-blur-xl md:hidden">
        <div className="flex items-center justify-between px-4 py-3">
          <h1 className="text-lg font-bold text-neutral-900">📖 宠物知识</h1>
        </div>
      </header>

      <div className="mx-auto max-w-5xl px-4 py-6">
        {/* Hero */}
        <div className="mb-8 overflow-hidden rounded-3xl bg-gradient-to-br from-primary-500 via-primary-600 to-secondary-400 p-8 text-white shadow-lg md:p-12">
          <h2 className="text-2xl font-bold md:text-3xl">宠物知识科普</h2>
          <p className="mt-2 text-white/80">了解宠物品种特性，掌握健康护理知识，做更懂宠物的主人</p>

          <form onSubmit={handleSearch} className="mt-6 max-w-xl">
            <div className="relative">
              <svg className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="搜索品种名称、病症、关键词..."
                className="w-full rounded-2xl border border-white/20 bg-white/15 py-3.5 pl-12 pr-4 text-sm text-white placeholder-white/60 backdrop-blur transition-all focus:border-white/40 focus:outline-none focus:ring-4 focus:ring-white/20"
              />
              {isSearching && (
                <div className="absolute right-4 top-1/2 -translate-y-1/2">
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                </div>
              )}
            </div>
          </form>
        </div>

        {/* Search Results */}
        {showSearch && searchResults && (
          <div className="mb-8 rounded-2xl border border-neutral-200 bg-white p-6 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="font-semibold text-neutral-900">搜索结果</h3>
              <button onClick={() => { setShowSearch(false); setSearchResults(null); }} className="text-sm text-neutral-400 hover:text-neutral-600">
                关闭
              </button>
            </div>
            {searchResults.breeds.length === 0 && searchResults.conditions.length === 0 ? (
              <p className="text-sm text-neutral-500">未找到相关结果，请尝试其他关键词</p>
            ) : (
              <div className="space-y-4">
                {searchResults.breeds.length > 0 && (
                  <div>
                    <p className="mb-2 text-xs font-semibold text-neutral-400">📚 品种</p>
                    <div className="flex flex-wrap gap-2">
                      {searchResults.breeds.map(b => (
                        <Link key={b.id} href={`/knowledge/breeds/${b.id}`}
                          className="rounded-full bg-primary-50 px-3 py-1.5 text-xs text-primary-700 transition-colors hover:bg-primary-100">
                          {b.image_emoji} {b.name}
                        </Link>
                      ))}
                    </div>
                  </div>
                )}
                {searchResults.conditions.length > 0 && (
                  <div>
                    <p className="mb-2 text-xs font-semibold text-neutral-400">🏥 健康知识</p>
                    <div className="flex flex-wrap gap-2">
                      {searchResults.conditions.map(c => (
                        <Link key={c.id} href={`/knowledge/health/${c.id}`}
                          className="rounded-full bg-secondary-50 px-3 py-1.5 text-xs text-secondary-700 transition-colors hover:bg-secondary-100">
                          {c.image_emoji} {c.name}
                        </Link>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Knowledge Modules */}
        <div className="mb-8 grid gap-4 md:grid-cols-2">
          {knowledgeModules.map(mod => (
            <div key={mod.id} className="overflow-hidden rounded-2xl border border-neutral-100 bg-white shadow-sm transition-all hover:shadow-md">
              <div className={`bg-gradient-to-br ${mod.gradient} p-6 text-white`}>
                <span className="text-3xl">{mod.icon}</span>
                <h3 className="mt-2 text-lg font-bold">{mod.name}</h3>
                <p className="mt-1 text-sm text-white/80">{mod.description}</p>
              </div>
              <div className="p-4">
                <div className="flex items-center justify-between">
                  <p className="text-xs text-neutral-400">选择物种查看详情</p>
                  <svg className="h-4 w-4 text-neutral-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Species Selection */}
        <h3 className="mb-4 text-lg font-bold text-neutral-900">选择物种</h3>
        <div className="grid gap-4 sm:grid-cols-2">
          {speciesList.map(s => (
            <Link
              key={s.id}
              href={`/knowledge/breeds/${s.id}`}
              className="group relative overflow-hidden rounded-2xl bg-white shadow-sm transition-all hover:shadow-xl hover:-translate-y-1"
            >
              <div className={`bg-gradient-to-br ${s.gradient} p-6 text-white`}>
                <span className="text-2xl font-bold">{s.name}</span>
                <p className="mt-1 text-sm text-white/80">{s.desc}</p>
              </div>
              <div className="flex gap-2 border-t border-neutral-100 p-4">
              <Link href={`/knowledge/breeds?species=${s.id}`}
                  className="flex-1 rounded-xl bg-neutral-100 py-2 text-center text-xs font-medium text-neutral-600 transition-colors hover:bg-primary-50 hover:text-primary-600">
                  📚 品种百科
                </Link>
                <Link href={`/knowledge/health?species=${s.id}`}
                  className="flex-1 rounded-xl bg-neutral-100 py-2 text-center text-xs font-medium text-neutral-600 transition-colors hover:bg-secondary-50 hover:text-secondary-600">
                  🏥 健康知识
                </Link>
              </div>
            </Link>
          ))}
        </div>

        <div className="h-20 md:h-0" />
      </div>
    </div>
  );
}
