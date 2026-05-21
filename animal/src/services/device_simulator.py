"""
设备健康数据模拟生成器

用于 Phase 0 POC 阶段，在未对接真实设备 API 前生成模拟健康数据。
模拟的指标与合理范围：
  - heart_rate (心率): 猫 110-140 bpm, 犬 60-120 bpm（安静状态）
  - steps (步数): 0-15000 步/小时不等
  - temperature (体温): 猫犬 37.5-39.2°C
  - activity_level (活动级别): 1-10 级别
  - sleep_hours (睡眠时长): 累计时长
  - calories (消耗卡路里): 模拟值
"""
import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


# 各物种基准值范围
SPECIES_BASELINES = {
    "dog": {
        "heart_rate": {"mean": 90, "std": 15, "min": 50, "max": 140},
        "temperature": {"mean": 38.5, "std": 0.3, "min": 37.5, "max": 39.2},
        "activity_level": {"mean": 5, "std": 2, "min": 1, "max": 10},
        "steps": {"hourly": (100, 2000)},
        "sleep_hours": {"daily": (12, 16)},
        "calories": {"daily": (200, 800)},
    },
    "cat": {
        "heart_rate": {"mean": 120, "std": 15, "min": 100, "max": 160},
        "temperature": {"mean": 38.5, "std": 0.3, "min": 37.5, "max": 39.2},
        "activity_level": {"mean": 4, "std": 2, "min": 1, "max": 10},
        "steps": {"hourly": (50, 800)},
        "sleep_hours": {"daily": (14, 18)},
        "calories": {"daily": (150, 400)},
    },
    "rabbit": {
        "heart_rate": {"mean": 130, "std": 20, "min": 100, "max": 180},
        "temperature": {"mean": 38.0, "std": 0.5, "min": 37.0, "max": 39.5},
        "activity_level": {"mean": 4, "std": 2, "min": 1, "max": 10},
        "steps": {"hourly": (20, 500)},
        "sleep_hours": {"daily": (8, 12)},
        "calories": {"daily": (100, 300)},
    },
}


def _clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, value))


def _gaussian(mean: float, std: float, min_val: float, max_val: float) -> float:
    val = random.gauss(mean, std)
    return _clamp(val, min_val, max_val)


def _hourly_activity_multiplier(hour: int) -> float:
    """根据小时返回活动倍率，模拟昼夜节律"""
    if 0 <= hour < 6:
        return 0.2   # 深夜休息
    elif 6 <= hour < 9:
        return 1.5   # 早晨活跃
    elif 9 <= hour < 12:
        return 0.8   # 上午平静
    elif 12 <= hour < 14:
        return 0.5   # 午后休息
    elif 14 <= hour < 17:
        return 1.0   # 下午一般
    elif 17 <= hour < 20:
        return 1.8   # 傍晚活跃
    elif 20 <= hour < 23:
        return 1.2   # 晚间
    else:
        return 0.3   # 深夜


