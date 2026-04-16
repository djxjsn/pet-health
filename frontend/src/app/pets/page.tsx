
import type { NextPage } from 'next';

const PetsPage: NextPage = () => {
  const pets = [
    {
      id: 1,
      name: '豆豆',
      breed: '金毛',
      age: 2,
      weight: 15,
      avatar: '🐕',
      active: true,
    },
    {
      id: 2,
      name: '咪咪',
      breed: '布偶',
      age: 1,
      weight: 4,
      avatar: '🐱',
      active: false,
    },
  ];

  return (
    <div className="min-h-screen bg-neutral-50 p-4 sm:p-6 md:p-8">
      <div className="mx-auto max-w-4xl">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-neutral-900">我的宠物</h1>
          <a
            href="/pets/new"
            className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
          >
            + 添加新宠物
          </a>
        </div>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {pets.map((pet) => (
            <div
              key={pet.id}
              className={`rounded-lg border bg-white p-6 shadow-sm ${pet.active ? 'border-primary-500 ring-2 ring-primary-500' : 'border-neutral-200'}`}
            >
              <div className="flex items-center space-x-4">
                <div className="text-4xl">{pet.avatar}</div>
                <div>
                  <h2 className="text-lg font-semibold text-neutral-900">{pet.name}</h2>
                  <p className="text-sm text-neutral-500">
                    {pet.breed} · {pet.age}岁 · {pet.weight}kg
                  </p>
                </div>
              </div>
              <div className="mt-4 flex justify-end space-x-2">
                <a
                  href={`/pets/${pet.id}`}
                  className="rounded-md bg-neutral-100 px-3 py-1 text-sm font-medium text-neutral-700 hover:bg-neutral-200"
                >
                  查看档案
                </a>
                {!pet.active && (
                  <button className="rounded-md bg-primary-100 px-3 py-1 text-sm font-medium text-primary-700 hover:bg-primary-200">
                    开始对话
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PetsPage;
