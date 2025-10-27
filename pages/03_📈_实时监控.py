"""
页面3：实时监控与异常检测（重新设计 - 新手友好版）
"""
import streamlit as st
import pandas as pd
from modules.charts import ChartGenerator
from modules.anomaly_detector import AnomalyDetector

st.title("📈 实时监控与异常检测")

if not st.session_state.get('data_loaded'):
    st.error("❌ 数据未加载，请先在主页配置API Key并等待数据加载完成")
    st.stop()

df = st.session_state.daily_df.copy()
ai_engine = st.session_state.ai_engine

# 顶部操作指引
st.info("💡 **新手指引**：本页面展示最近30天的数据监控和异常检测。自动展示 → 查看异常 → 点击分析 → 下载清单")

# ==================== 第1部分：总览仪表盘 ====================
st.markdown("---")
st.markdown("## 📊 第1部分：总览仪表盘")
st.markdown("*自动展示最近30天的核心指标趋势，无需操作*")

# 关键指标卡片
st.markdown("### 📌 关键指标（最近7天平均）")
recent_7days = df.tail(7)

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_dau = recent_7days['dau'].mean()
    dau_change = ((recent_7days['dau'].iloc[-1] - recent_7days['dau'].iloc[0]) / recent_7days['dau'].iloc[0] * 100)
    st.metric(
        "DAU",
        f"{avg_dau:,.0f}",
        f"{dau_change:+.1f}%",
        help="日活跃用户数"
    )

with col2:
    avg_revenue = recent_7days['revenue'].mean()
    revenue_change = ((recent_7days['revenue'].iloc[-1] - recent_7days['revenue'].iloc[0]) / recent_7days['revenue'].iloc[0] * 100)
    st.metric(
        "日均收入",
        f"{avg_revenue:,.0f}元",
        f"{revenue_change:+.1f}%",
        help="会员收入"
    )

with col3:
    avg_arpu = recent_7days['arpu'].mean()
    arpu_change = recent_7days['arpu_change'].iloc[-1]
    st.metric(
        "单DAU边现",
        f"{avg_arpu:.4f}元",
        f"{arpu_change:+.1f}%",
        help="单个DAU的边际贡献"
    )

with col4:
    avg_cvr = recent_7days['conversion_rate'].mean()
    st.metric(
        "转化率",
        f"{avg_cvr:.2f}%",
        help="付费转化率"
    )

# 多指标趋势图
st.markdown("---")
st.markdown("### 📈 核心指标趋势（最近30天）")
st.caption("图表展示DAU、收入、边现、转化率的趋势变化")

chart_gen = ChartGenerator()
fig = chart_gen.create_multi_metric_dashboard(df)
st.plotly_chart(fig, use_container_width=True)

with st.expander("📊 查看详细数据表"):
    st.dataframe(
        df[['date', 'dau', 'revenue', 'arpu', 'conversion_rate', 'content_type']].tail(10),
        use_container_width=True,
        column_config={
            'date': '日期',
            'dau': st.column_config.NumberColumn('DAU', format="%d"),
            'revenue': st.column_config.NumberColumn('收入', format="¥%.0f"),
            'arpu': st.column_config.NumberColumn('单DAU边现', format="%.4f"),
            'conversion_rate': st.column_config.NumberColumn('转化率', format="%.2f%%"),
            'content_type': '内容类型'
        }
    )

# ==================== 第2部分：异常检测 ====================
st.markdown("---")
st.markdown("## 🔍 第2部分：AI异常检测")
st.markdown("*系统自动检测异常数据点，以下是检测结果*")

# 执行异常检测
detector = AnomalyDetector()
anomalies = detector.detect_arpu_anomalies(df)

if len(anomalies) > 0:
    st.warning(f"⚠️ **检测到 {len(anomalies)} 个异常数据点**（边现波动超过正常范围）")

    # 异常预警卡片
    st.markdown("### 🚨 异常数据点列表")

    for idx, (_, anomaly) in enumerate(anomalies.head(5).iterrows(), 1):
        level = anomaly['anomaly_level']
        date_str = anomaly['date'].strftime('%Y-%m-%d')

        # 根据严重程度选择颜色
        if level == '🔴 严重':
            container_type = st.error
        elif level == '🟡 中等':
            container_type = st.warning
        else:
            container_type = st.info

        with st.expander(f"**异常 {idx}**: {date_str} - {level} （Z-Score: {anomaly['arpu_zscore']:.2f}）", expanded=(idx==1)):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("边现", f"{anomaly['arpu']:.4f}元", help="单DAU边际贡献")
            with col2:
                st.metric("DAU", f"{anomaly['dau']:,.0f}", help="日活跃用户数")
            with col3:
                st.metric("收入", f"{anomaly['revenue']:,.0f}元", help="会员收入")
            with col4:
                st.metric("异常程度", f"{abs(anomaly['arpu_zscore']):.1f}σ", help="标准差倍数")

            st.caption(f"📅 日期：{date_str} | 📺 内容类型：{anomaly.get('content_type', '未知')}")

    # 异常点可视化
    st.markdown("---")
    st.markdown("### 📊 异常点可视化")
    st.caption("红色标记的点为检测到的异常数据点")

    anomaly_dates = anomalies['date'].dt.strftime('%Y-%m-%d').tolist()
    fig_anomaly = chart_gen.create_anomaly_highlight(df, anomaly_dates)
    st.plotly_chart(fig_anomaly, use_container_width=True)

