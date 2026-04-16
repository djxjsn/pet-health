
import type { NextPage } from 'next';

const PetDetailPage: NextPage<{ params: { id: string } }> = ({ params }) => {
  // Mock data for a single pet
  const pet = {
    id: params.id,
    name: '豆豆',
    breed: '金毛',
    age: 2,
    weight: 15.2,
    avatar: '🐕',
    gender: '公',
    birthDate: '2023-04-15',
    allergies: ['鸡肉', '尘螨'],
    medicalHistory: [
      {
        date: '2025-12-10',
        condition: '真菌性皮炎 (已治愈)',
        treatment: '开药: 酮康唑洗剂',
      },
    ],
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4 sm:p-6 md:p-8">
      <div className="mx-auto max-w-2xl">
        <div className="mb-6 flex items-center justify-between">
          <a href="/pets" className="text-sm font-medium text-indigo-600 hover:text-indigo-500">
            &larr; 返回宠物列表
          </a>
          <button className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700">
            编辑
          </button>
        </div>

        <div className="rounded-lg bg-white p-8 shadow-md">
          <div className="flex flex-col items-center space-y-4 text-center">
            <div className="text-6xl">{pet.avatar}</div>
            <h1 className="text-3xl font-bold text-gray-900">{pet.name}</h1>
            <p className="text-md text-gray-500">
              {pet.breed} · {pet.age}岁
            </p>
          </div>

          <div className="mt-8 space-y-6">
            {/* Basic Info */}
            <div>
              <h3 className="mb-3 text-lg font-semibold text-gray-900">基本信息</h3>
              <div className="space-y-2 text-sm text-gray-700">
                <p><strong>性别:</strong> {pet.gender}</p>
                <p><strong>出生日期:</strong> {pet.birthDate}</p>
                <p><strong>体重:</strong> {pet.weight} kg</p>
              </div>
            </div>

            {/* Allergies */}
            <div>
              <h3 className="mb-3 text-lg font-semibold text-gray-900">过敏源</h3>
              <div className="flex flex-wrap gap-2">
                {pet.allergies.map((allergy) => (
                  <span key={allergy} className="rounded-full bg-indigo-100 px-3 py-1 text-sm font-medium text-indigo-800">
                    {allergy}
                  </span>
                ))}
              </div>
            </div>

            {/* Medical History */}
            <div>
              <h3 className="mb-3 text-lg font-semibold text-gray-900">病史记录</h3>
              <div className="space-y-4">
                {pet.medicalHistory.map((record) => (
                  <div key={record.date} className="rounded-md border border-gray-200 bg-gray-50 p-4">
                    <p className="font-semibold text-gray-800">{record.date}</p>
                    <p className="text-gray-700">{record.condition}</p>
                    <p className="text-sm text-gray-500">{record.treatment}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PetDetailPage;
