"""
健康日报生成服务

从 InfluxDB 读取设备的健康时序数据，聚合统计后调用 LLM 生成自然语言的日报。
"""
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from src.core.influxdb import get_influxdb
from src.core.config import get_settings

logger = logging.getLogger(__name__)

# 各指标的中文名和单位
METRIC_INFO = {
    "heart_rate": {"name": "心率", "unit": "bpm", "healthy_range": "犬60-120 / 猫110-140"},
    "steps": {"name": "步数", "unit": "步", "healthy_range": "因犬种和活动量不同"},
    "temperature": {"name": "体温", "unit": "°C", "healthy_range": "37.5-39.2"},
    "activity_level": {"name": "活动级别", "unit": "级(1-10)", "healthy_range": "3-7"},
    "sleep_hours": {"name": "睡眠时长", "unit": "小时", "healthy_range": "犬12-16 / 猫14-18"},
    "calories": {"name": "消耗卡路里", "unit": "kcal", "healthy_range": "因体型不同"},
}


class ReportService:
    """日报生成服务"""

    def __init__(self):
        self.influxdb = get_influxdb()
        self.settings = get_settings()

    def collect_daily_metrics(
        self,
        device_id: str,
        date_str: str,
    ) -> Dict[str, Any]:
        """收集指定设备某一天的所有指标聚合数据"""
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError("日期格式错误，需要 YYYY-MM-DD")

        start_time = target_date.replace(hour=0, minute=0, second=0)
        end_time = target_date.replace(hour=23, minute=59, second=59)

        metrics_summary = {}
        alerts = []

        for metric_name, info in METRIC_INFO.items():
            agg = self.influxdb.query_aggregation(
                device_id=device_id,
                metric_name=metric_name,
                start_time=start_time,
                end_time=end_time,
            )
            if agg:
                metrics_summary[metric_name] = {
                    "name": info["name"],
                    "unit": info["unit"],
                    "avg": agg["avg"],
                    "min": agg["min"],
                    "max": agg["max"],
                    "latest": agg["latest"],
                    "count": agg["count"],
                    "healthy_range": info["healthy_range"],
                }

        # 检查预警
        alerts = self._check_alerts(metrics_summary)

        return {
            "date": date_str,
            "device_id": device_id,
            "metrics": metrics_summary,
            "alerts": alerts,
            "data_available": len(metrics_summary) > 0,
        }

    def _check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于指标数据检查是否触发预警"""
        alerts = []
        s = self.settings

        def _add(metric_name: str, value: float, threshold: float, msg: str, severity: str):
            alerts.append({
                "metric_name": metric_name,
                "value": value,
                "threshold": threshold,
                "message": msg,
                "severity": severity,
            })

        if "heart_rate" in metrics:
            hr = metrics["heart_rate"]
            if hr["avg"] > s.ALERT_HEART_RATE_HIGH:
                _add("heart_rate", hr["avg"], s.ALERT_HEART_RATE_HIGH,
                     f"平均心率 {hr['avg']} bpm 高于阈值 {s.ALERT_HEART_RATE_HIGH} bpm，请注意", "warning")
            if hr["min"] < s.ALERT_HEART_RATE_LOW:
                _add("heart_rate", hr["min"], s.ALERT_HEART_RATE_LOW,
                     f"最低心率 {hr['min']} bpm 低于阈值 {s.ALERT_HEART_RATE_LOW} bpm", "critical")

        if "temperature" in metrics:
            temp = metrics["temperature"]
            if temp["max"] > s.ALERT_TEMPERATURE_HIGH:
                _add("temperature", temp["max"], s.ALERT_TEMPERATURE_HIGH,
                     f"最高体温 {temp['max']}°C 高于阈值 {s.ALERT_TEMPERATURE_HIGH}°C，可能存在发热", "warning")
            if temp["min"] < s.ALERT_TEMPERATURE_LOW:
                _add("temperature", temp["min"], s.ALERT_TEMPERATURE_LOW,
                     f"最低体温 {temp['min']}°C 低于阈值 {s.ALERT_TEMPERATURE_LOW}°C", "critical")

        return alerts

    def build_report_context(
        self,
        pet_name: str,
        collected_data: Dict[str, Any],
    ) -> str:
        """构建 LLM 报告的上下文文本"""
        metrics = collected_data.get("metrics", {})
        alerts = collected_data.get("alerts", [])

        parts = [f"宠物名称: {pet_name}"]
        parts.append(f"报告日期: {collected_data['date']}")
        parts.append("")

        parts.append("## 今日健康数据统计\n")

        metric_order = ["heart_rate", "steps", "temperature", "activity_level", "sleep_hours", "calories"]
        for key in metric_order:
            if key not in metrics:
                continue
            m = metrics[key]
            parts.append(
                f"- {m['name']}: 平均 {m['avg']}{m['unit']}, "
                f"最低 {m['min']}{m['unit']}, 最高 {m['max']}{m['unit']}, "
                f"健康范围 {m['healthy_range']}"
            )

        if alerts:
            parts.append("")
            parts.append("## 预警提醒\n")
            for alert in alerts:
                icon = "严重" if alert["severity"] == "critical" else "注意"
                parts.append(f"- [{icon}] {alert['message']}")

        return "\n".join(parts)

    def generate_template_report(
        self,
        pet_name: str,
        collected_data: Dict[str, Any],
    ) -> str:
        """
        生成模板化日报（不依赖 LLM，用于 POC 阶段无 API Key 时使用）
        当 LLM 不可用时降级使用此方法
        """
        metrics = collected_data.get("metrics", {})
        alerts = collected_data.get("alerts", [])

        if not metrics:
            return f"## {pet_name} 健康日报 - {collected_data['date']}\n\n暂无数据。"

        lines = [
            f"# {pet_name} 健康日报",
            f"**日期**: {collected_data['date']}",
            "",
            "## 今日健康总览",
            "",
        ]

        # 心率
        if "heart_rate" in metrics:
            hr = metrics["heart_rate"]
            level = "偏高，请注意观察" if hr["avg"] > 130 else (
                "偏低，建议观察" if hr["avg"] < 50 else "正常范围"
            )
            lines.append(f"**心率**: 平均 {hr['avg']} bpm（{level}），"
                        f"波动范围 {hr['min']}-{hr['max']} bpm")

        # 步数
        if "steps" in metrics:
            st = metrics["steps"]
            lines.append(f"**今日步数**: 累计 {st['avg'] * st['count']:.0f} 步，"
                        f"每小时平均 {st['avg']:.0f} 步")

        # 体温
        if "temperature" in metrics:
            temp = metrics["temperature"]
            level = "偏高" if temp["max"] > 39.2 else ("偏低" if temp["min"] < 37.5 else "正常")
            lines.append(f"**体温**: 平均 {temp['avg']}°C（{level}），"
                        f"范围 {temp['min']}-{temp['max']}°C")

        # 活动级别
        if "activity_level" in metrics:
            al = metrics["activity_level"]
            level = "非常活跃" if al["avg"] > 7 else (
                "活跃度偏低" if al["avg"] < 3 else "正常活动"
            )
            lines.append(f"**活动级别**: 平均 {al['avg']} 级（{level}）")

        # 睡眠
        if "sleep_hours" in metrics:
            sl = metrics["sleep_hours"]
            total = sl["avg"] * sl["count"]
            lines.append(f"**睡眠**: 累计约 {total:.1f} 小时")

        # 卡路里
        if "calories" in metrics:
            cal = metrics["calories"]
            total = cal["avg"] * cal["count"]
            lines.append(f"**消耗卡路里**: 约 {total:.0f} kcal")

        # 预警
        if alerts:
            lines.append("")
            lines.append("## 预警")
            for alert in alerts:
                icon = "严重" if alert["severity"] == "critical" else "注意"
                lines.append(f"- [{icon}] {alert['message']}")

        # 建议
        lines.append("")
        lines.append("## 健康建议")
        suggestions = self._generate_suggestions(metrics, alerts)
        for i, s in enumerate(suggestions, 1):
            lines.append(f"{i}. {s}")

        lines.append("")
        lines.append(f"*报告生成时间: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC*")

        return "\n".join(lines)

    def _generate_suggestions(
        self,
        metrics: Dict[str, Any],
        alerts: List[Dict[str, Any]],
    ) -> List[str]:
        """基于数据生成健康建议"""
        suggestions = []

        if "activity_level" in metrics:
            al = metrics["activity_level"]
            if al["avg"] > 7:
                suggestions.append("今日活动量较高，注意补充水分，避免过度疲劳")
            elif al["avg"] < 2:
                suggestions.append("今日活动量偏少，建议适当增加互动和遛弯时间")

        if "steps" in metrics:
            st = metrics["steps"]
            total = st["avg"] * st["count"]
            if total < 2000:
                suggestions.append("步数较少，建议增加户外活动时间")

        if "heart_rate" in metrics:
            hr = metrics["heart_rate"]
            if hr["avg"] > 130:
                suggestions.append("心率持续偏高，建议保持安静环境，如持续请咨询兽医")

        if "temperature" in metrics:
            temp = metrics["temperature"]
            if temp["max"] > 39.2:
                suggestions.append("体温偏高，请注意是否有其他异常症状，必要时就医")

        if alerts:
            suggestions.append("存在预警项，请密切关注相关指标变化")

        if not suggestions:
            suggestions = [
                "各项指标正常，继续保持当前的健康管理方式",
                "建议保持规律的饮食和运动习惯",
            ]

        return suggestions

    async def generate_daily_report_llm(
        self,
        pet_name: str,
        collected_data: Dict[str, Any],
    ) -> str:
        """
        使用 LLM 生成日报（异步）
        如果 LLM 不可用则降级为模板化报告
        """
        try:
            from src.core.llm import get_llm
            llm = get_llm()

            context = self.build_report_context(pet_name, collected_data)
            prompt = f"""你是一位专业的宠物健康顾问。请根据以下宠物健康数据，生成一份简洁的日报。

要求：
1. 用中文写，格式为 Markdown
2. 包含「今日总览」「指标详情」「健康建议」三个部分
3. 语言温暖但专业，面向宠物主人
4. 如果有预警项请突出提醒
5. 字数控制在300字以内

{context}

请生成日报："""

            result = await llm.ainvoke(prompt)
            return result.content if hasattr(result, "content") else str(result)

        except Exception as e:
            logger.warning(f"LLM 日报生成失败，降级为模板报告: {e}")
            return self.generate_template_report(pet_name, collected_data)


def get_report_service() -> ReportService:
    return ReportService()