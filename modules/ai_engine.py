"""
AI引擎模块
"""
import openai
from typing import Dict
import pandas as pd
import json
import re
from utils.config import Config
from utils.validators import StrategyResponse
from loguru import logger


class AIStrategyEngine:
    """AI策略推荐引擎"""

    def __init__(self, api_key: str = None, model: str = None, base_url: str = None):
        """
        初始化AI引擎

        Args:
            api_key: API Key (支持 OpenAI/DeepSeek 等)
            model: 模型名称 (gpt-4o-mini/deepseek-chat等)
            base_url: API Base URL (DeepSeek: https://api.deepseek.com/v1)
        """
        api_key = api_key or Config.OPENAI_API_KEY
        self.model = model or Config.OPENAI_MODEL

        # 支持自定义 base_url（用于 DeepSeek 等兼容API）
        client_kwargs = {
            'api_key': api_key,
            'timeout': Config.OPENAI_TIMEOUT,
            'max_retries': Config.OPENAI_MAX_RETRIES
        }

        # 优先使用传入的 base_url，其次使用配置文件中的
        if base_url:
            client_kwargs['base_url'] = base_url
        elif Config.OPENAI_BASE_URL:
            client_kwargs['base_url'] = Config.OPENAI_BASE_URL

        self.client = openai.OpenAI(**client_kwargs)

        logger.info(f"AI引擎初始化完成 - 模型: {self.model}, Base URL: {client_kwargs.get('base_url', 'OpenAI默认')}")

    def recommend_strategy(self, target: str, history_df: pd.DataFrame,
                          segments_df: pd.DataFrame) -> Dict:
        """
        策略推荐核心逻辑

        Args:
            target: 运营目标描述
            history_df: 历史活动数据
            segments_df: 用户分层数据

        Returns:
            推荐策略字典
        """
        # 1. 召回相似历史案例
        similar_cases = history_df.nlargest(3, 'roi')[
            ['campaign_id', 'strategy_tag', 'roi', 'arpu_lift', 'success_factors']
        ]

        # 2. 构建prompt
        prompt = f"""你是会员运营AI助手,分析目标并推荐策略。

【运营目标】
{target}

【历史成功案例TOP3】
{similar_cases.to_string()}

【可用用户分层】
{segments_df[['segment', 'size', 'content_preference', 'price_sensitivity']].to_string()}

请输出JSON格式推荐方案:
{{
  "target_segment": "推荐人群(选择最匹配的segment)",
  "estimated_size": "预估触达人数",
  "content_strategy": {{
    "primary_content": "主推内容类型",
    "content_ratio": "内容配比(如家庭剧70%+动漫30%)",
    "reason": "为什么选择这个组合"
  }},
  "resource_allocation": {{
    "positions": ["资源位列表"],
    "peak_hours": "最佳投放时段",
    "budget_focus": "预算重点分配"
  }},
  "discount_recommendation": "优惠策略(命名格式：会员类型+VIP+连包/连月/连季+面额+券-平台名,如:影视VIP连月10元券-优爱腾)",
  "kpi_forecast": {{
    "arpu_lift": "预估边现提升(元)",
    "confidence": "置信度(0-100)",
    "roi_estimate": "预估ROI"
  }},
  "risk_alert": "风险提示字符串(多条用换行分隔,不要用数组)",
  "historical_reference": "参考的历史活动ID"
}}

注意：
1. 只输出JSON，不要其他文字
2. risk_alert必须是字符串，不要用数组格式
3. discount_recommendation使用真实券名格式"""

        try:
            # 3. 调用GPT
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            # 4. 解析并校验
            return self._parse_strategy_safe(response.choices[0].message.content)

        except Exception as e:
            logger.warning(f"AI调用失败，使用降级方案: {e}")
            return self._get_default_strategy()

    def explain_anomaly(self, date: str, metrics: Dict,
                       context_df: pd.DataFrame) -> str:
        """
        异常解释模块

        Args:
            date: 异常日期
            metrics: 指标字典
            context_df: 上下文数据

        Returns:
            Markdown格式分析报告
        """
        # 获取前后3天数据作为上下文
        target_date = pd.to_datetime(date)
        context = context_df[
            (context_df['date'] >= target_date - pd.Timedelta(days=3)) &
            (context_df['date'] <= target_date + pd.Timedelta(days=3))
        ]

        prompt = f"""你是数据分析专家,解释会员数据异常。

【异常日期】{date}

【关键指标】
- DAU: {metrics.get('dau', 0):,.0f} (环比变化: {metrics.get('dau_change', 0):.1f}%)
- 会员收入: {metrics.get('revenue', 0):,.0f}元 (环比变化: {metrics.get('revenue_change', 0):.1f}%)
- 单DAU边现: {metrics.get('arpu', 0):.4f}元 (环比变化: {metrics.get('arpu_change', 0):.1f}%)
- 转化率: {metrics.get('conversion_rate', 0):.2f}%

【上下文数据】
{context[['date', 'dau', 'revenue', 'arpu', 'content_type']].to_string()}

请分析并输出（Markdown格式）:

### 核心原因
1. [最多3条,按影响程度排序,每条不超过30字]

### 数据洞察
[发现的规律或趋势,50字以内]

### 行动建议
1. [2条可执行措施,每条不超过30字]

要求:简洁、具体、可执行。"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.warning(f"AI异常解释失败: {e}")
            return self._get_default_anomaly_explanation(metrics)

    def generate_report(self, start_date: str, end_date: str,
                       period_df: pd.DataFrame) -> str:
        """
        AI复盘报告生成

        Args:
            start_date: 开始日期
            end_date: 结束日期
            period_df: 周期数据

        Returns:
            Markdown格式复盘报告
        """
        # 计算关键指标
        total_revenue = period_df['revenue'].sum()
        avg_arpu = period_df['arpu'].mean()
        arpu_change = (period_df['arpu'].iloc[-1] - period_df['arpu'].iloc[0]) / period_df['arpu'].iloc[0] * 100 if len(period_df) > 0 else 0

        # 内容分析
        content_performance = period_df.groupby('content_type').agg({
            'revenue': 'sum',
            'arpu': 'mean'
        }).sort_values('revenue', ascending=False)

        prompt = f"""你是运营复盘专家,生成详细的活动总结报告。

