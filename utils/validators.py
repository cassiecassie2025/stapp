"""
数据校验模块 - 使用Pydantic定义数据模型
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class ContentStrategy(BaseModel):
    """内容策略模型"""
    primary_content: str = Field(..., description="主推内容类型")
    content_ratio: str = Field(..., description="内容配比")
    reason: str = Field(..., description="选择理由")


class ResourceAllocation(BaseModel):
    """资源位分配模型"""
    positions: List[str] = Field(..., description="资源位列表")
    peak_hours: str = Field(..., description="最佳投放时段")
    budget_focus: str = Field(..., description="预算重点分配")


class KPIForecast(BaseModel):
    """KPI预测模型"""
    arpu_lift: str = Field(..., description="预估边现提升")
    confidence: str = Field(..., description="置信度(0-100)")
    roi_estimate: str = Field(..., description="预估ROI")


class StrategyResponse(BaseModel):
    """AI策略推荐响应模型"""
    target_segment: str = Field(..., description="推荐人群")
    estimated_size: str = Field(..., description="预估触达人数")
    content_strategy: ContentStrategy = Field(..., description="内容策略")
    resource_allocation: ResourceAllocation = Field(..., description="资源位配置")
    discount_recommendation: str = Field(..., description="优惠策略")
    kpi_forecast: KPIForecast = Field(..., description="KPI预测")
    risk_alert: str = Field(..., description="风险提示")
    historical_reference: str = Field(..., description="参考活动ID")

    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "target_segment": "家庭向高活跃",
                "estimated_size": "86万",
                "content_strategy": {
                    "primary_content": "家庭剧",
                    "content_ratio": "家庭剧70%+动漫30%",
                    "reason": "该人群对家庭剧偏好强烈"
                },
                "resource_allocation": {
                    "positions": ["首页位3", "详情页推荐"],
                    "peak_hours": "周五19-22点+周末全天",
                    "budget_focus": "70%投入首页位"
                },
                "discount_recommendation": "10元券",
                "kpi_forecast": {
                    "arpu_lift": "+0.019",
                    "confidence": "75",
                    "roi_estimate": "1.30"
                },
                "risk_alert": "建议延长活动周期至7天以上",
                "historical_reference": "2024Q4_VIP"
            }
        }
