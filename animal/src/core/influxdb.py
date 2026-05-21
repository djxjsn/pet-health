"""
InfluxDB 时序数据库集成模块

用于存储和查询宠物穿戴设备的健康时序数据。
数据模型设计：
  - Bucket: pet_health_metrics
  - Measurement: device_health
  - Tags: device_id, pet_id, metric_name
  - Fields: value (float)
  - Timestamp: 数据采集时间

安装依赖: pip install influxdb-client
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.query_api import QueryApi

from src.core.config import get_settings

logger = logging.getLogger(__name__)


class InfluxDBManager:
    """InfluxDB 连接管理器（单例）"""

    _instance: Optional["InfluxDBManager"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        settings = get_settings()
        self._url = settings.INFLUXDB_URL
        self._token = settings.INFLUXDB_TOKEN
        self._org = settings.INFLUXDB_ORG
        self._bucket = settings.INFLUXDB_BUCKET
        self._timeout = settings.INFLUXDB_TIMEOUT_MS
        self._client: Optional[InfluxDBClient] = None
        self._write_api = None
        self._query_api: Optional[QueryApi] = None
        self._initialized = True

    def _ensure_client(self):
        """懒加载客户端连接"""
        if self._client is None:
            self._client = InfluxDBClient(
                url=self._url,
                token=self._token,
                org=self._org,
                timeout=self._timeout,
            )
            self._write_api = self._client.write_api(write_options=SYNCHRONOUS)
            self._query_api = self._client.query_api()
            logger.info(f"InfluxDB 连接成功: {self._url}")

    @property
    def write_api(self):
        self._ensure_client()
        return self._write_api

    @property
    def query_api(self) -> QueryApi:
        self._ensure_client()
        return self._query_api

    # ==================== 数据写入 ====================

    def write_health_data(
        self,
        device_id: str,
        pet_id: str,
        metric_name: str,
        value: float,
        timestamp: Optional[datetime] = None,
    ):
        """
        写入一条健康指标数据

        Args:
            device_id: 设备ID
            pet_id: 宠物ID
            metric_name: 指标名称 (heart_rate/steps/temperature/activity_level/sleep_hours/calories)
            value: 指标值
            timestamp: 时间戳，默认当前UTC时间
        """
        point = Point("device_health") \
            .tag("device_id", device_id) \
            .tag("pet_id", pet_id) \
            .tag("metric_name", metric_name) \
            .field("value", float(value)) \
            .time(timestamp or datetime.utcnow(), WritePrecision.NS)

        self.write_api.write(bucket=self._bucket, org=self._org, record=point)

    def write_batch(
        self,
        device_id: str,
        pet_id: str,
        metrics: List[Dict[str, Any]],
    ):
        """
        批量写入健康指标数据

        Args:
            device_id: 设备ID
            pet_id: 宠物ID
            metrics: [{"metric_name": "heart_rate", "value": 80.5, "timestamp": datetime}, ...]
        """
        points = []
        for m in metrics:
            point = Point("device_health") \
                .tag("device_id", device_id) \
                .tag("pet_id", pet_id) \
                .tag("metric_name", m["metric_name"]) \
                .field("value", float(m["value"])) \
                .time(m.get("timestamp", datetime.utcnow()), WritePrecision.NS)
            points.append(point)

        self.write_api.write(bucket=self._bucket, org=self._org, record=points)
        logger.debug(f"批量写入 {len(points)} 条健康数据")

    # ==================== 数据查询 ====================

    def query_metrics(
        self,
        device_id: str,
        metric_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        interval: str = "1h",
    ) -> List[Dict[str, Any]]:
        """
        查询指定设备的健康指标时序数据

        Args:
            device_id: 设备ID
            metric_name: 指标名称，不传则查全部
            start_time: 开始时间
            end_time: 结束时间
            interval: 聚合间隔 (1m/5m/15m/1h/1d)

        Returns:
            [{"metric_name": "heart_rate", "value": 80.5, "timestamp": datetime}, ...]
        """
        end_time = end_time or datetime.utcnow()
        start_time = start_time or (end_time - timedelta(hours=24))

        metric_filter = f'and r.metric_name == "{metric_name}"' if metric_name else ""

        query = f'''
        from(bucket: "{self._bucket}")
          |> range(start: {start_time.isoformat()}Z, stop: {end_time.isoformat()}Z)
          |> filter(fn: (r) => r._measurement == "device_health")
          |> filter(fn: (r) => r.device_id == "{device_id}")
          {metric_filter}
          |> filter(fn: (r) => r._field == "value")
          |> aggregateWindow(every: {interval}, fn: mean, createEmpty: false)
          |> yield(name: "mean")
        '''

        result = self.query_api.query(org=self._org, query=query)

        records = []
        for table in result:
            for record in table.records:
                records.append({
                    "metric_name": record.values.get("metric_name", ""),
                    "value": round(record.get_value(), 2) if record.get_value() else 0,
                    "timestamp": record.get_time(),
                })
        return records

    def query_aggregation(
        self,
        device_id: str,
        metric_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        查询指定指标在时间段内的聚合统计

        Returns:
            {"metric_name": "heart_rate", "avg": 85.2, "min": 60.0, "max": 120.0, "latest": 82.0, "count": 1440}
        """
        end_time = end_time or datetime.utcnow()
        start_time = start_time or (end_time - timedelta(hours=24))

        query = f'''
        from(bucket: "{self._bucket}")
          |> range(start: {start_time.isoformat()}Z, stop: {end_time.isoformat()}Z)
          |> filter(fn: (r) => r._measurement == "device_health")
          |> filter(fn: (r) => r.device_id == "{device_id}")
          |> filter(fn: (r) => r.metric_name == "{metric_name}")
          |> filter(fn: (r) => r._field == "value")

        data = from(bucket: "{self._bucket}")
          |> range(start: {start_time.isoformat()}Z, stop: {end_time.isoformat()}Z)
          |> filter(fn: (r) => r._measurement == "device_health")
          |> filter(fn: (r) => r.device_id == "{device_id}")
          |> filter(fn: (r) => r.metric_name == "{metric_name}")
          |> filter(fn: (r) => r._field == "value")

        union(tables: [
          data |> mean() |> map(fn: (r) => ({{r with _field: "avg"}})),
          data |> min() |> map(fn: (r) => ({{r with _field: "min"}})),
          data |> max() |> map(fn: (r) => ({{r with _field: "max"}})),
          data |> last() |> map(fn: (r) => ({{r with _field: "latest"}})),
          data |> count() |> map(fn: (r) => ({{r with _field: "count"}})),
        ])
        |> yield(name: "aggregation")
        '''

        result = self.query_api.query(org=self._org, query=query)

        agg = {"metric_name": metric_name, "avg": 0, "min": 0, "max": 0, "latest": 0, "count": 0}
        for table in result:
            for record in table.records:
                field = record.get_field()
                value = record.get_value()
                if field == "avg":
                    agg["avg"] = round(value, 2) if value else 0
                elif field == "min":
                    agg["min"] = round(value, 2) if value else 0
                elif field == "max":
                    agg["max"] = round(value, 2) if value else 0
                elif field == "latest":
                    agg["latest"] = round(value, 2) if value else 0
                elif field == "count":
                    agg["count"] = int(value) if value else 0

        return agg if agg["count"] > 0 else None

    def get_latest_value(
        self,
        device_id: str,
        metric_name: str,
    ) -> Optional[Dict[str, Any]]:
        """获取最新的单条指标数据"""
        query = f'''
        from(bucket: "{self._bucket}")
          |> range(start: -1h)
          |> filter(fn: (r) => r._measurement == "device_health")
          |> filter(fn: (r) => r.device_id == "{device_id}")
          |> filter(fn: (r) => r.metric_name == "{metric_name}")
          |> filter(fn: (r) => r._field == "value")
          |> last()
        '''

        result = self.query_api.query(org=self._org, query=query)
        for table in result:
            for record in table.records:
                return {
                    "metric_name": metric_name,
                    "value": round(record.get_value(), 2) if record.get_value() else 0,
                    "timestamp": record.get_time(),
                }
        return None

    def get_all_latest(
        self,
        device_id: str,
    ) -> List[Dict[str, Any]]:
        """获取设备所有指标的最新值"""
        metrics = [
            "heart_rate", "steps", "temperature", "activity_level",
            "sleep_hours", "calories"
        ]
        results = []
        for metric in metrics:
            latest = self.get_latest_value(device_id, metric)
            if latest:
                results.append(latest)
        return results

    def close(self):
        """关闭连接"""
        if self._client:
            self._client.close()
            self._client = None
            self._write_api = None
            self._query_api = None
            logger.info("InfluxDB 连接已关闭")


def get_influxdb() -> InfluxDBManager:
    """获取 InfluxDB 管理器实例（依赖注入用）"""
    return InfluxDBManager()