【活动周期】{start_date} 至 {end_date}

【整体表现】
- 总收入: {total_revenue:,.0f}元
- 平均边现: {avg_arpu:.4f}元
- 边现变化: {arpu_change:+.1f}%

【内容表现】
{content_performance.to_string()}

【日度数据】
{period_df[['date', 'dau', 'revenue', 'arpu', 'content_type']].to_string()}

请生成Markdown格式复盘报告,包含:

## 📊 活动总结

### 核心成果
- [3个关键数据亮点,带具体数字]

### 驱动因素分析
- [最成功的内容策略(数据支撑)]
- [关键转折点分析]

### 待优化项
- [2个需改进的方面]

## 🎯 策略执行模板（可复用）

### 目标人群
[基于数据推荐最优人群,带人群规模]

### 内容策略
[最优内容组合比例,如: XX%+XX%+XX%]

### 资源位配置
[推荐的资源位组合]

### 优惠方案
[推荐的优惠券，命名格式：会员类型+VIP+连包/连月/连季+面额+券-平台名，如：影视VIP连季10元券-优爱腾、亲子VIP5元券]

### KPI目标
- 边现提升: [预期提升值]
- ROI: [预期ROI值]

### 行动清单
- [ ] [具体执行步骤1]
- [ ] [具体执行步骤2]
- [ ] [具体执行步骤3]
- [ ] [具体执行步骤4]

### 风险点与建议
[关键风险提示和规避建议]

## 💡 下期优化建议
1. [可执行的优化措施1]
2. [可执行的优化措施2]
3. [可执行的优化措施3]

## 📝 策略沉淀
[可复用的经验总结,用于后续相似场景]