class DeviceSimulator:
    """设备数据模拟器"""

    def __init__(self, species: str = "dog", seed: Optional[int] = None):
        """
        Args:
            species: 宠物物种 (dog/cat/rabbit)
            seed: 随机种子，用于可复现模拟
        """
        if species not in SPECIES_BASELINES:
            raise ValueError(f"不支持的物种: {species}，可选: {list(SPECIES_BASELINES.keys())}")
        self.species = species
        self.baseline = SPECIES_BASELINES[species]
        if seed is not None:
            random.seed(seed)

    def generate_data_point(self, device_id: str, pet_id: str, timestamp: datetime) -> List[Dict[str, Any]]:
        """生成单个时间点的全套健康指标数据"""
        hour = timestamp.hour
        mult = _hourly_activity_multiplier(hour)

        hr = self.baseline["heart_rate"]
        heart_rate = round(_gaussian(hr["mean"] * mult, hr["std"], hr["min"], hr["max"]), 1)

        temp = self.baseline["temperature"]
        temperature = round(_gaussian(temp["mean"], temp["std"], temp["min"], temp["max"]), 1)

        al = self.baseline["activity_level"]
        activity = round(_gaussian(al["mean"] * mult, al["std"], al["min"], al["max"]))

        step_range = self.baseline["steps"]["hourly"]
        steps = random.randint(int(step_range[0] * mult), int(step_range[1] * mult))

        # 睡眠时长按天计算，这里每小时增量（仅深夜累计）
        sleep_increment = 0.0
        if hour < 6:
            sleep_increment = round(random.uniform(0.5, 1.0), 2)

        cal = self.baseline["calories"]["daily"]
        hourly_cal = round(cal[0] / 24 + random.uniform(0, (cal[1] - cal[0]) / 24 * mult), 1)

        return [
            {"device_id": device_id, "pet_id": pet_id, "metric_name": "heart_rate",
             "value": heart_rate, "timestamp": timestamp},
            {"device_id": device_id, "pet_id": pet_id, "metric_name": "steps",
             "value": float(steps), "timestamp": timestamp},
            {"device_id": device_id, "pet_id": pet_id, "metric_name": "temperature",
             "value": temperature, "timestamp": timestamp},
            {"device_id": device_id, "pet_id": pet_id, "metric_name": "activity_level",
             "value": float(activity), "timestamp": timestamp},
            {"device_id": device_id, "pet_id": pet_id, "metric_name": "sleep_hours",
             "value": sleep_increment, "timestamp": timestamp},
            {"device_id": device_id, "pet_id": pet_id, "metric_name": "calories",
             "value": hourly_cal, "timestamp": timestamp},
        ]

    def generate_hourly_data(
        self,
        device_id: str,
        pet_id: str,
        start_time: datetime,
        hours: int = 24,
    ) -> List[Dict[str, Any]]:
        """生成连续多小时的模拟数据"""
        all_data = []
        for h in range(hours):
            ts = start_time + timedelta(hours=h)
            all_data.extend(self.generate_data_point(device_id, pet_id, ts))
        return all_data

    def generate_daily_data(
        self,
        device_id: str,
        pet_id: str,
        date: datetime,
        interval_minutes: int = 15,
    ) -> List[Dict[str, Any]]:
        """生成一整天的模拟数据（默认每15分钟一条）"""
        all_data = []
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        points = 24 * 60 // interval_minutes

        for i in range(points):
            ts = start + timedelta(minutes=i * interval_minutes)
            all_data.extend(self.generate_data_point(device_id, pet_id, ts))

        return all_data

    def generate_anomaly_event(
        self,
        device_id: str,
        pet_id: str,
        timestamp: datetime,
        anomaly_type: str = "heart_rate_high",
    ) -> List[Dict[str, Any]]:
        """生成异常事件数据（用于测试预警功能）"""
        data = self.generate_data_point(device_id, pet_id, timestamp)

        anomaly_values = {
            "heart_rate_high": ("heart_rate", 180.0),
            "heart_rate_low": ("heart_rate", 30.0),
            "temperature_high": ("temperature", 40.5),
            "temperature_low": ("temperature", 35.0),
            "inactive": ("activity_level", 0.0),
        }

        if anomaly_type in anomaly_values:
            metric, value = anomaly_values[anomaly_type]
            for d in data:
                if d["metric_name"] == metric:
                    d["value"] = value
        return data


# ==================== 便捷工厂函数 ====================

def create_simulator_for_pet(species: str) -> DeviceSimulator:
    """根据物种创建对应的模拟器"""
    return DeviceSimulator(species=species)


def generate_poc_data(
    device_id: str,
    pet_id: str,
    species: str,
    days: int = 7,
    interval_minutes: int = 15,
) -> List[Dict[str, Any]]:
    """
    POC 阶段便捷函数：生成多天模拟数据

    Args:
        device_id: 设备ID
        pet_id: 宠物ID
        species: 物种
        days: 模拟天数
        interval_minutes: 采样间隔（分钟）

    Returns:
        全部模拟数据点列表
    """
    sim = DeviceSimulator(species=species)
    all_data = []
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    for d in range(days):
        date = today - timedelta(days=days - d - 1)
        day_data = sim.generate_daily_data(device_id, pet_id, date, interval_minutes)
        all_data.extend(day_data)

    return all_data