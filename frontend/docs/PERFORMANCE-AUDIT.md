# 前端性能审计与优化报告

**项目**: AI 宠物健康助手前端
**审计日期**: 2026-04-15
**审计范围**: 代码级静态分析 + Next.js/React 最佳实践审查

---

## 一、当前架构性能评估

### 1.1 技术栈基础评分

| 维度 | 评级 | 说明 |
|------|------|------|
| **框架选择** | ⭐⭐⭐⭐⭐ | Next.js 14 App Router + React 18，SSR/SSG 支持 |
| **状态管理** | ⭐⭐⭐⭐⭐ | Zustand 轻量无冗余渲染，persist 按需持久化 |
| **样式方案** | ⭐⭐⭐⭐⭐ | Tailwind CSS JIT，生产环境自动 purge |
| **TypeScript** | ⭐⭐⭐⭐⭐ | 全量类型覆盖，strict 模式 |
| **构建工具** | ⭐⭐⭐⭐ | Turbopack（dev）+ webpack（build） |

### 1.2 预估核心指标

| 指标 | 预估值 | 目标值 | 状态 |
|------|--------|--------|------|
| First Contentful Paint (FCP) | ~1.2s | < 1.8s | ✅ 良好 |
| Largest Contentful Paint (LCP) | ~2.0s | < 2.5s | ⚠️ 可优化 |
| Time to Interactive (TTI) | ~2.5s | < 3.8s | ✅ 良好 |
| Cumulative Layout Shift (CLS) | < 0.05 | < 0.1 | ✅ 良好 |
| Total Bundle Size (gzipped) | ~120KB | < 150KB | ✅ 良好 |

---

## 二、已实现的性能优化

### 2.1 架构层面

```
✅ 已优化项:
├── App Router (Server Components) — 首屏 HTML 由服务端渲染
├── Zustand (非 Redux) — 减少 ~80% 样板代码和运行时开销
├── Tailwind CSS JIT — 仅生成使用到的 CSS 类
├── next/image — 自动图片优化（WebP/AVIF + 响应式）
├── next/font — 字体优化（Inter 子集化 + display: swap）
└── Code Splitting — App Router 自动按路由拆分 JS
```

### 2.2 组件层面

- **骨架屏**: PageLoading 组件提供 4 种页面形态的加载占位
- **懒加载**: 对话气泡、商品卡片等列表组件可进一步使用 `dynamic()`
- **防抖**: utils/debounce 工具函数已就绪
- **虚拟滚动**: 大型列表（历史记录 >100 条）待实现

---

## 三、优化建议（按优先级排序）

### P0 — 立即实施（高影响 / 低成本）

#### 3.1 图片懒加载与优化

**现状**: ImageUploader 组件上传预览未使用 `next/image`
**方案**:
```tsx
// 替换原生 <img> 为 next/image
import Image from 'next/image';

<Image
  src={previewUrl}
  alt="预览"
  width={200}
  height={200}
  className="rounded-lg object-cover"
  placeholder="blur"
  blurDataURL="data:image/jpeg;base64,..." // 极小模糊占位
/>
```
**预期收益**: LCP 降低 15~30%，带宽节省 40~60%

#### 3.2 动态导入重型组件

**现状**: DesktopLayout、KnowledgeSourceCard 等在首屏可能不需要立即加载
**方案**:
```tsx
// 使用 next/dynamic 懒加载
const DesktopLayout = dynamic(
  () => import('@/components/layout/DesktopLayout'),
  { ssr: false, loading: () => <PageSkeleton /> }
);

const KnowledgeSourceCard = dynamic(
  () => import('@/components/chat/KnowledgeSourceCard'),
  { ssr: false }
);
```
**预期收益**: 首屏 JS 减少 20~35KB (gzipped)

#### 3.3 字体显示优化

**现状**: Inter 字体已配置但未添加 `font-display: swap` fallback
**确认**: `next/font/google` 默认已处理，✅ 无需额外操作

---

### P1 — 短期实施（中影响 / 中成本）

#### 3.4 React.memo 包裹纯展示组件

**适用组件**: MessageBubble、PetSwitcher、Spinner
```tsx
export const MessageBubble = React.memo(function MessageBubble({ ... }) {
  // ...
});
```
**预期收益**: 减少不必要的重渲染，尤其聊天消息列表

#### 3.5 useMemo/useCallback 优化

**目标文件**:
- `useTypewriter.tsx`: 缓存打字机计算结果
- `DesktopLayout.tsx`: 缓存导航菜单数据
- `Toaster.tsx`: 缓存 ICON_MAP 查找结果

```tsx
// 示例：Toaster 中缓存图标查找
const icon = useMemo(() => ICON_MAP[t.type], [t.type]);
```

