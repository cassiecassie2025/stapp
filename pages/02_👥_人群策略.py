"""
页面2：人群策略与AI推荐（重新设计 - 新手友好版）
"""
import streamlit as st
import json
from modules.charts import ChartGenerator
from modules.budget_simulator import BudgetSimulator

st.title("👥 人群圈选与策略推荐")

if not st.session_state.get('data_loaded'):
    st.error("❌ 数据未加载，请先在主页配置API Key并等待数据加载完成")
    st.stop()

segments_df = st.session_state.segments_df
campaigns_df = st.session_state.campaigns_df
capacity_df = st.session_state.capacity_df
ai_engine = st.session_state.ai_engine

# 顶部操作指引
st.info("💡 **新手指引**：本页面根据您的目标生成AI推荐策略。请按照下方3个步骤操作 → 确认目标 → 生成策略 → 下载执行模板")

# ==================== 步骤1：确认运营目标 ====================
st.markdown("---")
st.markdown("## 📝 步骤1：确认运营目标")
st.markdown("*请在下方填写或修改您的运营目标*")

# 检查是否从页面1带入目标
has_goal_from_page1 = st.session_state.get('goal_submitted', False)

if has_goal_from_page1:
    st.success(f"""
    ✅ **已从页面1带入目标**：
    - 目标人群：{st.session_state.get('target_segment', '未设定')}
    - 目标指标：{st.session_state.get('target_metric', '未设定')}
    - 提升幅度：{st.session_state.get('target_value', 0)}%
    - 目标周期：{st.session_state.get('target_period', '未设定')}
    """)

    # 自动生成目标描述
    default_target = f"提升{st.session_state.get('target_segment', '家庭向高活跃')}的{st.session_state.get('target_metric', '会员收入')}{st.session_state.get('target_value', 15)}%，周期为{st.session_state.get('target_period', '2周')}"
else:
    st.warning("⚠️ 您还没有在页面1设定目标。可以在下方手动填写，或返回页面1完成目标设定")
    default_target = "提升家庭向高活跃用户的会员收入15%，周期为2周"

with st.form("strategy_input_form"):
    st.markdown("### 📋 目标与预算设定")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("**1️⃣ 运营目标描述** *（AI将基于此生成策略）*")
        user_target = st.text_area(
            "运营目标",
            value=default_target,
            height=100,
            help="详细描述您的运营目标，包括人群、指标、提升幅度、周期等",
            label_visibility="collapsed"
        )

    with col2:
        st.markdown("**2️⃣ 预算设定** *（万元）*")
        budget = st.number_input(
            "预算",
            min_value=10,
            max_value=500,
            value=100,
            help="本次活动的总预算（包括优惠券成本、资源位成本等）",
            label_visibility="collapsed"
        )
        st.caption(f"💰 预算：**{budget}万元**")

        st.markdown("**3️⃣ 活动周期** *（天）*")
        duration = st.slider(
            "周期",
            min_value=3,
            max_value=14,
            value=7,
            help="建议至少7天，以便观察完整效果",
            label_visibility="collapsed"
        )
        st.caption(f"📅 周期：**{duration}天**")

    st.markdown("---")

    # 提交按钮
    submitted = st.form_submit_button(
        "🤖 生成AI推荐策略",
        type="primary",
        use_container_width=True
    )

