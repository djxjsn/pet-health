# AI 宠物健康助手 - 前端项目

基于 Next.js 14 + TypeScript 开发的前端应用。

## 技术栈

- **框架**: Next.js 14 (App Router)
- **语言**: TypeScript 5
- **样式**: Tailwind CSS + PostCSS
- **代码质量**: ESLint + Prettier
- **包管理**: npm

## 项目结构

```
frontend/
├── src/
│   ├── app/              # Next.js App Router 页面
│   │   ├── api/          # API 路由
│   │   ├── globals.css   # 全局样式
│   │   ├── layout.tsx    # 根布局
│   │   └── page.tsx      # 首页
│   ├── components/       # React 组件
│   ├── hooks/           # 自定义 Hooks
│   ├── styles/          # 样式文件
│   ├── types/           # TypeScript 类型定义
│   └── utils/           # 工具函数
├── public/              # 静态资源
├── .env.local           # 环境变量
├── next.config.js       # Next.js 配置
├── tailwind.config.js   # Tailwind 配置
├── tsconfig.json        # TypeScript 配置
└── package.json         # 项目依赖
```

## 快速开始

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问 [http://localhost:3000](http://localhost:3000) 查看应用。

### 构建生产版本

```bash
npm run build
```

### 启动生产服务器

```bash
npm start
```

### 代码检查

```bash
# ESLint 检查
npm run lint

# Prettier 格式化
npm run format
```

## 可用脚本

| 命令 | 说明 |
|------|------|
| `npm run dev` | 启动开发服务器 |
| `npm run build` | 构建生产版本 |
| `npm run start` | 启动生产服务器 |
| `npm run lint` | ESLint 代码检查 |
| `npm run format` | Prettier 代码格式化 |

## 代码规范

### ESLint 规则

- 使用 `no-unused-vars` 警告未使用的变量（下划线开头的参数除外）
- 允许使用 `console.warn` 和 `console.error`
- 推荐使用 `const` 而非 `let`
- 强制使用分号

### Prettier 配置

- 单引号
- 行尾逗号 (ES5)
- 最大行宽 100 字符
- 2 空格缩进
- 始终在箭头函数参数周围使用括号

## 环境变量

在 `.env.local` 文件中配置：

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_NAME=AI 宠物健康助手
NEXT_PUBLIC_APP_VERSION=1.0.0
```

## 开发指南

### 创建新页面

在 `src/app` 目录下创建新的路由：

```typescript
// src/app/about/page.tsx
export default function AboutPage() {
  return (
    <div>
      <h1>关于我们</h1>
    </div>
  );
}
```

### 创建组件

在 `src/components` 目录下创建可复用组件：

```typescript
// src/components/Button.tsx
interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary';
}

export default function Button({ children, onClick, variant = 'primary' }: ButtonProps) {
  return (
    <button className={`btn-${variant}`} onClick={onClick}>
      {children}
    </button>
  );
}
```

### 使用自定义 Hook

```typescript
import { useLocalStorage } from '@/hooks';

export default function UserProfile() {
  const [theme, setTheme] = useLocalStorage('theme', 'light');
  
  return <div>当前主题：{theme}</div>;
}
```

## 项目进度

- ✅ 项目初始化完成
- ✅ TypeScript 配置完成
- ✅ ESLint + Prettier 集成完成
- ✅ Tailwind CSS 配置完成
- ✅ 项目目录结构创建完成
- ✅ 基础类型定义完成
- ✅ 工具函数和 Hooks 创建完成
- ⏳ 页面组件开发中

## 下一步计划

1. 实现登录/注册页面
2. 实现首页/对话页面
3. 实现宠物档案管理页面
4. 集成后端 API
5. 实现响应式布局

## 相关文档

- [UI 设计文档](../animal/docs/UI-Design.md)
- [API 接口文档](../animal/docs/API 接口文档.md)
- [产品需求文档](../animal/docs/PRD.md)

## 许可证

ISC