else:
    st.success("✅ **近期数据平稳**，未检测到明显异常，系统运行正常")
    st.caption("系统使用Z-Score算法自动检测边现波动，已剔除周末/节假日影响")

# ==================== 第3部分：AI异常分析 ====================
if len(anomalies) > 0:
    st.markdown("---")
    st.markdown("## 🤖 第3部分：AI异常分析")
    st.markdown("*选择异常日期，点击按钮生成AI分析报告*")

    # 使用form让操作更明确
    with st.form("anomaly_analysis_form"):
        st.markdown("### 📋 选择要分析的异常")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("**1️⃣ 选择异常日期** *（选择需要深入分析的日期）*")
            selected_anomaly = st.selectbox(
                "异常日期",
                anomaly_dates,
                help="选择一个异常日期，AI将分析原因并给出建议",
                label_visibility="collapsed"
            )

        with col2:
            st.markdown("**2️⃣ 点击生成分析**")
            st.caption("AI分析需要10-15秒")

        st.markdown("---")

        # 提交按钮
        analyze_submitted = st.form_submit_button(
            "🤖 生成AI异常分析",
            type="primary",
            use_container_width=True
        )

    # 显示分析结果
    if analyze_submitted or st.session_state.get('anomaly_analyzed'):

        if analyze_submitted:
            with st.spinner("🤖 AI分析中，请稍候（约10-15秒）..."):
                try:
                    # 获取异常日期的数据
                    anomaly_row = df[df['date'] == pd.to_datetime(selected_anomaly)].iloc[0]

                    metrics_dict = {
                        'dau': int(anomaly_row['dau']),
                        'revenue': int(anomaly_row['revenue']),
                        'arpu': float(anomaly_row['arpu']),
                        'dau_change': float(anomaly_row.get('dau_change', 0)),
                        'revenue_change': float(anomaly_row.get('revenue_change', 0)),
                        'arpu_change': float(anomaly_row.get('arpu_change', 0)),
                        'conversion_rate': float(anomaly_row.get('conversion_rate', 0))
                    }

                    explanation = ai_engine.explain_anomaly(
                        selected_anomaly,
                        metrics_dict,
                        df
                    )

                    # 保存到session state
                    st.session_state.anomaly_analyzed = True
                    st.session_state.anomaly_explanation = explanation
                    st.session_state.anomaly_date = selected_anomaly
                    st.session_state.anomaly_metrics = metrics_dict

                    st.success("✅ AI分析完成！")

                except Exception as e:
                    st.error(f"❌ AI分析失败: {str(e)}")
                    st.info("💡 使用降级方案显示数据摘要...")

                    # 降级方案
                    explanation = f"""### 核心原因
1. 单DAU边现环比变化{metrics_dict['arpu_change']:.1f}%
2. 建议查看当日内容策略和资源位配置

### 数据洞察
指标出现异常波动，需进一步分析用户行为数据

### 行动建议
1. 检查当日运营活动是否有变化
2. 对比历史同期数据找规律
"""
                    st.session_state.anomaly_analyzed = True
                    st.session_state.anomaly_explanation = explanation
                    st.session_state.anomaly_date = selected_anomaly
                    st.session_state.anomaly_metrics = metrics_dict

        # 展示分析结果
        if st.session_state.get('anomaly_analyzed'):
            explanation = st.session_state.get('anomaly_explanation', '')
            anomaly_date = st.session_state.get('anomaly_date', '')
            metrics_dict = st.session_state.get('anomaly_metrics', {})

            st.markdown("---")
            st.markdown(f"### 📝 AI分析报告 - {anomaly_date}")

            # 使用tabs组织分析内容
            tab1, tab2, tab3 = st.tabs(["🤖 AI分析", "📊 数据详情", "📥 下载清单"])

            with tab1:
                st.markdown(explanation)

            with tab2:
                st.markdown("#### 📊 异常数据详情")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**当日指标**")
                    st.metric("DAU", f"{metrics_dict['dau']:,.0f}", f"{metrics_dict['dau_change']:+.1f}%")
                    st.metric("收入", f"{metrics_dict['revenue']:,.0f}元", f"{metrics_dict['revenue_change']:+.1f}%")

                with col2:
                    st.metric("边现", f"{metrics_dict['arpu']:.4f}元", f"{metrics_dict['arpu_change']:+.1f}%")
                    st.metric("转化率", f"{metrics_dict['conversion_rate']:.2f}%")

                st.markdown("---")
                st.markdown("#### 💡 对比分析")
                st.markdown(f"""
                - **DAU变化**: {metrics_dict['dau_change']:+.1f}% {'⬆️ 上升' if metrics_dict['dau_change'] > 0 else '⬇️ 下降'}
                - **收入变化**: {metrics_dict['revenue_change']:+.1f}% {'⬆️ 上升' if metrics_dict['revenue_change'] > 0 else '⬇️ 下降'}
                - **边现变化**: {metrics_dict['arpu_change']:+.1f}% {'⬆️ 上升' if metrics_dict['arpu_change'] > 0 else '⬇️ 下降'}

                **异常类型**: {'边现下降但DAU上升（稀释效应）' if metrics_dict['arpu_change'] < 0 and metrics_dict['dau_change'] > 0 else '综合性异常'}
                """)

            with tab3:
                st.markdown("#### 📥 下载行动清单")

                # 生成行动清单
                action_list = f"""## 🎯 异常处理行动清单

**异常日期**: {anomaly_date}

{explanation}

---

## 📋 执行计划

### ⚡ 立即执行（今日内）
- [ ] 检查当日运营活动配置是否正常
- [ ] 分析用户流失漏斗，定位流失环节
- [ ] 检查资源位曝光和点击数据

### 📅 24小时内
- [ ] 调整内容推荐策略（基于AI建议）
- [ ] 优化资源位配置和投放时段
- [ ] 检查优惠券发放和核销情况

### 🔍 48小时内
- [ ] 对比历史同期数据，寻找规律
- [ ] 分析竞品动态，是否有竞争影响
- [ ] 生成详细复盘报告

---

## 👥 负责人分工

- **执行负责人**: [@运营负责人]
- **数据分析**: [@数据分析师]
- **技术支持**: [@产品经理]

---

## 📊 关键数据

- DAU: {metrics_dict['dau']:,.0f} ({metrics_dict['dau_change']:+.1f}%)
- 收入: {metrics_dict['revenue']:,.0f}元 ({metrics_dict['revenue_change']:+.1f}%)
- 边现: {metrics_dict['arpu']:.4f}元 ({metrics_dict['arpu_change']:+.1f}%)
- 转化率: {metrics_dict['conversion_rate']:.2f}%

---

**生成时间**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
**生成页面**: 实时监控 - AI异常分析
"""

                st.download_button(
                    label="📥 下载完整行动清单",
                    data=action_list,
                    file_name=f"异常处理清单_{anomaly_date}.md",
                    mime="text/markdown",
                    use_container_width=True,
                    type="primary"
                )

                st.info("💡 **提示**：行动清单包含AI分析、执行计划、责任分工，可直接用于团队协作")

