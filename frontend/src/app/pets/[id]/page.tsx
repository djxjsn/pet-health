'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { petApi } from '@/api/pets';
import { deviceApi } from '@/api/devices';
import type { Pet, PetAllergy, PetVaccination } from '@/types';

const SPECIES_LABELS: Record<string, string> = {
  dog: '犬', cat: '猫', bird: '鸟', rabbit: '兔', hamster: '仓鼠', fish: '鱼', other: '其他',
};
const GENDER_LABELS: Record<string, string> = { male: '公', female: '母', unknown: '未知' };
const STATUS_LABELS: Record<string, { text: string; color: string }> = {
  healthy: { text: '健康', color: 'bg-green-100 text-green-700' },
  ill: { text: '生病中', color: 'bg-red-100 text-red-700' },
  recovering: { text: '恢复中', color: 'bg-yellow-100 text-yellow-700' },
  chronic: { text: '慢性病', color: 'bg-orange-100 text-orange-700' },
  deceased: { text: '已故', color: 'bg-neutral-200 text-neutral-600' },
};
const ALLERGY_SEVERITY: Record<string, { text: string; color: string }> = {
  mild: { text: '轻微', color: 'bg-yellow-100 text-yellow-700' },
  moderate: { text: '中等', color: 'bg-orange-100 text-orange-700' },
  severe: { text: '严重', color: 'bg-red-100 text-red-700' },
  anaphylaxis: { text: '过敏性休克', color: 'bg-red-200 text-red-800' },
};

