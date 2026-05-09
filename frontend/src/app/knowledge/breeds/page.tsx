'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { encyclopediaApi, type BreedSummary } from '@/api/encyclopedia';

const speciesConfig: Record<string, { name: string; emoji: string; gradient: string }> = {
  cat: { name: '猫咪品种百科', emoji: '🐱', gradient: 'from-primary-400 to-primary-500' },
  dog: { name: '狗狗品种百科', emoji: '🐶', gradient: 'from-accent-400 to-accent-500' },
};

export default function BreedListPage() {
  const searchParams = useSearchParams();
  const species = searchParams.get('species') || 'cat';
  const [breeds, setBreeds] = useState<BreedSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const config = speciesConfig[species] || speciesConfig.cat;

  useEffect(() => {
    setIsLoading(true);
    encyclopediaApi.getBreeds(species).then(setBreeds).finally(() => setIsLoading(false));
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
          <p className="mt-2 text-white/80">共收录 {breeds.length} 个常见品种</p>

          {/* Species Tabs */}
          <div className="mt-4 flex gap-2">
            {Object.entries(speciesConfig).map(([key, cfg]) => (
              <Link
                key={key}
                href={`/knowledge/breeds?species=${key}`}
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

        {/* Breed Grid */}
        {isLoading ? (
          <div className="grid gap-4 md:grid-cols-2">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="animate-pulse rounded-2xl bg-white p-6 shadow-sm">
                <div className="mb-3 h-5 w-2/3 rounded bg-neutral-200" />
                <div className="h-4 w-full rounded bg-neutral-200" />
                <div className="mt-3 flex gap-2">
                  <div className="h-6 w-16 rounded-full bg-neutral-200" />
                  <div className="h-6 w-16 rounded-full bg-neutral-200" />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {breeds.map(breed => (
              <Link
                key={breed.id}
                href={`/knowledge/breeds/${breed.id}`}
                className="group rounded-2xl border border-neutral-100 bg-white p-5 shadow-sm transition-all hover:shadow-xl hover:-translate-y-1 hover:border-primary-100"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-neutral-100 to-neutral-200 text-2xl group-hover:from-primary-100 group-hover:to-primary-200 transition-all">
                      {breed.image_emoji}
                    </span>
                    <div>
                      <h3 className="font-bold text-neutral-900 group-hover:text-primary-600 transition-colors">{breed.name}</h3>
                      {breed.english_name && (
                        <p className="text-xs text-neutral-400">{breed.english_name}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-0.5">
                    {[...Array(10)].map((_, i) => (
                      <div key={i} className={`h-1.5 w-1.5 rounded-full ${i < breed.popularity ? 'bg-secondary-400' : 'bg-neutral-200'}`} />
                    ))}
                  </div>
                </div>
                <p className="mt-3 text-sm leading-relaxed text-neutral-500 line-clamp-2">{breed.summary}</p>
              </Link>
            ))}
          </div>
        )}

        <div className="h-20 md:h-0" />
      </div>
    </div>
  );
}
