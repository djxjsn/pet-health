'use client';

import { useState } from 'react';

export interface KnowledgeSource {
  id: string;
  title: string;
  type: 'knowledge' | 'reference' | 'product';
  url?: string;
  relevance?: number;
  summary?: string;
  author?: string;
  date?: string;
}

interface KnowledgeSourceCardProps {
  source: KnowledgeSource;
  compact?: boolean; // Compact mode for inline display
  className?: string;
}

const sourceConfig = {
  knowledge: {
    icon: '📚',
    label: '知识库',
    color: 'blue',
    bgClass: 'bg-blue-50',
    borderClass: 'border-blue-200',
    textClass: 'text-blue-700',
  },
  reference: {
    icon: '📄',
    label: '参考资料',
    color: 'green',
    bgClass: 'bg-green-50',
    borderClass: 'border-green-200',
    textClass: 'text-green-700',
  },
  product: {
    icon: '🛒',
    label: '推荐商品',
    color: 'orange',
    bgClass: 'bg-orange-50',
    borderClass: 'border-orange-200',
    textClass: 'text-orange-700',
  },
};

export default function KnowledgeSourceCard({
  source,
  compact = false,
  className = '',
}: KnowledgeSourceCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const config = sourceConfig[source.type];

  if (compact) {
    return (
      <span
        className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${config.bgClass} ${config.textClass} ${className}`}
        title={source.title}
      >
        <span>{config.icon}</span>
        <span className="truncate max-w-[150px]">{source.title}</span>
        {source.relevance && (
          <span className="opacity-60">{Math.round(source.relevance * 100)}%</span>
        )}
      </span>
    );
  }

  return (
    <div
      className={`
        group rounded-xl border transition-all duration-200
        hover:shadow-md
        ${config.borderClass}
        ${isExpanded ? 'bg-white shadow-md' : config.bgClass}
        ${className}
      `}
    >
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex w-full items-start gap-3 p-3 text-left"
      >
        {/* Icon */}
        <div className={`mt-0.5 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg ${config.bgClass}`}>
          <span className="text-lg">{config.icon}</span>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h4 className="font-medium text-gray-900 truncate text-sm">
              {source.title}
            </h4>
            {/* Expand/Collapse indicator */}
            <svg
              className={`h-4 w-4 flex-shrink-0 text-gray-400 transition-transform duration-200 ${
                isExpanded ? 'rotate-90' : ''
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </div>

          {/* Meta info */}
          <div className="mt-1 flex items-center gap-3 text-xs text-gray-500">
            <span className={`${config.textClass} font-medium`}>{config.label}</span>
            
            {source.relevance && (
              <span className="flex items-center gap-1">
                <span className="h-1.5 w-1.5 rounded-full bg-green-400" />
                相关度 {(source.relevance * 100).toFixed(0)}%
              </span>
            )}

            {source.author && (
              <span>作者：{source.author}</span>
            )}

            {source.date && (
              <span>{source.date}</span>
            )}
          </div>

          {/* Summary (when expanded) */}
          {isExpanded && source.summary && (
            <p className="mt-2 text-sm leading-relaxed text-gray-600">
              {source.summary}
            </p>
          )}
        </div>

        {/* Action (if URL exists) */}
        {source.url && isExpanded && (
          <a
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-2 ml-auto flex-shrink-0 rounded-lg px-3 py-1.5 text-xs font-medium text-primary-600 hover:bg-primary-50 transition-colors"
            onClick={(e) => e.stopPropagation()}
          >
            查看原文 →
          </a>
        )}
      </button>

      {/* Expanded content area */}
      {isExpanded && !source.summary && (
        <div className="px-4 pb-3 pt-0">
          <div className="rounded-lg bg-gray-50 p-3 text-sm text-gray-500">
            <p>暂无详细摘要</p>
          </div>
        </div>
      )}
    </div>
  );
}

// Multiple sources container
interface KnowledgeSourcesListProps {
  sources: KnowledgeSource[];
  maxVisible?: number;
  showMoreLabel?: string;
  className?: string;
}

export function KnowledgeSourcesList({
  sources,
  maxVisible = 3,
  showMoreLabel = '查看全部来源',
  className = '',
}: KnowledgeSourcesListProps) {
  const [showAll, setShowAll] = useState(false);
  const visibleSources = showAll ? sources : sources.slice(0, maxVisible);

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="space-y-2">
        {visibleSources.map((source) => (
          <KnowledgeSourceCard key={source.id} source={source} />
        ))}
      </div>

      {/* Show more button */}
      {sources.length > maxVisible && (
        <button
          onClick={() => setShowAll(!showAll)}
          className="w-full rounded-lg border border-dashed border-gray-300 py-2.5 text-sm font-medium text-gray-500 hover:border-gray-400 hover:text-gray-700 hover:bg-gray-50 transition-colors"
        >
          {showAll ? `收起 (${sources.length})` : `${showMoreLabel} (+${sources.length - maxVisible})`}
        </button>
      )}
    </div>
  );
}