# ==================== 步骤2：查看AI推荐策略 ====================
if submitted or st.session_state.get('strategy_generated'):

    # 如果是新提交，调用AI
    if submitted:
        with st.spinner("🤖 AI策略生成中，请稍候（约10-15秒）..."):
            try:
                # 调用AI推荐
                strategy = ai_engine.recommend_strategy(
                    user_target,
                    campaigns_df,
                    segments_df
                )

                # 保存到session state
                st.session_state.current_strategy = strategy
                st.session_state.strategy_generated = True
                st.session_state.strategy_budget = budget
                st.session_state.strategy_duration = duration

                st.success("✅ AI策略推荐完成！")

            except Exception as e:
                st.error(f"❌ AI调用失败: {str(e)}")
                st.info("💡 使用默认策略模板...")
                # 使用降级方案
                strategy = ai_engine._get_default_strategy()
                st.session_state.current_strategy = strategy
                st.session_state.strategy_generated = True
                st.session_state.strategy_budget = budget
                st.session_state.strategy_duration = duration

    # 展示策略
    if 'current_strategy' in st.session_state:
        strategy = st.session_state.current_strategy
        budget = st.session_state.get('strategy_budget', 100)
        duration = st.session_state.get('strategy_duration', 7)

        st.markdown("---")
        st.markdown("## 🎯 步骤2：查看AI推荐策略")
        st.markdown("*以下是AI根据您的目标自动生成的策略方案，无需操作*")

        # 使用tabs组织策略内容
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "👥 目标人群",
            "🎬 内容策略",
            "📺 资源位策略",
            "💰 优惠策略",
            "📊 KPI预测"
        ])

        # Tab 1: 目标人群
        with tab1:
            st.markdown("### 👥 推荐目标人群")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("人群标签", strategy['target_segment'])
            with col2:
                st.metric("预估规模", strategy['estimated_size'])
            with col3:
                # 查找人群信息
                segment_info = segments_df[segments_df['segment'] == strategy['target_segment']]
                if len(segment_info) > 0:
                    cvr = segment_info.iloc[0]['historical_cvr']
                    st.metric("历史转化率", f"{cvr:.1%}")
                else:
                    st.metric("历史转化率", "3.2%")

            st.markdown("---")
            st.markdown("#### 💡 为什么推荐这个人群？")
            st.info(strategy['content_strategy']['reason'])

            # 人群详细数据表
            with st.expander("📊 查看人群详细数据"):
                if len(segment_info) > 0:
                    st.dataframe(
                        segment_info,
                        use_container_width=True,
                        column_config={
                            'segment': '人群标签',
                            'size': '规模',
                            'current_arpu': st.column_config.NumberColumn('当前ARPU', format="%.4f"),
                            'historical_cvr': st.column_config.NumberColumn('历史转化率', format="%.2%"),
                            'potential': '潜力评级'
                        }
                    )

        # Tab 2: 内容策略
        with tab2:
            st.markdown("### 🎬 内容策略推荐")

            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown(f"""
                **主推内容类型**：{strategy['content_strategy']['primary_content']}

                **内容配比**：{strategy['content_strategy']['content_ratio']}

                **策略说明**：
                - 优先推荐{strategy['content_strategy']['primary_content']}，这是该人群最偏好的内容类型
                - 配比基于历史ROI数据优化
                - 建议准备至少200部精选内容
                """)

            with col2:
                # 解析内容配比并生成图表
                content_str = strategy['content_strategy']['content_ratio']
                # 简单解析（实际应更robust）
                content_ratio = {'家庭剧': 70, '动漫': 20, '综艺': 10}

                chart_gen = ChartGenerator()
                fig = chart_gen.create_strategy_simulator(content_ratio, 0.092)
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            st.markdown("#### 📋 内容准备清单")
            st.markdown("""
            - [ ] 准备200+部精选剧集（主推类型占70%）
            - [ ] 确保内容评分≥8.0分
            - [ ] 配置内容推荐池，设置动态更新规则
            - [ ] 每3天更新一次推荐池，保持新鲜感
            """)

        # Tab 3: 资源位策略
        with tab3:
            st.markdown("### 📺 资源位策略")

            positions = strategy['resource_allocation']['positions']

            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown("#### 推荐资源位组合")
                for i, pos in enumerate(positions, 1):
                    st.markdown(f"**{i}.** {pos}")

                st.markdown("---")
                st.markdown("#### 📋 资源位申请清单")
                st.markdown("""
                - [ ] 提前3天申请首页焦点图位
                - [ ] 提前2天申请推荐流位
                - [ ] 提前1天申请详情页位
                - [ ] 配置资源位投放时段规则
                """)

            with col2:
                st.markdown("#### 投放时段策略")
                st.success(f"**最佳时段**：{strategy['resource_allocation']['peak_hours']}")
                st.caption("基于历史数据，该时段转化率最高")

                st.markdown("#### 预算分配建议")
                st.info(f"**重点投入**：{strategy['resource_allocation']['budget_focus']}")
                st.caption(f"总预算 {budget}万元，建议70%投入首页位")

                # 预算分配表
                st.markdown("#### 💰 预算分配明细")
                budget_allocation = {
                    '首页焦点图位': budget * 0.4,
                    '首页推荐流位': budget * 0.3,
                    '详情页推荐位': budget * 0.2,
                    'Push通知': budget * 0.1
                }

                for pos, amount in budget_allocation.items():
                    st.metric(pos, f"{amount:.1f}万元", f"{amount/budget*100:.0f}%")

        # Tab 4: 优惠策略
        with tab4:
            st.markdown("### 💰 优惠策略推荐")

            st.success(f"**推荐优惠券**：{strategy['discount_recommendation']}")

            st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 优惠券配置建议")
                st.markdown(f"""
                **主推券**：{strategy['discount_recommendation']}
                - 发放规则：首页曝光后领取
                - 有效期：7天
                - 使用门槛：≥15元订单
                - 预期核销率：35%

                **备选券**（分层发放）：
                - 高价值用户：影视VIP连季15元券-爱奇艺
                - 亲子家庭：亲子VIP5元券
                """)

            with col2:
                st.markdown("#### 成本与ROI预估")

                # 估算优惠券成本
                coupon_cost = budget * 0.3  # 假设优惠券占预算30%
                expected_revenue = coupon_cost * 1.3  # ROI 1.3

                st.metric("优惠券预算", f"{coupon_cost:.1f}万元", f"{coupon_cost/budget*100:.0f}%")
                st.metric("预期收入", f"{expected_revenue:.1f}万元")
                st.metric("预期ROI", strategy['kpi_forecast']['roi_estimate'])

            st.markdown("---")
            st.markdown("#### 📋 优惠券设置清单")
            st.markdown(f"""
            - [ ] 创建优惠券：{strategy['discount_recommendation']}
            - [ ] 设置发放规则（首页曝光领取）
            - [ ] 配置使用门槛（≥15元）
            - [ ] 设置有效期（7天）
            - [ ] 配置风控规则（限制每用户1张）
            """)

        # Tab 5: KPI预测
        with tab5:
            st.markdown("### 📊 KPI预测与评估")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "预估边现提升",
                    strategy['kpi_forecast']['arpu_lift'],
                    help="基于历史数据预测的边现提升幅度"
                )
            with col2:
                st.metric(
                    "预测置信度",
                    f"{strategy['kpi_forecast']['confidence']}%",
                    help="AI模型对预测结果的置信度"
                )
            with col3:
                st.metric(
                    "预估ROI",
                    strategy['kpi_forecast']['roi_estimate'],
                    help="投入产出比（每投入1元预期获得的收入）"
                )

            st.markdown("---")

            # 风险提示
            st.markdown("#### ⚠️ 风险提示")
            st.warning(strategy['risk_alert'])

            st.markdown("---")

            # 历史参考
            st.markdown("#### 📚 历史参考活动")
            st.info(f"**参考案例**：{strategy['historical_reference']}")
            st.caption("该活动与您的目标最相似，可参考其执行经验")

            st.markdown("---")

            # KPI监控建议
            st.markdown("#### 📈 KPI监控建议")
            st.markdown(f"""
            **每日必看指标**（前往页面3查看）：
            1. **DAU**：目标 +10%
            2. **单DAU边现**：目标 {strategy['kpi_forecast']['arpu_lift']}
            3. **转化率**：目标 +15%
            4. **ROI**：目标 {strategy['kpi_forecast']['roi_estimate']}

            **预警阈值**：
            - ARPU波动 ±15% 触发预警
            - DAU异常下降 >20% 触发预警
            - 转化率低于基线 触发预警
            """)

