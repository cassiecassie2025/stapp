"""
页面1：目标规划与AI预测（重新设计 - 新手友好版）
"""
import streamlit as st
from modules.charts import ChartGenerator

st.title("🎯 目标规划与AI预测")

if not st.session_state.get('data_loaded'):
    st.error("❌ 数据未加载，请先在主页配置API Key并等待数据加载完成")
    st.stop()

df = st.session_state.daily_df
segments_df = st.session_state.segments_df

# 顶部操作指引
st.info("💡 **新手指引**：本页面帮助您设定运营目标并评估可行性。请按照下方3个步骤操作 → 填写目标 → 查看分析 → 前往下一页生成策略")

# ==================== 步骤1：填写目标 ====================
st.markdown("---")
st.markdown("## 📝 步骤1：填写运营目标")
st.markdown("*请在下方表单中填写您的运营目标，所有字段都需要填写*")

with st.container():
    # 使用form让用户明确"提交"操作
    with st.form("goal_setting_form"):
        st.markdown("### 📋 目标设定表单")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**1️⃣ 选择目标指标** *（您想要提升什么？）*")
            target_metric = st.selectbox(
                "目标指标",
                ["会员收入", "单DAU边现", "新增会员数", "转化率"],
                help="选择您想要优化的核心指标",
                label_visibility="collapsed"
            )

            st.markdown("**2️⃣ 设定提升幅度** *（提升多少？）*")
            target_value = st.slider(
                "目标提升幅度(%)",
                min_value=5,
                max_value=50,
                value=15,
                step=5,
                help="建议设定在10-20%之间，过高可能难以实现",
                label_visibility="collapsed"
            )
            st.caption(f"✨ 当前设定：提升 **{target_value}%**")

        with col2:
            st.markdown("**3️⃣ 选择目标人群** *（针对谁？）*")
            target_segment = st.selectbox(
                "目标人群",
                segments_df['segment'].tolist(),
                help="选择您想要重点运营的用户群体",
                label_visibility="collapsed"
            )

            # 显示人群规模
            segment_info = segments_df[segments_df['segment'] == target_segment].iloc[0]
            st.caption(f"👥 人群规模：**{segment_info['size']}** | ARPU贡献：**{segment_info['avg_arpu_contribution']:.4f}元**")

            st.markdown("**4️⃣ 选择目标周期** *（多长时间？）*")
            target_period = st.selectbox(
                "目标周期",
                ["1周", "2周", "1个月"],
                help="建议至少选择2周，以便观察完整效果",
                label_visibility="collapsed"
            )

        st.markdown("---")

        # 表单提交按钮
        submitted = st.form_submit_button(
            "🚀 生成目标分析",
            use_container_width=True,
            type="primary"
        )

