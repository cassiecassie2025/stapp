"""
数据加载模块
"""
import pandas as pd
import os
from utils.config import Config


class DataLoader:
    """数据加载器"""

    def __init__(self, data_path: str = None):
        self.data_path = data_path or Config.DATA_PATH

    def load_daily_metrics(self) -> pd.DataFrame:
        """加载日报数据并计算衍生指标"""
        df = pd.read_csv(os.path.join(self.data_path, 'daily_metrics.csv'))
        df['date'] = pd.to_datetime(df['date'])

        # 计算基础指标
        df['arpu'] = df['revenue'] / df['dau']
        df['arpu_change'] = df['arpu'].pct_change() * 100
        df['dau_change'] = df['dau'].pct_change() * 100
        df['revenue_change'] = df['revenue'].pct_change() * 100
        df['conversion_rate'] = (df['new_members'] + df['renew_members']) / df['dau'] * 100

        # 计算异常检测用指标
        df['arpu_ma7'] = df['arpu'].rolling(window=7, min_periods=1).mean()
        df['arpu_std7'] = df['arpu'].rolling(window=7, min_periods=1).std()

        # 处理NaN值
        df = df.fillna({
            'arpu_change': 0,
            'dau_change': 0,
            'revenue_change': 0,
            'arpu_std7': df['arpu'].std()
        })

        return df

    def load_user_segments(self) -> pd.DataFrame:
        """加载用户分层数据"""
        df = pd.read_csv(os.path.join(self.data_path, 'user_segments.csv'))
        return df

    def load_campaign_history(self) -> pd.DataFrame:
        """加载历史活动数据"""
        df = pd.read_csv(os.path.join(self.data_path, 'campaign_history.csv'))
        df['start_date'] = pd.to_datetime(df['start_date'])
        df['end_date'] = pd.to_datetime(df['end_date'])
        return df

    def load_resource_capacity(self) -> pd.DataFrame:
        """加载资源位容量数据"""
        df = pd.read_csv(os.path.join(self.data_path, 'resource_capacity.csv'))
        return df

    def get_latest_metrics(self, df: pd.DataFrame) -> dict:
        """获取最新的指标摘要"""
        if len(df) == 0:
            return {}

        latest = df.iloc[-1]
        return {
            'date': latest['date'],
            'dau': latest['dau'],
            'revenue': latest['revenue'],
            'arpu': latest['arpu'],
            'dau_change': latest.get('dau_change', 0),
            'revenue_change': latest.get('revenue_change', 0),
            'arpu_change': latest.get('arpu_change', 0),
            'conversion_rate': latest.get('conversion_rate', 0)
        }
