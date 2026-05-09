'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { encyclopediaApi, CATEGORY_CONFIG, SEVERITY_CONFIG, type HealthCategoryGroup } from '@/api/encyclopedia';

const speciesConfig: Record<string, { name: string; emoji: string; gradient: string }> = {
  cat: { name: '猫咪健康知识', emoji: '🐱', gradient: 'from-primary-400 to-primary-500' },
  dog: { name: '狗狗健康知识', emoji: '🐶', gradient: 'from-accent-400 to-accent-500' },
  both: { name: '综合健康知识', emoji: '🐾', gradient: 'from-success-400 to-accent-500' },
};

const severityStyles: Record<string, string> = {
  mild: 'bg-success-50 text-success-700 border-success-200',
  moderate: 'bg-secondary-50 text-secondary-700 border-secondary-200',
  severe: 'bg-primary-50 text-primary-700 border-primary-200',
  emergency: 'bg-primary-50 text-primary-700 border-primary-200',
};

export default function HealthListPage() {
  const searchParams = useSearchParams();
  const species = searchParams.get('species') || 'cat';
  const [categories, setCategories] = useState<HealthCategoryGroup[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const config = speciesConfig[species] || speciesConfig.cat;

  useEffect(() => {
    setIsLoading(true);
    encyclopediaApi.getHealthConditions(species).then(setCategories).finally(() => setIsLoading(false));
  }, [species]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-neutral-50 to-white">
      <header className="sticky top-0 z-40 border-b border-neutral-100 bg-white/80 backdrop-blur-xl md:hidden">
        <div className="flex items-center gap-3 px-4 py-3">
          <Link href="/knowledge" className="rounded-lg p-1 text-neutral-500 hover:bg-neutral-100">
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </Link>
          <h1 className="text-lg font-bold text-neutral-900">{config.emoji} {config.name}</h1>
        </div>
      </header>

      <div className="mx-auto max-w-5xl px-4 py-6">
        {/* Header */}
        <div className={`mb-8 overflow-hidden rounded-3xl bg-gradient-to-br ${config.gradient} p-8 text-white shadow-lg`}>
          <Link href="/knowledge" className="mb-3 inline-flex items-center gap-1 text-sm text-white/70 hover:text-white">
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            返回知识首页
          </Link>
          <h2 className="text-2xl font-bold md:text-3xl">{config.name}</h2>
          <p className="mt-2 text-white/80">{categories.reduce((sum, c) => sum + c.conditions.length, 0)} 种常见病症，按系统分类</p>

          {/* Species Tabs */}
          <div className="mt-4 flex flex-wrap gap-2">
            {Object.entries(speciesConfig).map(([key, cfg]) => (
              <Link
                key={key}
                href={`/knowledge/health?species=${key}`}
                className={`rounded-xl px-4 py-2 text-sm font-medium transition-all ${
                  species === key
                    ? 'bg-white/25 text-white shadow-sm'
                    : 'bg-white/10 text-white/70 hover:bg-white/20 hover:text-white'
                }`}
              >
                {cfg.emoji} {cfg.name}
              </Link>
            ))}
          </div>
        </div>

        {/* Disclaimer */}
        <div className="mb-6 rounded-2xl border border-secondary-200 bg-secondary-50 p-4 text-sm text-secondary-800">
          <p className="font-medium">⚠️ 重要提示</p>
          <p className="mt-1">本页面提供的信息仅供参考和学习，不能替代专业兽医诊断。如有宠物健康问题，请及时咨询执业兽医。</p>
        </div>

        {/* Categories */}
        {isLoading ? (
          <div className="space-y-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="animate-pulse rounded-2xl bg-white p-6 shadow-sm">
                <div className="mb-4 h-6 w-32 rounded bg-neutral-200" />
                <div className="grid gap-3 md:grid-cols-2">
                  {[...Array(4)].map((_, j) => (
                    <div key={j} className="h-20 rounded-xl bg-neutral-100" />
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-6">
            {categories.map(group => {
              const catConfig = CATEGORY_CONFIG[group.category] || { label: group.category, emoji: '📋' };
              return (
                <div key={group.category} className="rounded-2xl border border-neutral-100 bg-white p-6 shadow-sm">
                  <h3 className="mb-4 text-lg font-bold text-neutral-900">
                    {catConfig.emoji} {catConfig.label}
                    <span className="ml-2 text-sm font-normal text-neutral-400">({group.conditions.length}种)</span>
                  </h3>
                  <div className="grid gap-3 md:grid-cols-2">
                    {group.conditions.map(condition => {
                      const sevConfig = SEVERITY_CONFIG[condition.severity] || { label: '未知', variant: 'safe' };
                      const sevStyle = severityStyles[condition.severity] || severityStyles.mild;
                      return (
                        <Link
                          key={condition.id}
                          href={`/knowledge/health/${condition.id}`}
                          className="group flex items-center gap-3 rounded-xl border border-neutral-100 p-4 transition-all hover:shadow-md hover:border-primary-100 hover:-translate-y-0.5"
                        >
                          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-neutral-100 text-lg group-hover:bg-primary-50">
                            {condition.image_emoji || '🏥'}
                          </span>
                          <div className="min-w-0 flex-1">
                            <p className="truncate text-sm font-semibold text-neutral-900 group-hover:text-primary-600 transition-colors">
                              {condition.name}
                            </p>
                            <div className="mt-1 flex items-center gap-2">
                              <span className={`rounded-full border px-2 py-0.5 text-xs font-medium ${sevStyle}`}>
                                {sevConfig.label}
                              </span>
                            </div>
                          </div>
                          <svg className="h-4 w-4 shrink-0 text-neutral-300 group-hover:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </Link>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        <div className="h-20 md:h-0" />
      </div>
    </div>
  );
}
