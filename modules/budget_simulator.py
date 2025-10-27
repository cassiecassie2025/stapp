"""
预算模拟器模块
"""
import pandas as pd


class BudgetSimulator:
    """预算模拟器"""

    def __init__(self, baseline_arpu: float = 0.092):
        self.baseline_arpu = baseline_arpu

    def simulate(self, content_ratio: dict, resource_usage: dict,
                 capacity_df: pd.DataFrame) -> dict:
        """
        模拟预算和边现

        Args:
            content_ratio: 内容配比 {'家庭剧': 70, '动漫': 20, '综艺': 10}
            resource_usage: 资源位使用率 {'首页位1': 0.6, '首页位3': 0.5}
            capacity_df: 资源位容量表

        Returns:
            模拟结果字典
        """
        # 1. 计算内容效应（基于配比）
        content_effect = 1.0
        if content_ratio.get('家庭剧', 0) > 60:
            content_effect += 0.10  # 家庭剧提升10%
        if content_ratio.get('动漫', 0) > 30:
            content_effect += 0.05  # 动漫提升5%

        # 2. 计算资源位效应
        resource_effect = 1.0
        for pos, usage in resource_usage.items():
            capacity_row = capacity_df[capacity_df['resource_position'] == pos]
            if len(capacity_row) > 0:
                elasticity = capacity_row.iloc[0]['elasticity']
                resource_effect += usage * elasticity

        # 3. 容量惩罚
        capacity_penalty = 1.0
        for pos, usage in resource_usage.items():
            capacity_row = capacity_df[capacity_df['resource_position'] == pos]
            if len(capacity_row) > 0:
                max_capacity = capacity_row.iloc[0]['max_capacity']
                if usage > max_capacity * 0.8:
                    capacity_penalty = 0.85  # 超容量惩罚

        # 4. 综合效应
        estimated_arpu = self.baseline_arpu * content_effect * resource_effect * capacity_penalty

        # 5. 计算预算
        total_cost = 0
        for pos, usage in resource_usage.items():
            capacity_row = capacity_df[capacity_df['resource_position'] == pos]
            if len(capacity_row) > 0:
                cost_per_10k = capacity_row.iloc[0]['cost_per_10k']
                # 假设DAU 470万
                total_cost += (4700000 / 10000) * usage * cost_per_10k

        # 6. 计算ROI
        estimated_revenue = estimated_arpu * 4700000 * 7  # 假设7天活动
        roi = estimated_revenue / total_cost if total_cost > 0 else 0

        return {
            'estimated_arpu': estimated_arpu,
            'arpu_lift': estimated_arpu - self.baseline_arpu,
            'arpu_lift_pct': (estimated_arpu - self.baseline_arpu) / self.baseline_arpu * 100,
            'total_cost': total_cost,
            'estimated_revenue': estimated_revenue,
            'roi': roi,
            'capacity_warning': capacity_penalty < 1.0
        }
