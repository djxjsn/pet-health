'use client';

import { useState, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface UserProfile {
  nickname: string;
  email: string;
  avatar: string;
  phone?: string;
}

interface PetSummary {
  pet_id: string;
  name: string;
  species: string;
  avatar_url?: string;
}

const mockUser: UserProfile = {
  nickname: '宠物爱好者',
  email: 'user@example.com',
  avatar: '',
  phone: '138****8888',
};

const mockPets: PetSummary[] = [
  { pet_id: 'pet-001', name: '小橘', species: 'cat' },
  { pet_id: 'pet-002', name: '旺财', species: 'dog' },
];

const menuItems = [
  {
    section: '我的宠物',
    items: [
      { icon: '🐾', label: '宠物档案', href: '/pets', badge: `${mockPets.length}` },
      { icon: '📋', label: '健康记录', href: '/health/records' },
      { icon: '💊', label: '用药提醒', href: '/medication' },
      { icon: '📅', label: '疫苗日历', href: '/vaccines' },
    ],
  },
  {
    section: '订单与服务',
    items: [
      { icon: '🛒', label: '我的订单', href: '/orders', badge: '2' },
      { icon: '❤️', label: '收藏夹', href: '/favorites' },
      { icon: '📍', label: '收货地址', href: '/addresses' },
    ],
  },
  {
    section: '设置',
    items: [
      { icon: '👤', label: '账号设置', href: '/settings/account' },
      { icon: '🔔', label: '消息通知', href: '/settings/notifications' },
      { icon: '🔒', label: '隐私安全', href: '/settings/privacy' },
      { icon: '❓', label: '帮助与反馈', href: '/help' },
      { icon: 'ℹ️', label: '关于我们', href: '/about' },
    ],
  },
];

export default function ProfilePage() {
  const router = useRouter();
  const [user] = useState<UserProfile>(mockUser);
  const [pets] = useState<PetSummary[]>(mockPets);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

  const handleLogout = useCallback(() => {
    router.push('/');
  }, [router]);

  const getPetEmoji = (species: string): string => {
    if (species.includes('cat')) return '🐱';
    if (species.includes('dog')) return '🐕';
    return '🐾';
  };

  return (
    <div className="min-h-screen bg-neutral-50">
      <header className="sticky top-0 z-40 border-b bg-white px-4 py-3 md:hidden">
        <h1 className="text-lg font-semibold text-neutral-900">我的</h1>
      </header>

      <div className="mx-auto max-w-lg pb-20 md:max-w-4xl md:pb-6">
        <div className="mx-4 mt-4 rounded-xl bg-gradient-to-r from-primary-500 to-secondary-400 p-6 shadow-md md:mx-auto md:mt-6 md:max-w-2xl">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-white/20 text-3xl font-bold text-white backdrop-blur-sm">
                {user.nickname.charAt(0).toUpperCase()}
              </div>
              <button className="absolute -bottom-1 -right-1 flex h-7 w-7 items-center justify-center rounded-full bg-white text-primary-600 shadow-md hover:bg-neutral-50 transition-colors">
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
              </button>
            </div>

            <div className="flex-1 min-w-0">
              <h2 className="truncate text-xl font-bold text-white">{user.nickname}</h2>
              <p className="mt-0.5 truncate text-sm text-white/80">{user.email}</p>
              {user.phone && (
                <p className="mt-0.5 text-xs text-white/60">{user.phone}</p>
              )}
            </div>

            <Link
              href="/settings"
              className="rounded-full p-2 text-white/80 hover:bg-white/10 transition-colors"
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </Link>
          </div>

          <div className="mt-4 grid grid-cols-3 gap-4 rounded-lg bg-white/10 p-3 backdrop-blur-sm">
            <div className="text-center">
              <p className="text-2xl font-bold text-white">{pets.length}</p>
              <p className="text-xs text-white/80">宠物</p>
            </div>
            <div className="text-center border-l border-white/10">
              <p className="text-2xl font-bold text-white">12</p>
              <p className="text-xs text-white/80">咨询</p>
            </div>
            <div className="text-center border-l border-white/10">
              <p className="text-2xl font-bold text-white">28</p>
              <p className="text-xs text-white/80">天</p>
            </div>
          </div>
        </div>

        <div className="mx-4 mt-6 md:mx-auto md:max-w-2xl">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-neutral-900">我的宠物</h3>
            <Link
              href="/pets/new"
              className="flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700"
            >
              <span>+</span>
              <span>添加</span>
            </Link>
          </div>

          <div className="flex gap-3 overflow-x-auto pb-2">
            {pets.map(pet => (
              <Link
                key={pet.pet_id}
                href={`/pets/${pet.pet_id}`}
                className="flex-shrink-0 flex flex-col items-center gap-2 rounded-xl bg-white p-4 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex h-14 w-14 items-center justify-center rounded-full bg-neutral-100 text-2xl">
                  {getPetEmoji(pet.species)}
                </div>
                <span className="text-sm font-medium text-neutral-700 truncate max-w-[80px]">
                  {pet.name}
                </span>
              </Link>
            ))}
            
            <Link
              href="/pets/new"
              className="flex-shrink-0 flex flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-neutral-200 p-4 hover:border-primary-300 hover:bg-primary-50 transition-colors"
            >
              <div className="flex h-14 w-14 items-center justify-center rounded-full bg-neutral-50 text-2xl text-neutral-400">
                +
              </div>
              <span className="text-sm text-neutral-500">新宠物</span>
            </Link>
          </div>
        </div>

        <div className="mx-4 mt-6 space-y-6 md:mx-auto md:max-w-2xl">
          {menuItems.map((section, idx) => (
            <div key={idx}>
              <h3 className="mb-3 px-1 text-sm font-semibold uppercase tracking-wider text-neutral-400">
                {section.section}
              </h3>
              
              <div className="rounded-xl bg-white shadow-sm overflow-hidden">
                {section.items.map((item, itemIdx) => (
                  <Link
                    key={itemIdx}
                    href={item.href}
                    className={`
                      flex items-center justify-between px-4 py-3.5 transition-colors hover:bg-neutral-50
                      ${itemIdx < section.items.length - 1 ? 'border-b border-neutral-100' : ''}
                    `}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-xl">{item.icon}</span>
                      <span className="text-sm font-medium text-neutral-700">{item.label}</span>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {item.badge && (
                        <span className="rounded-full bg-primary-100 px-2 py-0.5 text-xs font-medium text-primary-700">
                          {item.badge}
                        </span>
                      )}
                      <svg className="h-4 w-4 text-neutral-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="mx-4 mt-8 md:mx-auto md:max-w-2xl">
          {!showLogoutConfirm ? (
            <button
              onClick={() => setShowLogoutConfirm(true)}
              className="w-full rounded-xl border border-red-200 bg-white py-3 text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
            >
              退出登录
            </button>
          ) : (
            <div className="rounded-xl border border-red-300 bg-red-50 p-4">
              <p className="text-center text-sm text-red-800 mb-3">
                确定要退出登录吗？
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowLogoutConfirm(false)}
                  className="flex-1 rounded-lg border border-neutral-200 bg-white py-2 text-sm font-medium text-neutral-700 hover:bg-neutral-50 transition-colors"
                >
                  取消
                </button>
                <button
                  onClick={handleLogout}
                  className="flex-1 rounded-lg bg-red-600 py-2 text-sm font-medium text-white hover:bg-red-700 transition-colors"
                >
                  确认退出
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="mt-8 text-center text-xs text-neutral-400">
          <p>AI 宠物健康助手 v1.0.0</p>
          <p className="mt-1">&copy; 2026 All Rights Reserved</p>
        </div>
      </div>

      <div className="h-20 md:h-0" />
    </div>
  );
}