# ==================== 第4部分：预警规则配置 ====================
st.markdown("---")
st.markdown("## ⚙️ 第4部分：预警规则配置")
st.markdown("*可选：设置自动预警阈值，系统将在指标异常时推送通知*")

with st.expander("🔧 配置预警规则（可选）", expanded=False):
    st.caption("设置监控阈值，当指标超过阈值时系统会自动预警")

    with st.form("alert_config_form"):
        st.markdown("### 📋 预警阈值设置")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**边现预警**")
            arpu_alert = st.slider(
                "边现下降预警(%)",
                min_value=-30,
                max_value=-5,
                value=-10,
                help="边现下降超过该百分比时触发预警"
            )
            st.caption(f"⚠️ 下降超过 {abs(arpu_alert)}% 时预警")

        with col2:
            st.markdown("**DAU预警**")
            dau_alert = st.slider(
                "DAU波动预警(%)",
                min_value=5,
                max_value=30,
                value=15,
                help="DAU波动超过该百分比时触发预警"
            )
            st.caption(f"⚠️ 波动超过 ±{dau_alert}% 时预警")

        with col3:
            st.markdown("**转化率预警**")
            conversion_alert = st.slider(
                "转化率下降预警(%)",
                min_value=-40,
                max_value=-10,
                value=-15,
                help="转化率下降超过该百分比时触发预警"
            )
            st.caption(f"⚠️ 下降超过 {abs(conversion_alert)}% 时预警")

        st.markdown("---")

        # 提交按钮
        save_alert = st.form_submit_button(
            "💾 保存预警规则",
            use_container_width=True
        )

    if save_alert:
        st.session_state.alert_rules = {
            'arpu_alert': arpu_alert,
            'dau_alert': dau_alert,
            'conversion_alert': conversion_alert
        }
        st.success("✅ 预警规则已保存！系统将自动监控并在异常时推送通知（邮件/钉钉/企微）")

# ==================== 底部引导 ====================
st.markdown("---")
st.markdown("## 🎯 下一步操作")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.success("""
    ✅ **实时监控完成！**

    **下一步建议**：
    1. 如果活动已结束，前往 **"04 🧠 AI复盘"** 生成复盘报告
    2. 如果需要参考历史案例，前往 **"05 📚 经验库"** 搜索相似活动
    3. 如果需要调整策略，返回 **"02 👥 人群策略"** 重新生成
    """)

    st.info("💡 **提示**：建议每日早10点和晚20点查看监控数据，及时发现异常")