要求:数据驱动、洞察深刻、建议具体、可直接复用。"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.warning(f"AI复盘生成失败: {e}")
            return self._get_default_report(total_revenue, avg_arpu, arpu_change, content_performance)

    def _parse_strategy_safe(self, response_text: str) -> Dict:
        """三层防护解析"""
        try:
            # 提取JSON代码块
            json_str = self._extract_json_block(response_text)
            data = json.loads(json_str)

            # 预处理：将list转换为string（AI有时会返回list格式）
            if isinstance(data.get('risk_alert'), list):
                data['risk_alert'] = '\n'.join(str(item) for item in data['risk_alert'])
                logger.info("已将risk_alert从list转换为string")

            # Pydantic校验
            validated = StrategyResponse(**data)
            return validated.model_dump()

        except Exception as e:
            logger.warning(f"解析失败: {e}")
            # 尝试直接解析
            try:
                data = json.loads(response_text)
                # 同样的预处理
                if isinstance(data.get('risk_alert'), list):
                    data['risk_alert'] = '\n'.join(str(item) for item in data['risk_alert'])
                return data
            except:
                raise ValueError("无法解析AI响应")

    def _extract_json_block(self, text: str) -> str:
        """提取JSON代码块"""
        # 尝试提取```json```代码块
        match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            return match.group(1)

        # 尝试提取{}
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return match.group(0)

        return text

    def _get_default_strategy(self) -> Dict:
        """降级默认策略"""
        return {
            "target_segment": "家庭向高活跃",
            "estimated_size": "86万",
            "content_strategy": {
                "primary_content": "家庭剧",
                "content_ratio": "家庭剧70%+动漫20%+综艺10%",
                "reason": "基于历史最佳ROI活动"
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

    def _get_default_anomaly_explanation(self, metrics: Dict) -> str:
        """降级异常解释"""
        return f"""### 核心原因
1. 单DAU边现环比变化{metrics.get('arpu_change', 0):.1f}%
2. 建议查看当日内容策略和资源位配置

### 数据洞察
指标出现异常波动，需进一步分析用户行为数据

### 行动建议
1. 检查当日运营活动是否有变化
2. 对比历史同期数据找规律
"""

    def _get_default_report(self, total_revenue, avg_arpu, arpu_change, content_perf) -> str:
        """降级复盘报告"""
        top_content = content_perf.index[0] if len(content_perf) > 0 else "家庭剧"
        top_revenue = content_perf.iloc[0]['revenue'] if len(content_perf) > 0 else 0

        return f"""## 📊 活动总结

### 核心成果
- 总收入: {total_revenue:,.0f}元，平均边现: {avg_arpu:.4f}元
- 边现变化: {arpu_change:+.1f}%，整体呈上升趋势
- {top_content}内容表现最佳，贡献收入{top_revenue:,.0f}元

### 驱动因素分析
- 主要内容类型贡献度较高，内容策略有效
- 整体运营策略执行到位，用户响应积极

### 待优化项
- 需继续优化内容配比，提升用户体验
- 关注转化率提升，加强精准营销

## 🎯 策略执行模板（可复用）

### 目标人群
家庭向高活跃用户 - 约86万

### 内容策略
{top_content}70% + 综艺20% + 动漫10%

### 资源位配置
首页位3个 + 详情页推荐位

### 优惠方案
影视VIP连月10元券-优爱腾（适度优惠力度）

### KPI目标
- 边现提升: +0.015元以上
- ROI: 1.25以上

### 行动清单
- [ ] 配置内容推荐池（优先{top_content}）
- [ ] 申请资源位排期
- [ ] 设置优惠券发放规则
- [ ] 配置监控大盘和预警

### 风险点与建议
建议活动周期至少7天，以便观察完整用户行为周期

## 💡 下期优化建议
1. 延续当前有效策略，继续聚焦高活跃人群
2. 加大优质内容投入，提升用户满意度
3. 优化资源位配置，提高曝光转化效率

## 📝 策略沉淀
基于数据持续迭代优化，{top_content}内容策略可复用至类似场景
"""
