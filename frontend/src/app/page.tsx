'use client';

import { useState } from 'react';
import AuthModal from '@/components/auth/AuthModal';

export default function Home() {
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');

  const handleOpenRegister = () => {
    setAuthMode('register');
    setIsAuthModalOpen(true);
  };

  const capabilities = [
    {
      icon: (
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      ),
      title: 'AI 智能问诊引擎',
      description: '基于 LangChain ReAct Agent 架构，集成 RAG 知识增强检索，支持多轮对话与上下文感知，覆盖症状分诊、健康建议、紧急预警等场景。已对接 5 大知识库（营养/疾病/急救/用药/行为），实现精准诊断。',
      status: '已上线',
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
      ),
      title: '宠物档案与健康追踪',
      description: '支持多宠物种（犬/猫/兔/鸟等）档案管理，记录疫苗接种、体重变化、医疗历史。通过 WebSocket 实现对话流式响应，所有咨询记录持久化至 MongoDB，支持历史回溯。',
      status: '已上线',
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      title: '行为分析与智能购物',
      description: '基于品种特性与行为知识库，识别异常行为模式并提供训练建议。智能购物模块支持商品成分分析、多商品对比报告、AI 推荐引擎，帮宠物主做出科学消费决策。',
      status: '已上线',
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      title: '实时数据安全保障',
      description: '企业级安全体系：AES-256 敏感数据加密、RBAC 角色权限控制、审计日志全量记录、JWT 令牌管理、API 限流与异常检测。数据在传输和存储中均受保护。',
      status: '已上线',
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
      ),
      title: '可穿戴设备健康监控',
      description: '支持智能项圈/定位牌等 IoT 设备数据接入，基于 InfluxDB 时序数据库存储心率、步数、体温、活动量等 6 项健康指标。内置数据模拟器，POC 阶段即可跑通全链路。日报引擎支持模板化 + LLM 双模式生成。',
      status: 'POC 验证中',
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      ),
      title: '扩展工具生态',
      description: '集成 MinIO 对象存储（文件/图片管理）、BaiduAI 图像识别（多模态分析）、Tavily 联网搜索（实时信息）、Celery 异步任务队列（耗时操作后台处理）、Redis 缓存与分布式锁。',
      status: '已上线',
    },
  ];

  const moduleStats = [
    { value: '12', label: '功能模块' },
    { value: '70+', label: 'API 端点' },
    { value: '5', label: '知识库分类' },
    { value: '6', label: '健康监测指标' },
  ];

  return (
    <div className="min-h-screen bg-white">
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        initialMode={authMode}
      />

      {/* ===== Hero: 目标 + 做了什么 + 解决什么 ===== */}
      <header className="relative bg-gradient-to-br from-primary-500 via-primary-600 to-accent-600 text-white overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4xIj48Y2lyY2xlIGN4PSIzMCIgY3k9IjMwIiByPSI0Ii8+PC9nPjwvZz48L3N2Zz4=')] opacity-20" />

        <nav className="relative container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white/20 backdrop-blur rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
              </div>
              <span className="text-xl font-bold">AI宠物健康助手</span>
            </div>
          </div>
        </nav>

        <div className="relative container mx-auto px-4 py-16 md:py-20">
          <div className="max-w-3xl mx-auto text-center">
            {/* 目标 */}
            <div className="inline-flex items-center gap-2 bg-white/15 backdrop-blur rounded-full px-4 py-1.5 text-sm text-white/90 mb-6">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              目标：让每只宠物都拥有 AI 驱动的全天候健康守护
            </div>

            <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6 leading-tight text-white">
              从智能问诊到设备监控，
              <span className="text-secondary-300">一站式宠物健康平台</span>
            </h1>

            {/* 核心三问 */}
            <div className="grid md:grid-cols-3 gap-4 mt-8 mb-8 max-w-3xl mx-auto">
              <div className="bg-white/10 backdrop-blur rounded-xl p-4 text-left">
                <div className="text-secondary-300 text-xs font-semibold mb-1 uppercase tracking-wider">核心问题</div>
                <p className="text-white/90 text-sm leading-relaxed">
                  宠物主面对生病、行为异常、选品决策时缺乏专业指导，IoT 设备数据孤立、未形成健康闭环
                </p>
              </div>
              <div className="bg-white/10 backdrop-blur rounded-xl p-4 text-left">
                <div className="text-secondary-300 text-xs font-semibold mb-1 uppercase tracking-wider">已实现</div>
                <p className="text-white/90 text-sm leading-relaxed">
                  12 个功能模块 + 70+ API，覆盖问诊/行为/购物/科普/安全，新接入设备健康监控全链路
                </p>
              </div>
              <div className="bg-white/10 backdrop-blur rounded-xl p-4 text-left">
                <div className="text-secondary-300 text-xs font-semibold mb-1 uppercase tracking-wider">下一阶段</div>
                <p className="text-white/90 text-sm leading-relaxed">
                  设备数据可视化、WebSocket 实时推送、多设备对比、LLM 增强日报、PDF 导出
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* 模块统计 */}
        <div className="relative container mx-auto px-4 pb-16">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
            {moduleStats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl md:text-4xl font-bold mb-1 text-white">{stat.value}</div>
                <div className="text-white/70 text-sm">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </header>

      {/* ===== 已完成的核心能力 ===== */}
      <section className="py-16 md:py-20 bg-neutral-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-14">
            <div className="inline-flex items-center gap-2 bg-green-100 text-green-700 rounded-full px-4 py-1 text-sm font-medium mb-4">
              <span className="w-2 h-2 bg-green-500 rounded-full" />
              12 个模块中 11 个已上线，1 个 POC 验证中
            </div>
            <h2 className="text-3xl md:text-4xl font-bold text-neutral-900 mb-4">
              已完成的核心能力
            </h2>
            <p className="text-lg text-neutral-600 max-w-2xl mx-auto">
              基于 LangChain + FastAPI + Next.js 全栈架构，构建覆盖宠物全生命周期健康管理的 AI 系统
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
            {capabilities.map((cap, index) => (
              <div
                key={index}
                className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-1 border border-neutral-100 flex flex-col"
              >
                <div className="w-12 h-12 bg-gradient-to-br from-accent-400 to-accent-500 rounded-xl flex items-center justify-center text-white mb-4">
                  {cap.icon}
                </div>
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="text-lg font-semibold text-neutral-900">{cap.title}</h3>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                    cap.status === '已上线'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-yellow-100 text-yellow-700'
                  }`}>
                    {cap.status}
                  </span>
                </div>
                <p className="text-neutral-600 text-sm leading-relaxed flex-1">{cap.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== 技术架构亮点 ===== */}
      <section className="py-16 md:py-20 bg-white">
        <div className="container mx-auto px-4 max-w-5xl">
          <div className="text-center mb-12">
            <h2 className="text-2xl md:text-3xl font-bold text-neutral-900 mb-3">技术架构概览</h2>
            <p className="text-neutral-600">Agent+RAG+MCP 架构，端到端设计落地</p>
          </div>

          <div className="grid md:grid-cols-4 gap-4">
            {[
              { layer: '前端', tech: 'Next.js 14 + Zustand + Tailwind CSS', desc: 'App Router / 流式WebSocket / 响应式设计' },
              { layer: 'API', tech: 'FastAPI v0.100+ / Uvicorn', desc: 'RESTful / WebSocket / JWT鉴权 / CORS' },
              { layer: 'Agent', tech: 'LangChain v1.0 + LangGraph', desc: 'ReAct推理 / 6个业务Tool / 上下文记忆' },
              { layer: '数据', tech: 'MySQL + MongoDB + InfluxDB + Qdrant', desc: '混合存储 / 时序数据 / 向量检索' },
            ].map((item, i) => (
              <div key={i} className="bg-neutral-50 rounded-xl p-5 border border-neutral-100">
                <div className="text-xs font-bold text-primary-600 uppercase mb-2">{item.layer}层</div>
                <div className="text-sm font-semibold text-neutral-900 mb-1">{item.tech}</div>
                <div className="text-xs text-neutral-500">{item.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== 下一阶段路线图 ===== */}
      <section className="py-16 md:py-20 bg-gradient-to-br from-accent-500 to-accent-600 text-white">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 text-white">下一阶段要做什么</h2>
            <p className="text-lg text-white/80">
              Phase 1 MVP 开发 (3周)，在 POC 基础上迈向可交付产品
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 max-w-4xl mx-auto">
            {[
              { step: '01', title: '数据可视化', desc: '集成 ECharts 实现健康指标时序图表，支持心率/体温/步数趋势对比' },
              { step: '02', title: 'WebSocket 实时推送', desc: '设备数据实时流式传输至前端，关键指标变化即时展示' },
              { step: '03', title: 'LLM 增强日报', desc: '对接 DeepSeek 模型，由 LLM 生成个性化自然语言健康报告' },
              { step: '04', title: '预警规则引擎', desc: '阈值触发 + 趋势检测，异常事件自动推送通知' },
            ].map((item, i) => (
              <div key={i} className="bg-white/10 backdrop-blur rounded-xl p-5 text-left">
                <div className="text-secondary-300 text-xl font-bold mb-2">{item.step}</div>
                <h3 className="font-semibold text-white mb-1">{item.title}</h3>
                <p className="text-white/70 text-sm leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>

          <div className="text-center mt-10">
            <p className="text-white/60 text-sm mb-6">
              后续规划：Phase 2 周/月/年报 + PDF导出 + 推送通知 → Phase 3 小米IoT/华为Health平台对接 → B端合作
            </p>
            <button
              onClick={handleOpenRegister}
              className="inline-flex items-center gap-2 bg-white text-accent-600 px-10 py-4 rounded-full text-lg font-semibold hover:bg-secondary-300 hover:text-accent-700 transition-all shadow-xl hover:shadow-2xl transform hover:scale-105"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              参与 POC 验证，体验设备健康监控
            </button>
          </div>
        </div>
      </section>

      <footer className="bg-neutral-900 text-white py-10">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
              </div>
              <span className="text-lg font-semibold">AI宠物健康助手</span>
            </div>
            <div className="flex gap-6 text-neutral-400 text-sm">
              <span>Agent + RAG + MCP 架构</span>
              <span className="hidden sm:inline">|</span>
              <span>LangChain + FastAPI + Next.js</span>
              <span className="hidden sm:inline">|</span>
              <span>&copy; 2026</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}