export default function PetDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [pet, setPet] = useState<Pet | null>(null);
  const [allergies, setAllergies] = useState<PetAllergy[]>([]);
  const [vaccinations, setVaccinations] = useState<PetVaccination[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = useCallback(async () => {
    if (!id) return;
    try {
      setLoading(true);
      const [petData, allergyData, vaccineData] = await Promise.all([
        petApi.getById(id),
        petApi.listAllergies(id).catch(() => []),
        petApi.listVaccinations(id).catch(() => []),
      ]);
      setPet(petData);
      setAllergies(allergyData);
      setVaccinations(vaccineData);
      setError(null);
    } catch {
      setError('加载宠物信息失败');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  const handleDelete = async () => {
    if (!pet || !confirm(`确定要删除「${pet.name}」的档案吗？此操作可恢复。`)) return;
    try {
      await petApi.delete(pet.pet_id);
      router.push('/pets');
    } catch {
      alert('删除失败');
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-500 border-t-transparent" />
      </div>
    );
  }

  if (error || !pet) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <p className="text-lg text-red-600">{error || '宠物不存在'}</p>
          <Link href="/pets" className="mt-4 inline-block text-primary-600 hover:underline">返回列表</Link>
        </div>
      </div>
    );
  }

  const age = pet.birth_date
    ? Math.floor((Date.now() - new Date(pet.birth_date).getTime()) / (365.25 * 24 * 60 * 60 * 1000))
    : null;
  const statusInfo = STATUS_LABELS[pet.current_status || 'healthy'] || STATUS_LABELS.healthy;

  return (
    <div className="min-h-screen bg-neutral-50 p-4 sm:p-6 md:p-8">
      <div className="mx-auto max-w-2xl">
        <div className="mb-6 flex items-center justify-between">
          <Link href="/pets" className="text-sm font-medium text-primary-600 hover:text-primary-500">
            &larr; 返回宠物列表
          </Link>
          <div className="flex gap-2">
            <Link
              href={`/pets/${pet.pet_id}/edit`}
              className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
            >
              编辑
            </Link>
            <button
              onClick={handleDelete}
              className="rounded-md bg-neutral-100 px-4 py-2 text-sm font-medium text-neutral-600 hover:bg-neutral-200"
            >
              删除
            </button>
          </div>
        </div>

        {/* 头部 */}
        <div className="rounded-lg bg-white p-8 shadow-md">
          <div className="flex flex-col items-center space-y-4 text-center">
            <div className="text-6xl">
              {pet.species === 'dog' ? '🐕' : pet.species === 'cat' ? '🐈' : pet.species === 'bird' ? '🐦' : pet.species === 'rabbit' ? '🐇' : '🐾'}
            </div>
            <h1 className="text-3xl font-bold text-neutral-900">{pet.name}</h1>
            <p className="text-md text-neutral-500">
              {pet.breed || SPECIES_LABELS[pet.species] || pet.species}
              {age !== null ? ` · ${age}岁` : ''}
              {pet.weight ? ` · ${pet.weight}kg` : ''}
            </p>
            <span className={`rounded-full px-3 py-1 text-xs font-medium ${statusInfo.color}`}>
              {statusInfo.text}
            </span>
          </div>

          {/* 基本信息 */}
          <div className="mt-8 space-y-6">
            <div>
              <h3 className="mb-3 text-lg font-semibold text-neutral-900">基本信息</h3>
              <div className="grid grid-cols-2 gap-3 text-sm">
                {[
                  ['性别', GENDER_LABELS[pet.gender || 'unknown'] || pet.gender],
                  ['出生日期', pet.birth_date || '--'],
                  ['体重', pet.weight ? `${pet.weight} kg` : '--'],
                  ['血型', pet.blood_type || '--'],
                  ['芯片号', pet.microchip_id || '--'],
                  ['饮食类型', pet.diet_type || '--'],
                  ['绝育', pet.is_neutered ? `是${pet.spay_neuter_date ? ` (${pet.spay_neuter_date})` : ''}` : '否'],
                  ['疫苗', pet.is_vaccinated ? '已接种' : '未接种'],
                  ['紧急联系人', pet.emergency_contact || '--'],
                  ['来源', pet.source || '--'],
                ].map(([label, value], i) => (
                  <div key={i} className="rounded-md bg-neutral-50 p-3">
                    <span className="text-neutral-500">{label}</span>
                    <p className="font-medium text-neutral-900">{value}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* 过敏源 */}
            <div>
              <h3 className="mb-3 text-lg font-semibold text-neutral-900">过敏源</h3>
              {allergies.length === 0 ? (
                <p className="text-sm text-neutral-500">暂无过敏源记录</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {allergies.map((a) => {
                    const sev = ALLERGY_SEVERITY[a.severity] || ALLERGY_SEVERITY.mild;
                    return (
                      <span key={a.allergy_id} className={`rounded-full px-3 py-1 text-sm font-medium ${sev.color}`}>
                        {a.allergen_name}
                        {a.reaction_desc ? ` (${a.reaction_desc})` : ''}
                      </span>
                    );
                  })}
                </div>
              )}
            </div>

            {/* 疫苗记录 */}
            <div>
              <h3 className="mb-3 text-lg font-semibold text-neutral-900">疫苗接种记录</h3>
              {vaccinations.length === 0 ? (
                <p className="text-sm text-neutral-500">暂无疫苗记录</p>
              ) : (
                <div className="space-y-3">
                  {vaccinations.map((v) => (
                    <div key={v.vaccination_id} className="rounded-md border border-neutral-200 bg-neutral-50 p-4">
                      <div className="flex items-center justify-between">
                        <p className="font-semibold text-neutral-800">{v.vaccine_name}</p>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                          v.vaccine_type === 'core' ? 'bg-blue-100 text-blue-700' : 'bg-neutral-100 text-neutral-600'
                        }`}>
                          {v.vaccine_type === 'core' ? '核心' : '非核心'}
                        </span>
                      </div>
                      <p className="text-sm text-neutral-600 mt-1">
                        接种日期: {v.administered_date}
                        {v.dose_number ? ` · 第${v.dose_number}针` : ''}
                        {v.vet_name ? ` · ${v.vet_name}` : ''}
                        {v.hospital ? ` · ${v.hospital}` : ''}
                      </p>
                      {v.next_due_date && (
                        <p className="text-sm text-orange-600 mt-1">
                          下次到期: {v.next_due_date}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}