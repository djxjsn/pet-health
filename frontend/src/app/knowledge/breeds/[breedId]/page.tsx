'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { encyclopediaApi, type BreedDetail } from '@/api/encyclopedia';

export default function BreedDetailPage() {
  const params = useParams();
  const breedId = params.breedId as string;
  const [breed, setBreed] = useState<BreedDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    encyclopediaApi.getBreedDetail(breedId)
      .then(setBreed)
      .finally(() => setIsLoading(false));
  }, [breedId]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-neutral-50">
        <div className="mx-auto max-w-4xl px-4 py-8">
          <div className="animate-pulse space-y-6">
            <div className="h-8 w-48 rounded-lg bg-neutral-200" />
            <div className="h-64 rounded-3xl bg-neutral-200" />
            <div className="h-4 w-full rounded bg-neutral-200" />
            <div className="h-4 w-3/4 rounded bg-neutral-200" />
          </div>
        </div>
      </div>
    );
  }

  if (!breed) {
    return (
      <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
        <div className="text-center">
          <span className="text-6xl">🔍</span>
          <p className="mt-4 text-lg font-semibold text-neutral-900">品种未找到</p>
          <Link href="/knowledge" className="mt-4 inline-block text-primary-600 hover:text-primary-700">
            返回知识首页
          </Link>
        </div>
      </div>
    );
  }

  const speciesLink = breed.species === 'cat' ? '/knowledge/breeds/cat' : '/knowledge/breeds/dog';
  const speciesName = breed.species === 'cat' ? '猫咪' : '狗狗';

  return (
    <div className="min-h-screen bg-gradient-to-b from-neutral-50 to-white">
      {/* Mobile header */}
      <header className="sticky top-0 z-40 border-b border-neutral-100 bg-white/80 backdrop-blur-xl md:hidden">
        <div className="flex items-center gap-3 px-4 py-3">
          <Link href={speciesLink} className="rounded-lg p-1 text-neutral-500 hover:bg-neutral-100">
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </Link>
          <h1 className="truncate text-lg font-bold text-neutral-900">{breed.name}</h1>
        </div>
      </header>

      <div className="mx-auto max-w-4xl px-4 py-6">
        {/* Back link (desktop) */}
        <Link href={speciesLink} className="mb-6 hidden items-center gap-1 text-sm text-neutral-500 hover:text-primary-600 md:inline-flex">
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          返回{speciesName}品种列表
        </Link>

        {/* Hero */}
        <div className="mb-8 overflow-hidden rounded-3xl bg-gradient-to-br from-primary-400 via-primary-500 to-secondary-400 p-8 text-white shadow-lg">
          <div className="flex items-center gap-4">
            <span className="flex h-16 w-16 items-center justify-center rounded-2xl bg-white/20 text-4xl backdrop-blur">
              {breed.image_emoji}
            </span>
            <div>
              <h2 className="text-2xl font-bold md:text-3xl">{breed.name}</h2>
              {breed.english_name && (
                <p className="text-white/70">{breed.english_name}</p>
              )}
              <div className="mt-2 flex items-center gap-2">
                <span className="rounded-full bg-white/20 px-3 py-0.5 text-xs backdrop-blur">{breed.category}</span>
                <span className="rounded-full bg-white/20 px-3 py-0.5 text-xs backdrop-blur">{breed.features.origin}</span>
              </div>
            </div>
          </div>
          <p className="mt-4 text-white/90 text-sm leading-relaxed">{breed.description}</p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          {/* Features */}
          <div className="rounded-2xl border border-neutral-100 bg-white p-6 shadow-sm">
            <h3 className="mb-4 flex items-center gap-2 text-lg font-bold text-neutral-900">
              <svg className="h-5 w-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              标准特征
            </h3>
            <div className="grid grid-cols-2 gap-3">
              {[
                { label: '原产地', value: breed.features.origin },
                { label: '体型', value: breed.features.size },
                { label: '体重', value: breed.features.weight },
                { label: '寿命', value: breed.features.lifespan },
                { label: '被毛', value: breed.features.coat },
              ].map(item => (
                <div key={item.label} className="rounded-xl bg-neutral-50 p-3">
                  <p className="text-xs text-neutral-400">{item.label}</p>
                  <p className="mt-0.5 text-sm font-medium text-neutral-900">{item.value}</p>
                </div>
              ))}
              <div className="col-span-2 rounded-xl bg-neutral-50 p-3">
                <p className="text-xs text-neutral-400">常见毛色</p>
                <div className="mt-1 flex flex-wrap gap-1">
                  {breed.features.colors.map(color => (
                    <span key={color} className="rounded-full bg-white px-2 py-0.5 text-xs text-neutral-700 shadow-sm">{color}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Personality */}
          <div className="rounded-2xl border border-neutral-100 bg-white p-6 shadow-sm">
            <h3 className="mb-4 flex items-center gap-2 text-lg font-bold text-neutral-900">
              <svg className="h-5 w-5 text-secondary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
              性格特点
            </h3>
            <ul className="space-y-2">
              {breed.personality.map((item, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-secondary-100 text-xs text-secondary-600">{i + 1}</span>
                  <span className="text-sm text-neutral-700">{item}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Care Requirements */}
          <div className="rounded-2xl border border-neutral-100 bg-white p-6 shadow-sm">
            <h3 className="mb-4 flex items-center gap-2 text-lg font-bold text-neutral-900">
              <svg className="h-5 w-5 text-success-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              饲养要求
            </h3>
            <div className="space-y-3">
              {[
                { label: '运动需求', value: breed.care_requirements.exercise, icon: '🏃' },
                { label: '美容护理', value: breed.care_requirements.grooming, icon: '🪮' },
                { label: '饮食建议', value: breed.care_requirements.diet, icon: '🍽️' },
                { label: '训练难度', value: breed.care_requirements.training, icon: '🎓' },
              ].map(item => (
                <div key={item.label} className="rounded-xl bg-neutral-50 p-3">
                  <div className="flex items-center gap-2">
                    <span>{item.icon}</span>
                    <p className="text-xs font-medium text-neutral-500">{item.label}</p>
                  </div>
                  <p className="mt-0.5 text-sm text-neutral-800">{item.value}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Health Issues + Suitable For */}
          <div className="space-y-6">
            <div className="rounded-2xl border border-neutral-100 bg-white p-6 shadow-sm">
              <h3 className="mb-4 flex items-center gap-2 text-lg font-bold text-neutral-900">
                <svg className="h-5 w-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.963-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
                常见健康问题
              </h3>
              <div className="flex flex-wrap gap-2">
                {breed.health_issues.map(issue => (
                  <span key={issue} className="rounded-full bg-primary-50 px-3 py-1 text-xs font-medium text-primary-700">{issue}</span>
                ))}
              </div>
            </div>

            <div className="rounded-2xl border border-neutral-100 bg-white p-6 shadow-sm">
              <h3 className="mb-4 flex items-center gap-2 text-lg font-bold text-neutral-900">
                <svg className="h-5 w-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                适合人群
              </h3>
              <div className="flex flex-wrap gap-2">
                {breed.suitable_for.map(item => (
                  <span key={item} className="rounded-full bg-primary-50 px-3 py-1 text-xs font-medium text-primary-700">{item}</span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="mt-8 rounded-2xl border border-primary-200 bg-primary-50 p-4 text-sm text-primary-800">
          <p className="font-medium">⚠️ 温馨提示</p>
          <p className="mt-1">品种信息仅供参考。每只宠物都是独立的个体，性格和健康状况可能存在个体差异。如有饲养决策需求，建议咨询专业繁育者或兽医。</p>
        </div>

        <div className="h-20 md:h-0" />
      </div>
    </div>
  );
}
