'use client';

interface PageLoadingProps {
  type?: 'default' | 'chat' | 'list' | 'card';
}

export default function PageLoading({ type = 'default' }: PageLoadingProps) {
  switch (type) {
    case 'chat':
      return <ChatSkeleton />;
    case 'list':
      return <ListSkeleton />;
    case 'card':
      return <CardSkeleton />;
    default:
      return <DefaultSkeleton />;
  }
}

function DefaultSkeleton() {
  return (
    <div className="flex min-h-screen animate-pulse flex-col bg-gray-50 p-6">
      <div className="mb-6 h-8 w-48 rounded-lg bg-gray-200" />
      <div className="mb-4 h-4 w-full max-w-2xl rounded bg-gray-200" />
      <div className="mb-4 h-4 w-3/4 max-w-xl rounded bg-gray-200" />
      <div className="mb-8 h-4 w-1/2 max-w-md rounded bg-gray-200" />
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-40 rounded-xl bg-gray-200" />
        ))}
      </div>
    </div>
  );
}

function ChatSkeleton() {
  return (
    <div className="flex min-h-screen animate-pulse flex-col bg-gray-50">
      <div className="border-b bg-white p-4">
        <div className="h-6 w-32 rounded bg-gray-200" />
      </div>
      <div className="flex-1 space-y-4 p-4">
        <div className="flex justify-end">
          <div className="h-16 w-64 rounded-2xl rounded-br-sm bg-primary-100" />
        </div>
        <div className="flex justify-start">
          <div className="h-24 w-80 rounded-2xl rounded-bl-sm bg-gray-200" />
        </div>
        <div className="flex justify-end">
          <div className="h-12 w-48 rounded-2xl rounded-br-sm bg-primary-100" />
        </div>
        <div className="flex justify-start">
          <div className="h-20 w-72 rounded-2xl rounded-bl-sm bg-gray-200" />
        </div>
      </div>
      <div className="border-t bg-white p-4">
        <div className="h-12 w-full rounded-full bg-gray-200" />
      </div>
    </div>
  );
}

function ListSkeleton() {
  return (
    <div className="flex min-h-screen animate-pulse flex-col bg-gray-50">
      <div className="border-b bg-white p-4">
        <div className="flex items-center justify-between">
          <div className="h-7 w-36 rounded bg-gray-200" />
          <div className="h-10 w-64 rounded-full bg-gray-200" />
        </div>
      </div>
      <div className="flex-1 space-y-3 p-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="flex items-center gap-4 rounded-xl bg-white p-4">
            <div className="h-12 w-12 shrink-0 rounded-full bg-gray-200" />
            <div className="flex-1 space-y-2">
              <div className="h-4 w-1/3 rounded bg-gray-200" />
              <div className="h-3 w-2/3 rounded bg-gray-100" />
            </div>
            <div className="h-3 w-16 rounded bg-gray-100" />
          </div>
        ))}
      </div>
    </div>
  );
}

function CardSkeleton() {
  return (
    <div className="flex min-h-screen animate-pulse flex-col bg-gray-50">
      <div className="border-b bg-white p-4">
        <div className="h-7 w-28 rounded bg-gray-200" />
      </div>
      <div className="flex-1 p-4">
        <div className="mb-4 flex gap-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-9 w-20 rounded-full bg-gray-200" />
          ))}
        </div>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="overflow-hidden rounded-xl bg-white">
              <div className="h-36 bg-gray-200" />
              <div className="space-y-2 p-3">
                <div className="h-4 w-3/4 rounded bg-gray-200" />
                <div className="h-3 w-1/2 rounded bg-gray-100" />
                <div className="h-5 w-1/3 rounded bg-gray-200" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
