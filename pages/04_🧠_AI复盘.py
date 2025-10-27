"""
页面4：AI自动复盘
"""
import streamlit as st
import pandas as pd
from modules.charts import ChartGenerator

st.title("🧠 AI自动复盘")

if not st.session_state.get('data_loaded'):
    st.warning("请先在主页配置API Key")
    st.stop()

df = st.session_state.daily_df.copy()
ai_engine = st.session_state.ai_engine

# 选择复盘周期
st.markdown("### 📅 选择复盘周期")

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input(
        "开始日期",
        value=df['date'].min().date()
    )
with col2:
    end_date = st.date_input(
        "结束日期",
        value=df['date'].max().date()
    )

# 生成复盘报告
if st.button("🤖 生成AI复盘报告", type="primary", use_container_width=True):
    with st.spinner("AI生成复盘报告中..."):
        # 筛选周期数据
        period_df = df[
            (df['date'] >= pd.to_datetime(start_date)) &
            (df['date'] <= pd.to_datetime(end_date))
        ]

        if len(period_df) == 0:
            st.error("所选周期内无数据")
            st.stop()

        try:
            # 调用AI生成报告
            report = ai_engine.generate_report(
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d'),
                period_df
            )

            # 保存报告
            st.session_state.current_report = report
            st.session_state.current_period_df = period_df

            st.success("✅ 复盘报告生成完成！")

        except Exception as e:
            st.error(f"❌ AI生成失败: {str(e)}")
            st.info("生成基础报告...")

            # 计算关键指标
            total_revenue = period_df['revenue'].sum()
            avg_arpu = period_df['arpu'].mean()
            arpu_change = (period_df['arpu'].iloc[-1] - period_df['arpu'].iloc[0]) / period_df['arpu'].iloc[0] * 100 if len(period_df) > 0 else 0

            # 使用降级方案
            content_perf = period_df.groupby('content_type').agg({
                'revenue': 'sum',
                'arpu': 'mean'
            }).sort_values('revenue', ascending=False)

            report = ai_engine._get_default_report(total_revenue, avg_arpu, arpu_change, content_perf)
            st.session_state.current_report = report
            st.session_state.current_period_df = period_df