#### 3.6 列表虚拟化（长列表场景）

**适用页面**: 历史记录页 (>100 条对话)、商城页 (>50 个商品)
**推荐库**: `@tanstack/react-virtual` (~3KB)
```tsx
import { useVirtualizer } from '@tanstack/react-virtual';

const virtualizer = useVirtualizer({
  count: conversations.length,
  getScrollElement: () => scrollRef.current,
  estimateSize: () => 80,
});
```
**预期收益**: 100 条列表 DOM 节点从 100 → ~12（视口内），内存降低 80%+

---

### P2 — 中期规划（高影响 / 高成本）

#### 3.7 Service Worker + 缓存策略

**方案**: 使用 `next-pwa` 或手动注册 SW
```typescript
// public/sw.js — 缓存策略
const CACHE_NAME = 'pet-health-v1';
const STATIC_ASSETS = ['/', '/offline.html'];

self.addEventListener('fetch', (event) => {
  // Network-first for API, Cache-first for static
});
```
**预期收益**: 二次访问 FCP < 500ms，离线可用

#### 3.8 Bundle 分析与 Tree Shaking

**操作步骤**:
1. 运行 `npm run build` 查看 bundle 分析
2. 识别大体积依赖（如 moment.js → date-fns）
3. 配置 `optimizePackageImports` in next.config
```javascript
// next.config.js
module.exports = {
  experimental: {
    optimizePackageImports: ['lucide-react', 'date-fns'],
  },
};
```

#### 3.9 ISR (增量静态再生) 适用页面

**适用页面**:
- `/shop` — 商品列表（每小时再生）
- `/pets/[id]` — 宠物详情（宠物信息变更时再生）
```tsx
// app/shop/page.tsx
export const revalidate = 3600; // 1 小时
```

---

## 四、性能监控方案

### 4.1 推荐集成

```typescript
// lib/analytics.ts — 性能数据采集
export function reportWebVitals(metric: Metric) {
  const body = JSON.stringify({
    name: metric.name,
    value: metric.value,
    rating: metric.rating,
    path: window.location.pathname,
  });

  if ('sendBeacon' in navigator) {
    navigator.sendBeacon('/api/vitals', body);
  }
}
```

### 4.2 Core Web Vitals 监控指标

| 指标 | 好阈值 | 需改进 | 差 |
|------|--------|--------|-----|
| LCP | ≤ 2.5s | 2.5s ~ 4.0s | > 4.0s |
| FID | ≤ 100ms | 100ms ~ 300ms | > 300ms |
| CLS | ≤ 0.1 | 0.1 ~ 0.25 | > 0.25 |
| INP | ≤ 200ms | 200ms ~ 500ms | > 500ms |

---

## 五、SEO 与可访问性检查

### 5.1 SEO 当前状态

| 检查项 | 状态 | 说明 |
|--------|------|------|
| Meta Title | ✅ | 已设置 "AI 宠物健康助手" |
| Meta Description | ✅ | 已设置项目描述 |
| Open Graph 标签 | ❌ 待补充 | 社交分享卡片 |
| Structured Data | ❌ 待补充 | JSON-LD 组织/应用标记 |
| Sitemap | ❌ 待生成 | `next-sitemap` |
| Robots.txt | ❌ 待创建 | 搜索引擎爬取规则 |

### 5.2 可访问性 (a11y) 当前状态

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 语义化 HTML | ✅ | nav/main/header/footer 正确使用 |
| ARIA 标签 | ✅ | Spinner 有 role/status，Toast 有 role/alert |
| 键盘导航 | ⚠️ 部分 | 底部导航需验证 Tab 顺序 |
| 颜色对比度 | ✅ | Tailwind 主色调符合 WCAG AA |
| Focus 可见性 | ✅ | ring 样式已全局配置 |
| 屏幕阅读器 | ⚠️ 待验证 | 需实际测试 VoiceOver/NVDA |

---

## 六、执行路线图

```
Week 1 (P0):
├── [ ] next/image 替换所有 <img>
├── [ ] dynamic() 导入 DesktopLayout/KnowledgeSourceCard
└── [ ] next.config.js optimizePackageImports 配置

Week 2 (P1):
├── [ ] React.memo 包裹 5 个纯展示组件
├── [ ] useMemo/useCallback 优化热点 Hook
└── [ ] @tanstack/react-virtual 集成到 History 页面

Week 3-4 (P2):
├── [ ] Service Worker + 离线页面
├── [ ] next-pwa 集成
├── [ ] OG 标签 + JSON-LD 结构化数据
└── [ ] next-sitemap 自动生成
```

---

*报告生成时间: 2026-04-15*
*下次审计建议: P0 实施完成后重新跑 Lighthouse*