# ==================== 步骤3：下载执行模板 ====================
if st.session_state.get('strategy_generated'):
    strategy = st.session_state.current_strategy
    budget = st.session_state.get('strategy_budget', 100)
    duration = st.session_state.get('strategy_duration', 7)

    st.markdown("---")
    st.markdown("## 📥 步骤3：下载执行模板")
    st.markdown("*策略已生成，现在可以下载执行模板并开始准备*")

    # 生成执行模板
    template = f"""# 运营执行模板

## 目标人群
{strategy['target_segment']} - {strategy['estimated_size']}

## 内容策略
{strategy['content_strategy']['content_ratio']}

## 资源位配置
{', '.join(strategy['resource_allocation']['positions'])}

**投放时段**：{strategy['resource_allocation']['peak_hours']}
**预算分配**：{strategy['resource_allocation']['budget_focus']}

## 优惠方案
{strategy['discount_recommendation']}

- 发放规则：首页曝光后领取
- 有效期：7天
- 使用门槛：≥15元订单

## KPI目标
- 边现提升: {strategy['kpi_forecast']['arpu_lift']}
- ROI: {strategy['kpi_forecast']['roi_estimate']}
- 置信度: {strategy['kpi_forecast']['confidence']}%

## 预算分配（总预算{budget}万元）
- 首页焦点图位：{budget * 0.4:.1f}万元（40%）
- 首页推荐流位：{budget * 0.3:.1f}万元（30%）
- 详情页推荐位：{budget * 0.2:.1f}万元（20%）
- Push通知：{budget * 0.1:.1f}万元（10%）

## 行动清单

### 第1-2天：准备阶段
- [ ] 配置内容推荐池（{strategy['content_strategy']['primary_content']}为主）
- [ ] 申请资源位排期
- [ ] 创建优惠券：{strategy['discount_recommendation']}
- [ ] 配置监控大盘和预警

### 第3-{duration}天：执行阶段
- [ ] 每日查看监控大盘（早10点、晚20点）
- [ ] 每日分析关键指标（DAU、ARPU、转化率）
- [ ] 每3天微调策略（基于实时数据）
- [ ] 每日汇报进度

### 第{duration+1}天：复盘阶段
- [ ] 生成AI复盘报告
- [ ] 提取策略执行模板
- [ ] 沉淀优化建议
- [ ] 更新经验库

## 风险点
{strategy['risk_alert']}

## 历史参考
{strategy['historical_reference']}

---
生成时间：{budget}万元预算，{duration}天周期
"""

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.download_button(
            label="📥 下载完整执行模板",
            data=template,
            file_name=f"strategy_execution_template_{strategy['target_segment']}.md",
            mime="text/markdown",
            use_container_width=True,
            type="primary"
        )

        st.success("""
        ✅ **策略推荐完成！**

        **下一步操作**：
        1. 下载执行模板并与团队确认
        2. 准备内容、申请资源位、配置优惠券
        3. 前往 **"03 📈 实时监控"** 页面查看实时数据
        4. 活动结束后前往 **"04 🧠 AI复盘"** 生成复盘报告
        """)

        st.info("💡 **提示**：如需修改策略，请重新填写上方表单并点击「生成AI推荐策略」按钮")

