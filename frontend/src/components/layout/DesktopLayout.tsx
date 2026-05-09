'use client';

import { useState, useCallback, ReactNode, useRef, useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';

interface ConversationItem {
  id: string;
  title: string;
  preview?: string;
  updatedAt: string;
}

const mockConversations: ConversationItem[] = [
  { id: 'conv-001', title: '猫咪软便', preview: '我的猫今天软便了...', updatedAt: '1小时前' },
  { id: 'conv-002', title: '狗粮推荐', preview: '金毛犬适合的狗粮...', updatedAt: '昨天' },
];

interface DesktopLayoutProps {
  children: ReactNode;
  sidebar?: ReactNode;
  rightPanel?: ReactNode;
  header?: ReactNode;
  className?: string;
}

export default function DesktopLayout({
  children,
  sidebar,
  rightPanel,
  header,
  className = '',
}: DesktopLayoutProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [rightPanelVisible, setRightPanelVisible] = useState(true);
  const [historyExpanded, setHistoryExpanded] = useState(false);
  const pathname = usePathname();
  const router = useRouter();
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setHistoryExpanded(false);
      }
    };

    if (historyExpanded) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [historyExpanded]);

  // Sidebar navigation items
  const navItems = [
    { icon: '💬', label: '对话', href: '/chat', id: 'chat' },
    { icon: '📜', label: '历史记录', href: '/history', id: 'history' },
    { icon: '🐾', label: '宠物档案', href: '/pets', id: 'pets' },
    { icon: '📖', label: '知识百科', href: '/knowledge', id: 'knowledge' },
    { icon: '🛒', label: '智能商城', href: '/shop', id: 'shop' },
    { icon: '⚙️', label: '健康咨询', href: '/health/consult', id: 'health' },
    { icon: '🎯', label: '行为分析', href: '/behavior', id: 'behavior' },
  ];

  const handleNavClick = useCallback((href: string) => {
    router.push(href);
  }, [router]);

  return (
    <div className={`flex h-screen overflow-hidden bg-gray-50 ${className}`}>
      {/* Left Sidebar */}
      <aside
        className={`
          flex h-full flex-col border-r bg-white transition-all duration-300 ease-in-out
          ${sidebarCollapsed ? 'w-[68px]' : 'w-[240px]'}
        `}
      >
        {/* Logo Area */}
        <div className="relative flex h-16 flex-shrink-0 items-center gap-2 border-b px-4">
          <span className="text-xl">🐾</span>
          {!sidebarCollapsed && (
            <span className="font-bold text-gray-900">宠物健康</span>
          )}

          {/* Collapse Button - inside sidebar header when expanded */}
          {!sidebarCollapsed && (
            <button
              onClick={() => setSidebarCollapsed(true)}
              className="absolute right-2 top-1/2 flex h-7 w-7 -translate-y-1/2 items-center justify-center rounded-md border border-gray-200 bg-white text-gray-400 shadow-sm transition-all duration-200 ease-in-out hover:border-gray-300 hover:bg-gray-50 hover:text-gray-600"
              title="收起侧栏"
            >
              <svg
                className="h-3.5 w-3.5 rotate-180"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                strokeWidth={2.5}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4 px-3">
          <ul className="space-y-1">
            {navItems.filter(item => item.id !== 'history').map((item) => {
              const isActive = pathname === item.href || 
                (item.href !== '/' && pathname.startsWith(item.href));
              
              return (
                <li key={item.id}>
                  {item.id === 'chat' && !sidebarCollapsed ? (
                    <div ref={dropdownRef} className="relative">
                      <button
                        onClick={() => {
                          handleNavClick(item.href);
                          setHistoryExpanded(!historyExpanded);
                        }}
                        className={`
                          group relative flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200
                          ${isActive
                            ? 'bg-primary-50 text-primary-700 shadow-sm'
                            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                          }
                        `}
                      >
                        {/* Active indicator */}
                        {isActive && (
                          <span className="absolute left-0 top-1/2 h-6 w-1 -translate-y-1/2 rounded-r-full bg-primary-500" />
                        )}
                        
                        <span className={`text-lg transition-transform duration-200 ${isActive ? 'scale-110' : ''} group-hover:scale-110`}>
                          {item.icon}
                        </span>
                        
                        <span className="truncate">{item.label}</span>
                        
                        {/* Expand indicator */}
                        <svg
                          className={`ml-auto h-3.5 w-3.5 transition-transform duration-200 ${historyExpanded ? 'rotate-180' : ''}`}
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>

                      {/* History Dropdown */}
                      <div
                        className={`
                          overflow-hidden transition-all duration-300 ease-in-out
                          ${historyExpanded ? 'max-h-96 opacity-100 mt-2' : 'max-h-0 opacity-0'}
                        `}
                      >
                        <div className="rounded-lg border border-gray-200 bg-gray-50 p-2">
                          <div className="px-2 pb-2 text-xs font-semibold uppercase tracking-wider text-gray-400">
                            对话历史
                          </div>
                          <div className="space-y-1">
                            {mockConversations.map((conv) => (
                              <button
                                key={conv.id}
                                onClick={() => {
                                  router.push('/chat');
                                  setHistoryExpanded(false);
                                }}
                                className="group w-full rounded-md p-2 text-left text-sm text-gray-600 hover:bg-white hover:shadow-sm transition-all"
                              >
                                <div className="truncate font-medium text-gray-900">{conv.title}</div>
                                {conv.preview && (
                                  <div className="mt-0.5 truncate text-xs text-gray-400">{conv.preview}</div>
                                )}
                              </button>
                            ))}
                          </div>
                          <button
                            onClick={() => router.push('/history')}
                            className="mt-2 w-full rounded-md py-1.5 text-xs font-medium text-primary-600 hover:bg-primary-50 transition-colors"
                          >
                            查看全部历史 →
                          </button>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={() => handleNavClick(item.href)}
                      className={`
                        group relative flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200
                        ${isActive
                          ? 'bg-primary-50 text-primary-700 shadow-sm'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                        }
                      `}
                    >
                      {/* Active indicator */}
                      {isActive && (
                        <span className="absolute left-0 top-1/2 h-6 w-1 -translate-y-1/2 rounded-r-full bg-primary-500" />
                      )}
                      
                      <span className={`text-lg transition-transform duration-200 ${isActive ? 'scale-110' : ''} group-hover:scale-110`}>
                        {item.icon}
                      </span>
                      
                      {!sidebarCollapsed && (
                        <>
                          <span className="truncate">{item.label}</span>
                          
                          {/* Keyboard shortcut hint */}
                          <span className="ml-auto text-xs opacity-40 group-hover:opacity-60">
                            {item.id === 'chat' && '⌘K'}
                            {item.id === 'pets' && '⌘P'}
                            {item.id === 'shop' && '⌘S'}
                          </span>
                        </>
                      )}

                      {sidebarCollapsed && (
                        <div className="absolute left-full ml-2 hidden rounded-md bg-gray-900 px-2 py-1 text-xs text-white opacity-0 group-hover:block group-hover:opacity-100 transition-opacity whitespace-nowrap z-50">
                          {item.label}
                        </div>
                      )}
                    </button>
                  )}
                </li>
              );
            })}
          </ul>

          {!sidebarCollapsed && (
            <div className="mt-6 pt-4 border-t">
              <p className="px-3 mb-2 text-xs font-semibold uppercase tracking-wider text-gray-400">
                快捷操作
              </p>
              <ul className="space-y-1">
                <li>
                  <button
                    onClick={() => router.push('/pets/new')}
                    className="group flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors"
                  >
                    <span className="text-base">➕</span>
                    {!sidebarCollapsed && <span>添加宠物</span>}
                  </button>
                </li>
                <li>
                  <button
                    onClick={() => router.push('/settings')}
                    className="group flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors"
                  >
                    <span className="text-base">⚙️</span>
                    {!sidebarCollapsed && <span>设置</span>}
                  </button>
                </li>
              </ul>
            </div>
          )}
        </nav>

        {/* User Info at Bottom */}
        <div className="border-t p-3">
          <div className={`flex items-center gap-3 ${sidebarCollapsed ? 'justify-center' : ''}`}>
            <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-primary-400 to-primary-600 text-sm font-bold text-white">
              U
            </div>
            
            {!sidebarCollapsed && (
              <div className="flex-1 min-w-0">
                <p className="truncate text-sm font-medium text-gray-700">用户名</p>
                <p className="truncate text-xs text-gray-400">user@email.com</p>
              </div>
            )}

            {!sidebarCollapsed && (
              <button
                onClick={() => router.push('/profile')}
                className="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
              >
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c-.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex min-w-0 flex-col overflow-hidden">
        {/* Top Header Bar */}
        {header || (
          <header className="flex h-14 flex-shrink-0 items-center justify-between border-b bg-white px-4 md:px-6">
            {/* Breadcrumb / Page Title */}
            <div className="flex items-center gap-3">
              {/* Sidebar toggle button - shows in main content when sidebar is collapsed */}
              {sidebarCollapsed && (
                <button
                  onClick={() => setSidebarCollapsed(false)}
                  className="flex h-7 w-7 items-center justify-center rounded-md border border-gray-200 bg-white text-gray-400 shadow-sm transition-all duration-200 ease-in-out hover:border-gray-300 hover:bg-gray-50 hover:text-gray-600"
                  title="展开侧栏"
                >
                  <svg
                    className="h-3.5 w-3.5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    strokeWidth={2.5}
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
              )}
              <h1 className="text-lg font-semibold text-gray-900">
                {navItems.find(item => item.href === pathname)?.label || '页面'}
              </h1>
            </div>

            {/* Right Actions */}
            <div className="flex items-center gap-2">
              {/* Search */}
              <button className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors">
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>

              {/* Notifications */}
              <button className="relative rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors">
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v6.159A2.032 2.032 0 0112 14.158V17M5 17h14m-3-3v3m-3 0H8" />
                </svg>
                <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-red-500" />
              </button>

              {/* Theme Toggle - import from ThemeProvider */}
              {/* Add theme toggle here if needed */}
            </div>
          </header>
        )}

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto">
          {children}
        </div>
      </main>

      {/* Right Panel (Optional) */}
      {rightPanel && rightPanelVisible && (
        <aside className="hidden xl:flex w-[320px] flex-shrink-0 flex-col border-l bg-white overflow-hidden">
          {/* Right Panel Header */}
          <div className="flex h-12 flex-shrink-0 items-center justify-between border-b px-4">
            <h2 className="font-semibold text-gray-900">信息面板</h2>
            <button
              onClick={() => setRightPanelVisible(false)}
              className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Right Panel Content */}
          <div className="flex-1 overflow-y-auto p-4">
            {rightPanel}
          </div>
        </aside>
      )}

      {/* Show right panel button when hidden */}
      {rightPanel && !rightPanelVisible && (
        <button
          onClick={() => setRightPanelVisible(true)}
          className="fixed right-4 bottom-20 z-40 rounded-full bg-primary-600 p-3 text-white shadow-lg hover:bg-primary-700 transition-all hover:scale-105"
          title="显示信息面板"
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
        </button>
      )}
    </div>
  );
}
