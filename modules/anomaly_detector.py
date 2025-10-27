"""
异常检测模块
"""
import pandas as pd
import numpy as np
from utils.config import Config


class AnomalyDetector:
    """异常检测器"""

    @staticmethod
    def detect_arpu_anomalies(df: pd.DataFrame, threshold: float = None):
        """
        智能异常检测（剔除日历效应）

        Args:
            df: 包含arpu, is_holiday的DataFrame
            threshold: Z-Score阈值（默认使用配置）

        Returns:
            异常点DataFrame
        """
        threshold = threshold or Config.ANOMALY_THRESHOLD

        # 1. 计算工作日/周末基线
        workday_mean = df[df['is_holiday'] == 0]['arpu'].mean() if len(df[df['is_holiday'] == 0]) > 0 else df['arpu'].mean()
        weekend_mean = df[df['is_holiday'] == 1]['arpu'].mean() if len(df[df['is_holiday'] == 1]) > 0 else df['arpu'].mean()

        # 2. 归一化处理（剔除日历效应）
        df['arpu_adjusted'] = df.apply(
            lambda row: row['arpu'] - (weekend_mean - workday_mean) if row['is_holiday'] else row['arpu'],
            axis=1
        )

        # 3. 滚动窗口Z-Score
        df['arpu_ma7'] = df['arpu_adjusted'].rolling(window=Config.ANOMALY_WINDOW, min_periods=1).mean()
        df['arpu_std7'] = df['arpu_adjusted'].rolling(window=Config.ANOMALY_WINDOW, min_periods=1).std()

        # 处理标准差为0的情况
        df['arpu_std7'] = df['arpu_std7'].replace(0, df['arpu'].std())

        df['arpu_zscore'] = (df['arpu_adjusted'] - df['arpu_ma7']) / df['arpu_std7']

        # 4. 多维度交叉验证（避免DAU突增导致的误判）
        if 'dau_change' not in df.columns:
            df['dau_change'] = df['dau'].pct_change() * 100

        is_anomaly = (
            (abs(df['arpu_zscore']) > threshold) &  # 边现异常
            (abs(df['dau_change']) < 30)            # DAU无剧烈波动
        )

        # 5. 分级
        df['anomaly_level'] = 'normal'
        df.loc[abs(df['arpu_zscore']) > 1.5, 'anomaly_level'] = '🟡 轻微'
        df.loc[abs(df['arpu_zscore']) > 2.0, 'anomaly_level'] = '🟠 中度'
        df.loc[abs(df['arpu_zscore']) > 2.5, 'anomaly_level'] = '🔴 严重'

        anomalies = df[is_anomaly].copy()

        if len(anomalies) > 0:
            return anomalies[['date', 'arpu', 'arpu_zscore', 'anomaly_level', 'dau', 'revenue']]
        else:
            return pd.DataFrame()

    @staticmethod
    def get_anomaly_dates(df: pd.DataFrame, threshold: float = None) -> list:
        """获取异常日期列表"""
        anomalies = AnomalyDetector.detect_arpu_anomalies(df, threshold)
        if len(anomalies) > 0:
            return anomalies['date'].tolist()
        return []
