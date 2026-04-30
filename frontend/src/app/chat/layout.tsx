'use client';

import DesktopLayout from '@/components/layout/DesktopLayout';

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <DesktopLayout>{children}</DesktopLayout>;
}