# 展示报告
if 'current_report' in st.session_state:
    report = st.session_state.current_report
    period_df = st.session_state.current_period_df

    st.markdown("---")

    # 使用tabs分隔不同部分
    tab1, tab2, tab3 = st.tabs(["📊 完整报告", "🎯 执行模板", "📈 数据可视化"])

    with tab1:
        st.markdown(report)

    with tab2:
        st.markdown("### 🎯 策略执行模板（可直接复用）")
        st.info("💡 此模板提取自复盘报告，可直接用于下期活动策划")

        # 提取执行模板部分
        if "## 🎯 策略执行模板" in report:
            template_start = report.find("## 🎯 策略执行模板")
            template_end = report.find("## 💡 下期优化建议", template_start)
            if template_end == -1:
                template_end = len(report)

            template_section = report[template_start:template_end]
            st.markdown(template_section)

            # 提供复制按钮
            st.download_button(
                label="📋 下载执行模板",
                data=template_section,
                file_name=f"策略执行模板_{pd.Timestamp.now().strftime('%Y%m%d')}.md",
                mime="text/markdown",
                use_container_width=True,
                key="download_template"
            )
        else:
            st.warning("当前报告未包含执行模板，请重新生成报告")

    with tab3:
        # 策略ROI排行
        content_perf = period_df.groupby('content_type').agg({
            'revenue': 'sum',
            'arpu': 'mean',
            'dau': 'sum'
        }).reset_index()

        content_perf['roi'] = content_perf['revenue'] / (content_perf['dau'] * 0.05)  # 假设成本
        content_perf = content_perf.sort_values('roi', ascending=False)

        st.markdown("#### 内容类型ROI排行")

        # 使用Plotly创建ROI柱状图
        import plotly.graph_objects as go

        fig_content = go.Figure()

        # 添加ROI柱状图
        fig_content.add_trace(go.Bar(
            x=content_perf['content_type'],
            y=content_perf['roi'],
            marker=dict(
                color=content_perf['roi'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="ROI")
            ),
            text=content_perf['roi'].apply(lambda x: f'{x:.2f}'),
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>' +
                          'ROI: %{y:.2f}<br>' +
                          '<extra></extra>'
        ))

        fig_content.update_layout(
            title='内容类型ROI对比',
            xaxis_title='内容类型',
            yaxis_title='ROI',
            height=400,
            template='plotly_white',
            showlegend=False
        )

        st.plotly_chart(fig_content, use_container_width=True)

        # 显示详细数据表
        with st.expander("📊 查看详细数据"):
            st.dataframe(
                content_perf,
                use_container_width=True,
                column_config={
                    'content_type': '内容类型',
                    'revenue': st.column_config.NumberColumn('收入', format="¥%d"),
                    'arpu': st.column_config.NumberColumn('平均边现', format="%.4f"),
                    'dau': st.column_config.NumberColumn('DAU', format="%d"),
                    'roi': st.column_config.NumberColumn('ROI', format="%.2f")
                }
            )

        # 趋势图
        st.markdown("#### 活动期间边现趋势")
        chart_gen = ChartGenerator()
        start_date_str = period_df['date'].min().strftime('%Y-%m-%d')
        end_date_str = period_df['date'].max().strftime('%Y-%m-%d')
        fig = chart_gen.create_trend_chart(period_df, 'arpu', f'活动期间边现趋势 ({start_date_str} - {end_date_str})')
        st.plotly_chart(fig, use_container_width=True)

    # 下载按钮区域
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="📥 下载完整复盘报告",
            data=report,
            file_name=f"复盘报告_{period_df['date'].min().strftime('%Y%m%d')}_{period_df['date'].max().strftime('%Y%m%d')}.md",
            mime="text/markdown",
            use_container_width=True,
            key="download_full_report"
        )

    with col2:
        # 提取执行模板用于单独下载
        if "## 🎯 策略执行模板" in report:
            template_start = report.find("## 🎯 策略执行模板")
            template_end = report.find("## 💡 下期优化建议", template_start)
            if template_end == -1:
                template_end = len(report)
            template_only = report[template_start:template_end]

            st.download_button(
                label="📋 下载执行模板（精简版）",
                data=template_only,
                file_name=f"策略执行模板_{pd.Timestamp.now().strftime('%Y%m%d')}.md",
                mime="text/markdown",
                use_container_width=True,
                key="download_template_only"
            )

# 历史复盘查看
st.markdown("---")
st.markdown("### 📚 历史复盘记录")

campaigns = st.session_state.campaigns_df.copy()

# 显示历史活动列表
# 格式化显示数据
display_campaigns = campaigns[['campaign_id', 'start_date', 'end_date', 'strategy_tag', 'roi', 'arpu_lift']].copy()
display_campaigns['start_date'] = display_campaigns['start_date'].dt.strftime('%Y-%m-%d')
display_campaigns['end_date'] = display_campaigns['end_date'].dt.strftime('%Y-%m-%d')

st.dataframe(
    display_campaigns,
    use_container_width=True,
    column_config={
        'campaign_id': '活动ID',
        'start_date': '开始日期',
        'end_date': '结束日期',
        'strategy_tag': '策略标签',
        'roi': st.column_config.NumberColumn('ROI', format="%.2f"),
        'arpu_lift': '边现提升'
    }
)

# ROI排行榜
chart_gen = ChartGenerator()
fig_roi = chart_gen.create_roi_ranking(campaigns)
st.plotly_chart(fig_roi, use_container_width=True)

st.success("✅ 复盘完成！接下来可前往 **📚 经验库** 页面查询相似活动")