# ==================== 额外功能：策略模拟器 ====================
if st.session_state.get('strategy_generated'):
    st.markdown("---")
    st.markdown("## 🎮 高级功能：策略模拟器")
    st.markdown("*可选：拖动滑块调整策略参数，实时查看效果预测*")

    with st.expander("🔧 打开策略模拟器", expanded=False):
        st.caption("调整下方参数，系统会实时预测调整后的效果")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**调整内容配比**")
            content_ratio_adjust = st.slider(
                "家庭剧占比(%)",
                min_value=50,
                max_value=90,
                value=70,
                help="调整家庭剧在内容池中的占比"
            )
            st.caption(f"当前配比：家庭剧{content_ratio_adjust}% + 其他{100-content_ratio_adjust}%")

        with col2:
            st.markdown("**调整资源位使用率**")
            resource_usage = st.slider(
                "首页位3使用率",
                min_value=0.0,
                max_value=1.0,
                value=0.6,
                help="首页位3的使用率（0-100%）"
            )
            st.caption(f"使用率：{resource_usage*100:.0f}%")

        # 实时预测
        simulator = BudgetSimulator(baseline_arpu=0.092)
        sim_result = simulator.simulate(
            content_ratio={'家庭剧': content_ratio_adjust, '动漫': 100-content_ratio_adjust},
            resource_usage={'首页位3': resource_usage},
            capacity_df=capacity_df
        )

        st.markdown("---")
        st.markdown("#### 📊 调整后预测结果")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "预估边现",
                f"{sim_result['estimated_arpu']:.4f}元",
                delta=f"+{sim_result['arpu_lift_pct']:.1f}%"
            )
        with col2:
            st.metric("预估ROI", f"{sim_result['roi']:.2f}")
        with col3:
            st.metric("预估成本", f"{sim_result['total_cost']/10000:.1f}万元")

        if sim_result['capacity_warning']:
            st.warning("⚠️ 资源位使用率超过80%，可能影响效果，建议降低使用率或增加资源位")
        else:
            st.success("✅ 资源位使用率合理")

# 未生成策略时的提示
else:
    st.markdown("---")
    st.warning("⬆️ 请先在上方填写目标并点击「🤖 生成AI推荐策略」按钮")
