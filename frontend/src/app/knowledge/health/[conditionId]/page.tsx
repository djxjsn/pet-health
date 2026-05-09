'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { encyclopediaApi, SEVERITY_CONFIG, CATEGORY_CONFIG, type HealthCondition } from '@/api/encyclopedia';

const severityColors: Record<string, { bg: string; text: string; border: string; icon: string }> = {
  mild: { bg: 'bg-success-50', text: 'text-success-700', border: 'border-success-200', icon: '🟢' },
  moderate: { bg: 'bg-secondary-50', text: 'text-secondary-700', border: 'border-secondary-200', icon: '🟡' },
  severe: { bg: 'bg-primary-50', text: 'text-primary-700', border: 'border-primary-200', icon: '🔴' },
  emergency: { bg: 'bg-primary-50', text: 'text-primary-700', border: 'border-primary-200', icon: '🚨' },
};

const sectionStyles = {
  container: 'rounded-2xl border border-neutral-100 bg-white p-6 shadow-sm',
  title: 'mb-4 flex items-center gap-2 text-lg font-bold text-neutral-900',
  list: 'space-y-2',
  listItem: 'flex items-start gap-2',
  bullet: 'mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-xs',
  tag: 'rounded-full px-3 py-1 text-xs font-medium',
};

export default function HealthDetailPage() {
  const params = useParams();
  const conditionId = params.conditionId as string;
  const [condition, setCondition] = useState<HealthCondition | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    encyclopediaApi.getHealthDetail(conditionId)
      .then(setCondition)
      .finally(() => setIsLoading(false));
  }, [conditionId]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-neutral-50">
        <div className="mx-auto max-w-4xl px-4 py-8">
          <div className="animate-pulse space-y-6">
            <div className="h-8 w-48 rounded-lg bg-neutral-200" />
            <div className="h-48 rounded-3xl bg-neutral-200" />
            <div className="h-4 w-full rounded bg-neutral-200" />
            <div className="h-4 w-3/4 rounded bg-neutral-200" />
          </div>
        </div>
      </div>
    );
  }

  if (!condition) {
    return (
      <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
        <div className="text-center">
          <span className="text-6xl">🔍</span>
          <p className="mt-4 text-lg font-semibold text-neutral-900">病症未找到</p>
          <Link href="/knowledge" className="mt-4 inline-block text-primary-600 hover:text-primary-700">
            返回知识首页
          </Link>
        </div>
      </div>
    );
  }

  const sevColor = severityColors[condition.severity] || severityColors.mild;
  const catConfig = CATEGORY_CONFIG[condition.category] || { label: condition.category, emoji: '📋' };
  const sevConfig = SEVERITY_CONFIG[condition.severity] || { label: '未知', variant: 'safe' };
  const speciesLink = `/knowledge/health?species=${condition.species}`;
  const speciesName = condition.species === 'cat' ? '猫咪' : condition.species === 'dog' ? '狗狗' : '宠物';

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
          <h1 className="truncate text-lg font-bold text-neutral-900">{condition.name}</h1>
        </div>
      </header>

      <div className="mx-auto max-w-4xl px-4 py-6">
        {/* Back link (desktop) */}
        <Link href={speciesLink} className="mb-6 hidden items-center gap-1 text-sm text-neutral-500 hover:text-primary-600 md:inline-flex">
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          返回{speciesName}健康知识
        </Link>

        {/* Hero */}
        <div className={`mb-8 overflow-hidden rounded-3xl border ${sevColor.border} ${sevColor.bg} p-8 shadow-sm`}>
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-white text-3xl shadow-sm">
                {condition.image_emoji || '🏥'}
              </span>
              <div>
                <h2 className="text-2xl font-bold text-neutral-900">{condition.name}</h2>
                <div className="mt-2 flex items-center gap-2">
                  <span className={`rounded-full border px-2.5 py-0.5 text-xs font-medium ${sevColor.text} ${sevColor.border}`}>
                    {sevColor.icon} {sevConfig.label}
                  </span>
                  <span className="rounded-full bg-white px-2.5 py-0.5 text-xs text-neutral-500 shadow-sm">
                    {catConfig.emoji} {catConfig.label}
                  </span>
                </div>
              </div>
            </div>
          </div>
          <p className="mt-4 text-sm leading-relaxed text-neutral-700">{condition.description}</p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          {/* Symptoms */}
          <div className={sectionStyles.container}>
            <h3 className={sectionStyles.title}>
              <svg className="h-5 w-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              常见症状
            </h3>
            <ul className={sectionStyles.list}>
              {condition.symptoms.map((symptom, i) => (
                <li key={i} className={sectionStyles.listItem}>
                  <span className={`${sectionStyles.bullet} bg-primary-100 text-primary-600`}>{i + 1}</span>
                  <span className="text-sm text-neutral-700">{symptom}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Possible Causes */}
          <div className={sectionStyles.container}>
            <h3 className={sectionStyles.title}>
              <svg className="h-5 w-5 text-secondary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              可能病因
            </h3>
            <ul className={sectionStyles.list}>
              {condition.possible_causes.map((cause, i) => (
                <li key={i} className={sectionStyles.listItem}>
                  <span className={`${sectionStyles.bullet} bg-secondary-100 text-secondary-600`}>{i + 1}</span>
                  <span className="text-sm text-neutral-700">{cause}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Urgent Symptoms */}
          {condition.urgent_symptoms.length > 0 && (
            <div className={`${sectionStyles.container} border-primary-200 bg-primary-50/50`}>
              <h3 className={sectionStyles.title}>
                <span className="flex h-6 w-6 items-center justify-center">
                  <svg className="h-5 w-5 text-primary-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </span>
                <span className="text-primary-700">需立即就医的警示症状</span>
              </h3>
              <ul className={sectionStyles.list}>
                {condition.urgent_symptoms.map((symptom, i) => (
                  <li key={i} className={`${sectionStyles.listItem} p-2 rounded-lg bg-white/80`}>
                    <span className="flex h-5 w-5 shrink-0 items-center justify-center text-sm">🚨</span>
                    <span className="text-sm font-medium text-primary-700">{symptom}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Treatment */}
          <div className={sectionStyles.container}>
            <h3 className={sectionStyles.title}>
              <svg className="h-5 w-5 text-success-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              治疗方案
            </h3>
            <ul className={sectionStyles.list}>
              {condition.treatment.map((item, i) => (
                <li key={i} className={sectionStyles.listItem}>
                  <span className={`${sectionStyles.bullet} bg-success-100 text-success-600`}>{i + 1}</span>
                  <span className="text-sm text-neutral-700">{item}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Home Care */}
          <div className={sectionStyles.container}>
            <h3 className={sectionStyles.title}>
              <svg className="h-5 w-5 text-accent-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              日常护理建议
            </h3>
            <ul className={sectionStyles.list}>
              {condition.home_care.map((item, i) => (
                <li key={i} className={sectionStyles.listItem}>
                  <span className={`${sectionStyles.bullet} bg-accent-100 text-accent-600`}>{i + 1}</span>
                  <span className="text-sm text-neutral-700">{item}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Prevention */}
          <div className={sectionStyles.container}>
            <h3 className={sectionStyles.title}>
              <svg className="h-5 w-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              预防措施
            </h3>
            <ul className={sectionStyles.list}>
              {condition.prevention.map((item, i) => (
                <li key={i} className={sectionStyles.listItem}>
                  <span className={`${sectionStyles.bullet} bg-primary-100 text-primary-600`}>{i + 1}</span>
                  <span className="text-sm text-neutral-700">{item}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* External Links */}
          {condition.urgent_symptoms.length > 0 && condition.severity !== 'mild' && (
            <div className="md:col-span-2">
              <Link href="/chat" className="flex items-center justify-center gap-2 rounded-2xl bg-primary-500 p-4 text-white shadow-lg transition-all hover:bg-primary-600 hover:shadow-xl">
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                咨询AI宠物健康助手
              </Link>
            </div>
          )}
        </div>

        {/* Disclaimer */}
        <div className="mt-8 rounded-2xl border border-primary-200 bg-primary-50 p-4 text-sm text-primary-800">
          <p className="font-medium">⚠️ 重要免责声明</p>
          <p className="mt-1">
            以上信息仅供参考，不能替代专业兽医诊断。如果您的宠物出现健康问题，特别是涉及紧急症状时，
            请立即联系执业兽医或前往最近的宠物医院就诊。本平台提供的所有健康内容均不作为医疗建议。
          </p>
        </div>

        <div className="h-20 md:h-0" />
      </div>
    </div>
  );
}
