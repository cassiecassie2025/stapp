"""
数据生成脚本 - 生成4个CSV模拟数据文件
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 固定随机种子（确保异常点可复现）
np.random.seed(42)

def generate_daily_metrics(days=30):
    """生成日报数据"""
    dates = pd.date_range(end=datetime.now(), periods=days)

    daily_data = []
    for i, date in enumerate(dates):
        # 周期性波动
        base_dau = 4700000
        weekend_boost = 200000 if date.dayofweek >= 5 else 0
        random_factor = np.random.randint(-100000, 150000)
        dau = base_dau + weekend_boost + random_factor

        # 边现模拟
        base_arpu = 0.092
        content_boost = np.random.choice([0.005, 0.008, -0.003], p=[0.4, 0.3, 0.3])
        arpu = base_arpu + content_boost + np.random.normal(0, 0.002)

        # 人工注入异常点（固定日期，便于演示）
        if i in [5, 12, 21]:  # 第6天、第13天、第22天
            arpu *= 0.85  # 下降15%

        revenue = int(dau * arpu)

        daily_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'dau': dau,
            'revenue': revenue,
            'new_members': np.random.randint(18000, 25000),
            'renew_members': np.random.randint(58000, 68000),
            'content_type': np.random.choice(['家庭剧', '动漫', '综艺'], p=[0.5, 0.3, 0.2]),
            'platform': 'TV',
            'resource_position': np.random.choice(['首页位1', '首页位3', '详情页推荐']),
            'discount_type': np.random.choice(['10元券', '5折月卡', '免费试看']),
            'is_holiday': 1 if date.dayofweek >= 5 else 0,
            'day_of_week': date.dayofweek
        })

    return pd.DataFrame(daily_data)


def generate_user_segments():
    """生成用户分层数据"""
    segments_data = [
        {
            'segment': '家庭向高活跃',
            'active_level': 'high',
            'membership_status': 'non_member',
            'size': 860000,
            'content_preference': '家庭剧',
            'avg_watch_time': 180,
            'price_sensitivity': 'low',
            'historical_cvr': 0.185,
            'avg_arpu_contribution': 0.012
        },
        {
            'segment': '动漫偏好沉默',
            'active_level': 'low',
            'membership_status': 'expired',
            'size': 230000,
            'content_preference': '动漫',
            'avg_watch_time': 45,
            'price_sensitivity': 'high',
            'historical_cvr': 0.082,
            'avg_arpu_contribution': 0.005
        },
        {
            'segment': '轻活跃用户',
            'active_level': 'medium',
            'membership_status': 'member',
            'size': 450000,
            'content_preference': '综艺',
            'avg_watch_time': 90,
            'price_sensitivity': 'medium',
            'historical_cvr': 0.145,
            'avg_arpu_contribution': 0.009
        },
        {
            'segment': '家庭剧铁粉',
            'active_level': 'high',
            'membership_status': 'member',
            'size': 320000,
            'content_preference': '家庭剧',
            'avg_watch_time': 240,
            'price_sensitivity': 'low',
            'historical_cvr': 0.220,
            'avg_arpu_contribution': 0.015
        },
        {
            'segment': '儿童动画家长',
            'active_level': 'medium',
            'membership_status': 'non_member',
            'size': 180000,
            'content_preference': '动漫',
            'avg_watch_time': 120,
            'price_sensitivity': 'medium',
            'historical_cvr': 0.165,
            'avg_arpu_contribution': 0.010
        },
        {
            'segment': '综艺轻度用户',
            'active_level': 'low',
            'membership_status': 'non_member',
            'size': 290000,
            'content_preference': '综艺',
            'avg_watch_time': 60,
            'price_sensitivity': 'high',
            'historical_cvr': 0.095,
            'avg_arpu_contribution': 0.006
        }
    ]

    return pd.DataFrame(segments_data)


def generate_campaign_history():
    """生成历史活动数据"""
    campaigns_data = [
        {
            'campaign_id': '2024Q4_VIP',
            'start_date': '2024-10-15',
            'end_date': '2024-10-21',
            'strategy_tag': '家庭剧促活',
            'target_segment': '家庭向高活跃',
            'content_mix': '家庭剧70%+动漫30%',
            'resource_positions': '首页位3+详情页',
            'discount': '10元券',
            'revenue_lift': '+18%',
            'arpu_lift': '+0.021',
            'roi': 1.34,
            'success_factors': '周五高峰+资源位权重高',
            'budget_used': 80,
            'resource_capacity': '首页位3:0.6,详情页:0.5'
        },
        {
            'campaign_id': '2025_SUMMER',
            'start_date': '2025-06-01',
            'end_date': '2025-06-05',
            'strategy_tag': '动漫限免',
            'target_segment': '儿童动画家长',
            'content_mix': '动漫80%+综艺20%',
            'resource_positions': '首页位1',
            'discount': '免费试看',
            'revenue_lift': '+12%',
            'arpu_lift': '+0.015',
            'roi': 1.12,
            'success_factors': '儿童节热点+内容匹配',
            'budget_used': 50,
            'resource_capacity': '首页位1:0.7'
        },
        {
            'campaign_id': '2024_NATIONAL',
            'start_date': '2024-10-01',
            'end_date': '2024-10-07',
            'strategy_tag': '国庆促活',
            'target_segment': '全用户',
            'content_mix': '家庭剧50%+综艺30%+动漫20%',
            'resource_positions': '首页位1+位3',
            'discount': '5折月卡',
            'revenue_lift': '+22%',
            'arpu_lift': '+0.025',
            'roi': 1.45,
            'success_factors': '长假档期+多内容组合',
            'budget_used': 120,
            'resource_capacity': '首页位1:0.8,首页位3:0.7'
        },
        {
            'campaign_id': '2024_SPRING',
            'start_date': '2024-03-08',
            'end_date': '2024-03-14',
            'strategy_tag': '女性向促活',
            'target_segment': '家庭剧铁粉',
            'content_mix': '家庭剧90%+综艺10%',
            'resource_positions': '首页位1+详情页',
            'discount': '10元券',
            'revenue_lift': '+16%',
            'arpu_lift': '+0.018',
            'roi': 1.28,
            'success_factors': '节日营销+精准人群',
            'budget_used': 65,
            'resource_capacity': '首页位1:0.5,详情页:0.4'
        },
        {
            'campaign_id': '2024_ANIME_FEST',
            'start_date': '2024-07-20',
            'end_date': '2024-07-26',
            'strategy_tag': '动漫狂欢',
            'target_segment': '动漫偏好沉默',
            'content_mix': '动漫100%',
            'resource_positions': '首页位3+详情页',
            'discount': '5折月卡',
            'revenue_lift': '+10%',
            'arpu_lift': '+0.012',
            'roi': 0.98,
            'success_factors': '暑期档+IP联动',
            'budget_used': 45,
            'resource_capacity': '首页位3:0.5,详情页:0.6'
        },
        {
            'campaign_id': '2024_VARIETY_WEEK',
            'start_date': '2024-09-10',
            'end_date': '2024-09-16',
            'strategy_tag': '综艺专场',
            'target_segment': '综艺轻度用户',
            'content_mix': '综艺80%+家庭剧20%',
            'resource_positions': '详情页推荐',
            'discount': '免费试看',
            'revenue_lift': '+8%',
            'arpu_lift': '+0.010',
            'roi': 1.05,
            'success_factors': '新综艺上线+口碑传播',
            'budget_used': 30,
            'resource_capacity': '详情页:0.3'
        }
    ]

    return pd.DataFrame(campaigns_data)


def generate_resource_capacity():
    """生成资源位容量表"""
    capacity_data = [
        {
            'resource_position': '首页位1',
            'max_capacity': 0.8,
            'cost_per_10k': 150,
            'elasticity': 0.12
        },
        {
            'resource_position': '首页位3',
            'max_capacity': 0.7,
            'cost_per_10k': 100,
            'elasticity': 0.10
        },
        {
            'resource_position': '详情页推荐',
            'max_capacity': 0.6,
            'cost_per_10k': 60,
            'elasticity': 0.08
        }
    ]

    return pd.DataFrame(capacity_data)


def main():
    """主函数：生成所有CSV文件"""
    # 切换到项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    # 确保data目录存在
    os.makedirs('data', exist_ok=True)

    # 1. 生成日报数据
    daily_df = generate_daily_metrics(30)
    daily_df.to_csv('data/daily_metrics.csv', index=False, encoding='utf-8-sig')
    print(f"✅ 生成日报数据: {len(daily_df)} 行")

    # 2. 生成用户分层
    segments_df = generate_user_segments()
    segments_df.to_csv('data/user_segments.csv', index=False, encoding='utf-8-sig')
    print(f"✅ 生成用户分层: {len(segments_df)} 行")

    # 3. 生成历史活动
    campaigns_df = generate_campaign_history()
    campaigns_df.to_csv('data/campaign_history.csv', index=False, encoding='utf-8-sig')
    print(f"✅ 生成历史活动: {len(campaigns_df)} 行")

    # 4. 生成资源位容量
    capacity_df = generate_resource_capacity()
    capacity_df.to_csv('data/resource_capacity.csv', index=False, encoding='utf-8-sig')
    print(f"✅ 生成资源位容量: {len(capacity_df)} 行")

    print("\n🎉 所有数据生成完成！")
    print(f"📁 数据文件位置: {os.path.join(project_root, 'data')}/")


if __name__ == '__main__':
    main()
