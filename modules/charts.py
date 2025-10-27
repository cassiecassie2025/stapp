"""
图表生成模块
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd


class ChartGenerator:
    """图表生成器"""

    @staticmethod
    def create_trend_chart(df: pd.DataFrame, metric: str, title: str):
        """创建趋势图"""
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df[metric],
            mode='lines+markers',
            name=title,
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=6)
        ))

        # 添加移动平均线
        if f'{metric}_ma7' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df[f'{metric}_ma7'],
                mode='lines',
                name='7日均线',
                line=dict(color='#ff7f0e', width=1, dash='dash'),
                opacity=0.6
            ))

        fig.update_layout(
            title=title,
            xaxis_title='日期',
            yaxis_title=metric,
            hovermode='x unified',
            height=400,
            template='plotly_white'
        )

        return fig

    @staticmethod
    def create_multi_metric_dashboard(df: pd.DataFrame):
        """创建多指标监控面板"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('DAU趋势', '会员收入', '单DAU边现', '转化率'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )

        # DAU
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['dau'], name='DAU',
                      line=dict(color='#2ca02c')),
            row=1, col=1
        )

        # 收入
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['revenue'], name='收入',
                      line=dict(color='#d62728')),
            row=1, col=2
        )

        # 边现
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['arpu'], name='边现',
                      line=dict(color='#9467bd')),
            row=2, col=1
        )

        # 转化率
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['conversion_rate'], name='转化率',
                      line=dict(color='#8c564b')),
            row=2, col=2
        )

        fig.update_layout(
            height=600,
            showlegend=False,
            hovermode='x unified',
            template='plotly_white'
        )

        return fig

    @staticmethod
    def create_anomaly_highlight(df: pd.DataFrame, anomaly_dates: list):
        """异常检测标注图"""
        fig = go.Figure()

        # 正常数据
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['arpu'],
            mode='lines+markers',
            name='边现趋势',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=5)
        ))

        # 移动平均线
        if 'arpu_ma7' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['arpu_ma7'],
                mode='lines',
                name='7日均线',
                line=dict(color='#ff7f0e', width=1, dash='dash'),
                opacity=0.5
            ))

        # 异常点标注
        if anomaly_dates:
            anomaly_df = df[df['date'].isin(pd.to_datetime(anomaly_dates))]
            if len(anomaly_df) > 0:
                fig.add_trace(go.Scatter(
                    x=anomaly_df['date'],
                    y=anomaly_df['arpu'],
                    mode='markers',
                    name='异常检测',
                    marker=dict(
                        size=14,
                        color='red',
                        symbol='x',
                        line=dict(width=2)
                    )
                ))

        fig.update_layout(
            title='边现异常检测',
            xaxis_title='日期',
            yaxis_title='单DAU边现',
            hovermode='x unified',
            height=450,
            template='plotly_white'
        )

        return fig

    @staticmethod
    def create_strategy_simulator(content_ratio: dict, arpu_baseline: float):
        """策略模拟器可视化"""
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('内容配比', '预估边现提升'),
            specs=[[{"type": "pie"}, {"type": "bar"}]]
        )

        # 饼图 - 内容配比
        fig.add_trace(
            go.Pie(
                labels=list(content_ratio.keys()),
                values=list(content_ratio.values()),
                hole=0.3,
                marker=dict(colors=px.colors.qualitative.Set3)
            ),
            row=1, col=1
        )

        # 边现预测柱状图
        scenarios = ['当前', '调整后', '最优']
        arpu_values = [arpu_baseline, arpu_baseline * 1.15, arpu_baseline * 1.25]

        fig.add_trace(
            go.Bar(
                x=scenarios,
                y=arpu_values,
                marker_color=['#1f77b4', '#ff7f0e', '#2ca02c'],
                text=[f'{v:.4f}' for v in arpu_values],
                textposition='auto'
            ),
            row=1, col=2
        )

        fig.update_layout(
            height=350,
            showlegend=False,
            template='plotly_white'
        )

        return fig

    @staticmethod
    def create_roi_ranking(campaigns_df: pd.DataFrame):
        """ROI排行榜"""
        # 按ROI排序
        sorted_df = campaigns_df.sort_values('roi', ascending=True).tail(5)

        fig = go.Figure(go.Bar(
            x=sorted_df['roi'],
            y=sorted_df['strategy_tag'],
            orientation='h',
            marker=dict(
                color=sorted_df['roi'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="ROI")
            ),
            text=sorted_df['roi'].apply(lambda x: f'{x:.2f}'),
            textposition='auto'
        ))

        fig.update_layout(
            title='历史活动ROI排行榜（TOP5）',
            xaxis_title='ROI',
            yaxis_title='策略',
            height=400,
            template='plotly_white'
        )

        return fig