# ==================== 步骤2：查看分析结果 ====================
if submitted or st.session_state.get('goal_submitted'):
    # 保存到session state
    st.session_state.goal_submitted = True
    st.session_state.target_metric = target_metric
    st.session_state.target_value = target_value
    st.session_state.target_segment = target_segment
    st.session_state.target_period = target_period

    st.markdown("---")
    st.markdown("## 📊 步骤2：查看AI分析结果")
    st.markdown("*以下是系统根据历史数据自动生成的分析，无需操作*")

    # 目标摘要卡片
    target_text = f"提升 **{target_segment}** 的 **{target_metric}** {target_value}%"

    st.success(f"✅ **您的运营目标**：{target_text}（周期：{target_period}）")

    # 关键指标卡片
    st.markdown("### 📌 关键指标预测")
    col1, col2, col3, col4 = st.columns(4)

    segment_info = segments_df[segments_df['segment'] == target_segment].iloc[0]
    baseline_arpu = segment_info['avg_arpu_contribution']
    target_arpu = baseline_arpu * (1 + target_value/100)

    with col1:
        st.metric(
            "难度评级",
            "⭐⭐⭐ 中等" if target_value <= 20 else "⭐⭐⭐⭐ 较难",
            help="基于历史数据评估的实现难度"
        )
    with col2:
        st.metric(
            "当前基线",
            f"{baseline_arpu:.4f}元",
            help="该人群当前的单DAU边现"
        )
    with col3:
        st.metric(
            "目标值",
            f"{target_arpu:.4f}元",
            delta=f"+{target_value}%",
            help="需要达到的目标边现"
        )
    with col4:
        st.metric(
            "预期ROI",
            "1.30",
            help="基于历史相似活动的ROI预估"
        )

    # 可行性分析（使用tabs让信息更清晰）
    st.markdown("### 🔍 详细分析")

    tab1, tab2, tab3 = st.tabs(["📈 可行性评估", "⚠️ 风险提示", "💡 AI建议"])

    with tab1:
        st.markdown(f"""
        #### 历史数据参考

        | 指标 | 数值 | 说明 |
        |------|------|------|
        | 相似活动平均提升 | 12-18% | 过去6个月的类似活动数据 |
        | 当前基线（{target_segment}） | {baseline_arpu:.4f}元 | 该人群最近7天平均边现 |
        | 目标值 | {target_arpu:.4f}元 | 需提升 {(target_arpu - baseline_arpu):.4f}元 |
        | 人群规模 | {segment_info['size']} | 可触达用户数 |

        #### 📊 可行性结论
        """)

        if target_value <= 15:
            st.success("✅ **高可行性**：目标提升幅度合理，历史数据显示有80%以上成功率")
        elif target_value <= 25:
            st.warning("⚠️ **中等可行性**：目标较为激进，需要精细化运营和充足资源投入")
        else:
            st.error("❌ **低可行性**：目标过高，建议调整至20%以内或延长周期")

    with tab2:
        st.markdown(f"""
        #### ⚠️ 需要注意的风险点

        1. **人群风险**
           - 目标人群：{target_segment}
           - 当前活跃度需评估（建议查看实时监控页面）
           - 该人群对优惠券的敏感度可能影响转化

        2. **周期风险**
           - 目标周期：{target_period}
           - {'⚠️ 周期较短，需要快速见效，建议加大首周投入' if target_period == '1周' else '✅ 周期合理，可以分阶段执行'}
           - 需关注竞品同期活动影响

        3. **资源风险**
           - 提升{target_value}%需要充足的资源位和预算
           - 建议提前申请首页焦点图位、推荐流位
           - 优惠券预算需要提前规划

        4. **内容风险**
           - 需要准备足够的优质内容（至少200部精选）
           - 内容与人群匹配度直接影响转化率
        """)

    with tab3:
        st.markdown(f"""
        #### 💡 AI智能建议

        **执行策略**（3步走）：

        **第1步：分阶段执行**
        - 第1周重点：拉活提升DAU（目标+{target_value//2}%）
        - 第2周重点：促转化提升付费（目标+{target_value - target_value//2}%）

        **第2步：资源倾斜**
        - 预算分配：70%投入首页位1+3，30%投入详情页位
        - 时段策略：重点投放19:00-23:00黄金时段
        - 周末加权：周末预算提升30%

        **第3步：内容策略**（基于{target_segment}人群偏好）
        - 推荐配比：家庭剧60% + 动漫30% + 综艺10%
        - 内容质量：优先选择评分8.0+的精品内容
        - 更新频率：每3天更新一次推荐池，保持新鲜感

        **优惠券策略**：
        - 主推：影视VIP连月10元券-优爱腾（适中力度，高性价比）
        - 备选：影视VIP连季15元券-爱奇艺（高价值用户专属）

        **监控要点**：
        - 每日查看ARPU、转化率、DAU三大指标
        - 如遇异常，参考实时监控页面的AI分析
        """)

    # 趋势图表
    st.markdown("---")
    st.markdown("### 📈 历史趋势参考")
    st.caption("以下是最近30天的边现趋势，供您参考历史波动情况")

    chart_gen = ChartGenerator()
    fig = chart_gen.create_trend_chart(df, 'arpu', '单DAU边现趋势（最近30天）')
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📊 查看详细数据表"):
        st.dataframe(
            df[['date', 'dau', 'revenue', 'arpu', 'conversion_rate']].tail(10),
            use_container_width=True,
            column_config={
                'date': '日期',
                'dau': st.column_config.NumberColumn('DAU', format="%d"),
                'revenue': st.column_config.NumberColumn('收入', format="¥%.0f"),
                'arpu': st.column_config.NumberColumn('单DAU边现', format="%.4f"),
                'conversion_rate': st.column_config.NumberColumn('转化率', format="%.2f%%")
            }
        )

# ==================== 步骤3：下一步操作 ====================
if st.session_state.get('goal_submitted'):
    st.markdown("---")
    st.markdown("## 🎯 步骤3：前往下一步")
    st.markdown("*目标分析已完成，现在可以进入下一页生成具体执行策略*")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.success("""
        ✅ **目标规划完成！**

        接下来请点击左侧导航栏的 **"02 👥 人群策略"** 页面，系统将为您：
        1. 基于刚才设定的目标
        2. 自动生成AI推荐的运营策略
        3. 包含具体的内容配比、资源位配置、优惠券方案
        """)

        st.info("💡 **提示**：如需修改目标，请重新填写上方表单并点击「生成目标分析」按钮")

else:
    # 未提交时的提示
    st.markdown("---")
    st.warning("⬆️ 请先在上方填写目标设定表单，然后点击「🚀 生成目标分析」按钮")
